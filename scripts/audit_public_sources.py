#!/usr/bin/env python3
"""Audit the CNIPA/PatentDatabases source catalog and run safe public queries.

This is an access-and-retrieval audit, not a claim search result set. It makes
one bounded read-only request to each catalog URL, then runs source-specific
public search URLs where the protocol is known and documented. Interactive,
login, CAPTCHA, subscription, or unknown form workflows are recorded as
manual rather than guessed or bypassed.
"""

import argparse
import csv
import html
import json
import re
import ssl
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import quote, urljoin, urlparse
from urllib.request import Request, urlopen


USER_AGENT = "medtech-patent-roadmap-source-audit/1.0 (read-only; contact not provided)"
def load_json(path, default=None):
    if not path.exists():
        return default if default is not None else {}
    return json.loads(path.read_text(encoding="utf-8"))


def normalize_url(url):
    url = str(url or "").strip()
    if not url or "NaN" in url:
        return ""
    parsed = urlparse(url)
    if parsed.scheme not in ("http", "https") or not parsed.netloc:
        return ""
    return url


def fetch(url, max_bytes=120000, timeout=10):
    if not url:
        return {"status": "invalid_url", "http_status": "", "final_url": "", "title": "", "content_type": "", "body": "", "error": "invalid URL"}
    request = Request(url, headers={"User-Agent": USER_AGENT, "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.6"})
    try:
        with urlopen(request, timeout=timeout, context=ssl.create_default_context()) as response:
            body = response.read(max_bytes).decode("utf-8", errors="replace")
            return {"status": "ok", "http_status": response.status, "final_url": response.geturl(), "title": extract_title(body), "content_type": response.headers.get("Content-Type", ""), "body": body, "error": ""}
    except HTTPError as exc:
        body = ""
        try:
            body = exc.read(max_bytes).decode("utf-8", errors="replace")
        except Exception:
            pass
        return {"status": "http_error", "http_status": exc.code, "final_url": getattr(exc, "url", url), "title": extract_title(body), "content_type": exc.headers.get("Content-Type", "") if exc.headers else "", "body": body, "error": str(exc.reason)}
    except (URLError, TimeoutError, ssl.SSLError, OSError) as exc:
        return {"status": "network_error", "http_status": "", "final_url": "", "title": "", "content_type": "", "body": "", "error": compact_error(exc)}


def compact_error(exc):
    text = str(exc).replace("\n", " ")
    return text[:260]


def extract_title(body):
    match = re.search(r"<title[^>]*>(.*?)</title>", body or "", flags=re.I | re.S)
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", "", match.group(1)))).strip()[:240] if match else ""


def is_public_http(result):
    return isinstance(result.get("http_status"), int) and 200 <= result["http_status"] < 400


def page_signal(result):
    body = (result.get("body") or "").lower()
    title = (result.get("title") or "").lower()
    login = any(x in body or x in title for x in ("sign in", "login", "log in", "subscription", "subscribe", "登录", "注册会员"))
    captcha = any(x in body for x in ("captcha", "recaptcha", "验证码"))
    search_form = bool(re.search(r"<(?:form|input|button)[^>]*(?:search|query|keyword|patent|检索|搜索)", body, flags=re.I))
    if captcha:
        return "captcha_or_bot_challenge"
    if login:
        return "login_or_subscription_signal"
    if search_form:
        return "public_page_with_search_controls"
    if body:
        return "public_page_no_search_signal"
    return "empty_response"


def unique_terms(values, limit=8):
    seen, result = set(), []
    for value in values:
        value = " ".join(str(value or "").split())
        if value and value.casefold() not in seen:
            seen.add(value.casefold())
            result.append(value)
        if len(result) >= limit:
            break
    return result


def case_query(project, override=""):
    if override:
        return override
    scope = load_json(project / "research_scope.json", {})
    identity = load_json(project / "identity.json", {})
    obj = scope.get("research_object", {})
    terms = unique_terms([
        obj.get("molecule"), identity.get("molecule", {}).get("canonical"),
        *obj.get("synonyms", []), *identity.get("molecule", {}).get("synonyms", []),
        obj.get("target"), identity.get("target", {}).get("canonical"),
        *identity.get("target", {}).get("aliases", []),
        obj.get("indication"), identity.get("indication", {}).get("canonical"),
    ])
    if not terms:
        raise ValueError("未找到检索词：请提供 --query，或补全 research_scope.json / identity.json。")
    return " OR ".join(f'"{term}"' for term in terms[:5])


def direct_search_url(source_id, query):
    q = quote(query, safe="")
    if source_id == "src-026":
        return "https://worldwide.espacenet.com/patent/search?q=" + q
    if source_id == "src-028":
        return "https://ppubs.uspto.gov/pubwebapp/external.html?q=" + q + "&db=USPAT%2CUS-PGPUB%2CUSOCR&type=quick"
    if source_id == "src-032":
        return "https://patentscope.wipo.int/search/en/result.jsf?query=" + quote(f"FP:({query})", safe="")
    if source_id == "src-045":
        return "https://patents.google.com/?q=" + q
    if source_id == "src-052":
        return "https://pubmed.ncbi.nlm.nih.gov/?term=" + q
    return ""


def search_signal(result, query):
    body = (result.get("body") or "").lower()
    if not body:
        return "no_body"
    signals = {
        "result_or_document_signal": ("result", "patent", "publication", "document", "检索结果", *[term.lower() for term in unique_terms([query])]),
        "search_form_signal": ("search", "query", "keyword", "检索", "搜索"),
        "login_or_subscription_signal": ("sign in", "login", "subscription", "验证码"),
    }
    for label, words in signals.items():
        if any(word in body for word in words):
            return label
    return "page_loaded_no_result_signal"


def classify(source, access):
    if not access["url"]:
        return "invalid_url"
    if not is_public_http(access):
        return "blocked_or_error"
    signal = page_signal(access)
    if signal == "captcha_or_bot_challenge":
        return "public_page_blocked_by_captcha"
    if signal == "login_or_subscription_signal" and source.get("source_kind") == "commercial_or_aggregator":
        return "landing_page_restricted_or_subscription"
    if source["source_id"] in {"src-026", "src-028", "src-032", "src-045", "src-052"}:
        return "public_searchable_known_endpoint"
    if signal == "public_page_with_search_controls":
        return "public_search_form_manual"
    return "public_page_manual_or_unknown_search"


def audit_one(source, query):
    original_url = normalize_url(source.get("url"))
    access = fetch(original_url)
    if access["status"] != "ok" and original_url.startswith("http://"):
        https_url = "https://" + original_url[len("http://"):]
        retry = fetch(https_url)
        if retry["status"] == "ok" or retry.get("http_status"):
            access = retry
    row = {
        "source_id": source.get("source_id"), "name": source.get("name"), "source_kind": source.get("source_kind"),
        "catalog_url": source.get("url"), "default_use": source.get("default_use"), "access_status": access.get("status"),
        "http_status": access.get("http_status"), "final_url": access.get("final_url"), "title": access.get("title"),
        "content_type": access.get("content_type"), "page_signal": page_signal(access), "access_class": classify(source, {**access, "url": original_url}),
        "landing_error": access.get("error", ""), "query": query, "search_attempt": "not_attempted", "search_url": "",
        "search_http_status": "", "search_final_url": "", "search_title": "", "search_signal": "", "search_error": "",
    }
    search_url = direct_search_url(source.get("source_id"), query)
    if search_url and is_public_http(access):
        search = fetch(search_url, max_bytes=180000, timeout=12)
        row.update({"search_attempt": "attempted", "search_url": search_url, "search_http_status": search.get("http_status"), "search_final_url": search.get("final_url"), "search_title": search.get("title"), "search_signal": search_signal(search, query), "search_error": search.get("error", "")})
    elif search_url:
        row["search_attempt"] = "not_attempted_landing_unavailable"
        row["search_url"] = search_url
    elif row["access_class"] in {"public_search_form_manual", "public_page_manual_or_unknown_search"}:
        row["search_attempt"] = "manual_interactive_or_endpoint_unknown"
    elif row["access_class"] in {"landing_page_restricted_or_subscription", "public_page_blocked_by_captcha", "blocked_or_error", "invalid_url"}:
        row["search_attempt"] = "not_attempted_restricted_or_unavailable"
    return row


def write_csv(path, rows):
    fields = [
        "source_id", "name", "source_kind", "catalog_url", "default_use", "access_status", "http_status", "final_url", "title", "content_type", "page_signal", "access_class", "landing_error", "query", "search_attempt", "search_url", "search_http_status", "search_final_url", "search_title", "search_signal", "search_error",
    ]
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows({field: row.get(field, "") for field in fields} for row in rows)


def build_report(rows, generated, query):
    counter = {}
    for row in rows:
        counter[row["access_class"]] = counter.get(row["access_class"], 0) + 1
    searched = [row for row in rows if row["search_attempt"] == "attempted"]
    public = [row for row in rows if row["access_class"].startswith("public_") or row["access_class"] == "public_searchable_known_endpoint"]
    lines = [
        "# 公开来源访问与检索审计报告", "", f"> 生成时间：{generated} · 目录来源：CNIPA/PatentDatabases · 统一检索式：`{query}`", "",
        "## 结论摘要", "", f"本轮对来源目录中的 **{len(rows)} 个去重 URL** 各执行一次只读访问检查；其中 **{len(public)} 个**返回可公开页面信号，**{len(searched)} 个**使用已知公开检索端点实际执行了查询。公开页面不等于开放全文、开放 API 或可直接用于法律状态核验。", "",
        "## 分层统计", "", "| 访问/检索层级 | 数量 | 含义 |", "|---|---:|---|",
        f"| 公开可检索（已知端点） | {counter.get('public_searchable_known_endpoint', 0)} | 已执行统一查询并记录搜索页响应 |",
        f"| 公开页面但需人工检索 | {counter.get('public_search_form_manual', 0) + counter.get('public_page_manual_or_unknown_search', 0)} | 页面可访问，但查询参数/表单流程未建立自动适配 |",
        f"| 受限、验证码或订阅 | {counter.get('landing_page_restricted_or_subscription', 0) + counter.get('public_page_blocked_by_captcha', 0)} | 未绕过登录、验证码或订阅 |",
        f"| 阻断、错误或 URL 失效 | {counter.get('blocked_or_error', 0) + counter.get('invalid_url', 0)} | 需人工复核或更新来源目录 |",
        "", "## 已实际执行的公开检索", "",
        "| 来源 | 检索入口 | 搜索响应 | 说明 |", "|---|---|---|---|",
    ]
    for row in searched:
        lines.append(f"| {row['source_id']} {row['name']} | [{row['search_url']}]({row['search_url']}) | HTTP {row.get('search_http_status') or '—'}；{row.get('search_signal') or '—'} | 需要回到结果页逐条去重、抽取 claim 和族成员 |")
    lines += ["", "## 公开来源清单", "", "以下清单按返回公开页面信号筛出；‘公开可检索’只对已建立端点的来源成立，其他来源需人工打开检索表单。", "", "| 来源 | 来源角色 | 访问分类 | 入口 | 页面标题 | 检索状态 |", "|---|---|---|---|---|---|"]
    for row in public:
        lines.append(f"| {row['source_id']} {row['name']} | {row['source_kind']} | {row['access_class']} | [{row['final_url'] or row['catalog_url']}]({row['final_url'] or row['catalog_url']}) | {row['title'] or '—'} | {row['search_attempt']} |")
    lines += ["", "## 未能自动检索的原因", "", "- 国家/地区专利局页面多数是公开入口，但搜索需要 JavaScript、会话、验证码、语言选择或 POST 表单；本轮不猜测参数，也不绕过访问控制。", "- 商业数据库的落地页可能公开，但全文、批量检索、导出或法律状态通常需要登录/订阅；这类来源只作为发现/交叉核验入口。", "- `search_attempt=manual_interactive_or_endpoint_unknown` 不表示没有结果，只表示当前脚本没有把人工表单当成已完成的自动检索。", "- 正式 FTO 仍应以目标法域官方登记簿、官方专利文本和审查档案为准。", "", "## 机器可读结果", "", "- `public-source-search-audit.csv`：逐来源访问与检索字段。", "- `public-source-search-audit.json`：包含统计、查询式和每个来源的完整记录。"]
    return "\n".join(lines) + "\n", counter, len(public), len(searched)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-dir", required=True)
    parser.add_argument("--query", default="", help="Optional query override; otherwise derive terms from the case scope")
    args = parser.parse_args()
    project = Path(args.project_dir).expanduser().resolve()
    query = case_query(project, args.query)
    plan = load_json(project / "fto-search-plan.json")
    sources = plan.get("source_catalog", {}).get("sources", [])
    generated = datetime.now(timezone.utc).isoformat()
    rows = []
    with ThreadPoolExecutor(max_workers=8) as pool:
        futures = [pool.submit(audit_one, source, query) for source in sources]
        for future in as_completed(futures):
            try:
                rows.append(future.result())
            except Exception as exc:  # keep a single broken source from dropping the audit
                rows.append({
                    "source_id": "UNHANDLED", "name": "unhandled source audit exception", "source_kind": "", "catalog_url": "",
                    "default_use": "", "access_status": "exception", "http_status": "", "final_url": "", "title": "", "content_type": "",
                    "page_signal": "", "access_class": "blocked_or_error", "landing_error": compact_error(exc), "query": query,
                    "search_attempt": "not_attempted_exception", "search_url": "", "search_http_status": "", "search_final_url": "",
                    "search_title": "", "search_signal": "", "search_error": "",
                })
            if len(rows) % 25 == 0:
                print(f"Audited {len(rows)}/{len(sources)} sources", flush=True)
    rows.sort(key=lambda row: row.get("source_id", ""))
    csv_path = project / "public-source-search-audit.csv"
    json_path = project / "public-source-search-audit.json"
    md_path = project / "public-source-search-report.md"
    write_csv(csv_path, rows)
    report, counts, public_count, searched_count = build_report(rows, generated, query)
    md_path.write_text(report, encoding="utf-8")
    json_path.write_text(json.dumps({"schema_version": "1.0", "generated_at": generated, "query": query, "source_count": len(rows), "public_page_count": public_count, "direct_search_count": searched_count, "counts_by_access_class": counts, "records": rows}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"source_count": len(rows), "public_page_count": public_count, "direct_search_count": searched_count, "counts_by_access_class": counts, "csv": str(csv_path), "report": str(md_path)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
