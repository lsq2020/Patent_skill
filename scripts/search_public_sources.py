#!/usr/bin/env python3
"""Run the public patent/literature source searches declared for a case.

The source catalog contains many landing pages, commercial products and
interactive portals.  This runner deliberately separates:

* ``executed``: a read-only GET/POST search request was actually submitted;
* ``browser_manual``: a public search page exists, but its query is submitted
  by JavaScript, a browser session, CAPTCHA, or a stateful form;
* ``not_mapped``: the catalog page is public, but no reliable patent-search
  endpoint has yet been identified.

It never guesses hidden API parameters and never bypasses login, CAPTCHA or
subscription controls.  The output is an execution ledger, not a patent
result set or a legal-status opinion.
"""

import argparse
import csv
import hashlib
import html
import json
import re
import ssl
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode, urlparse
from urllib.request import Request, urlopen


USER_AGENT = "medtech-patent-roadmap-public-search/1.0 (read-only)"
DEFAULT_QUERY = "durvalumab"
DEFAULT_QUERY_VARIANTS = ["durvalumab", "MEDI4736", "Imfinzi", "PD-L1"]


def load_json(path, default=None):
    if not path.exists():
        return default if default is not None else {}
    return json.loads(path.read_text(encoding="utf-8"))


def compact_error(exc):
    return str(exc).replace("\n", " ")[:300]


def extract_title(body):
    match = re.search(r"<title[^>]*>(.*?)</title>", body or "", flags=re.I | re.S)
    if not match:
        return ""
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", "", match.group(1)))).strip()[:240]


def fetch(url, method="GET", params=None, max_bytes=180000, timeout=18):
    data = None
    headers = {
        "User-Agent": USER_AGENT,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.5",
    }
    if method.upper() == "POST":
        data = urlencode(params or {}).encode("utf-8")
        headers["Content-Type"] = "application/x-www-form-urlencoded"
    request = Request(url, data=data, method=method.upper(), headers=headers)
    try:
        with urlopen(request, timeout=timeout, context=ssl.create_default_context()) as response:
            body = response.read(max_bytes).decode("utf-8", errors="replace")
            return {
                "transport_status": "ok",
                "http_status": response.status,
                "final_url": response.geturl(),
                "content_type": response.headers.get("Content-Type", ""),
                "body": body,
                "error": "",
            }
    except HTTPError as exc:
        body = ""
        try:
            body = exc.read(max_bytes).decode("utf-8", errors="replace")
        except Exception:
            pass
        return {
            "transport_status": "http_error",
            "http_status": exc.code,
            "final_url": getattr(exc, "url", url),
            "content_type": exc.headers.get("Content-Type", "") if exc.headers else "",
            "body": body,
            "error": str(exc.reason)[:300],
        }
    except (URLError, TimeoutError, ssl.SSLError, OSError) as exc:
        return {
            "transport_status": "network_error",
            "http_status": "",
            "final_url": "",
            "content_type": "",
            "body": "",
            "error": compact_error(exc),
        }


def interpolate(value, query):
    if isinstance(value, str):
        return value.replace("{query}", query)
    if isinstance(value, dict):
        return {key: interpolate(item, query) for key, item in value.items()}
    if isinstance(value, list):
        return [interpolate(item, query) for item in value]
    return value


def query_url(portal, query):
    template = portal.get("url_template") or portal.get("search_url") or portal.get("portal_url") or ""
    return interpolate(template, query)


def is_public(status):
    return isinstance(status, int) and 200 <= status < 400


def challenge_signal(body, title=""):
    text = f"{title} {body}".lower()
    if any(token in text for token in ("captcha", "recaptcha", "验证码", "cloudflare", "verify you are human")):
        return "captcha_or_bot_challenge"
    if any(token in text for token in ("sign in", "login", "log in", "subscription", "subscribe", "登录", "注册会员")):
        return "login_or_subscription_signal"
    return ""


def result_signal(body, query, title=""):
    text = (body or "").lower()
    title_text = (title or "").lower()
    q = query.lower()
    challenge = challenge_signal(body, title)
    if challenge:
        return challenge
    if q in text:
        if any(token in text for token in ("result", "patent", "publication", "document", "hit", "treffer", "réultat", "检索结果", "搜索结果")):
            return "query_and_result_signal"
        return "query_echo_or_page_signal"
    if any(token in text or token in title_text for token in ("result", "patent", "publication", "document", "search", "recherche", "检索", "搜索")):
        return "search_page_signal_no_query_echo"
    return "page_loaded_no_result_signal" if text else "no_body"


def result_count(body):
    patterns = [
        r"(?:results?|hits?|documents?|patents?|treffer|résultats?|resultados?)\D{0,20}([0-9][0-9, .]*)",
        r"([0-9][0-9, .]*)\D{0,20}(?:results?|hits?|documents?|patents?|treffer|résultats?|resultados?)",
    ]
    for pattern in patterns:
        match = re.search(pattern, body or "", flags=re.I)
        if match:
            value = re.sub(r"[^0-9]", "", match.group(1))
            if value:
                return value
    return ""


def snippet(body, query):
    clean = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", html.unescape(body or ""))).strip()
    if not clean:
        return ""
    position = clean.lower().find(query.lower())
    if position < 0:
        return clean[:320]
    start = max(0, position - 120)
    return clean[start:start + 420]


def digest(body):
    return hashlib.sha256((body or "").encode("utf-8", errors="replace")).hexdigest()[:16]


def portal_specs(project, audit, plan, config):
    source_map = {row.get("source_id"): row for row in audit.get("records", [])}
    names = {row.get("source_id"): row.get("name", "") for row in audit.get("records", [])}
    specs = []
    explicit = config.get("portals", []) if isinstance(config, dict) else []
    explicit_ids = set()
    for portal in explicit:
        source_id = portal.get("source_id", "")
        if not source_id:
            continue
        explicit_ids.add(source_id)
        item = dict(portal)
        item["name"] = item.get("name") or names.get(source_id, source_id)
        specs.append(item)

    # Preserve the audit's automatically discovered known endpoints for a
    # reusable skill.  Case-specific portal specs override these records.
    for row in audit.get("records", []):
        source_id = row.get("source_id")
        if source_id in explicit_ids:
            continue
        if row.get("search_attempt") not in {"attempted", "browser_verified_public_endpoint"}:
            continue
        if not row.get("search_url"):
            continue
        specs.append({
            "source_id": source_id,
            "name": row.get("name", source_id),
            "search_url": row.get("search_url"),
            "method": "GET",
            "mode": "browser_manual" if row.get("search_attempt") == "browser_verified_public_endpoint" else "GET",
            "scope": "patent_or_literature",
            "basis": "audit_known_endpoint",
        })

    # Every public catalog page appears in the ledger even if a query endpoint
    # is still unknown.  This prevents a source from silently disappearing.
    for source_id, row in source_map.items():
        if not source_id or source_id in explicit_ids:
            continue
        access_class = row.get("access_class", "")
        if not access_class.startswith("public_"):
            continue
        specs.append({
            "source_id": source_id,
            "name": row.get("name", source_id),
            "search_url": row.get("final_url") or row.get("catalog_url"),
            "method": "GET",
            "mode": "not_mapped",
            "scope": "public_page",
            "basis": "public_catalog_page_without_stable_query_endpoint",
        })
    return specs


def execute_spec(spec, query, query_variants):
    mode = (spec.get("mode") or "GET").upper()
    method = (spec.get("method") or "GET").upper()
    base = {
        "source_id": spec.get("source_id", ""),
        "name": spec.get("name", ""),
        "scope": spec.get("scope", "patent_or_literature"),
        "basis": spec.get("basis", ""),
        "query": query,
        "query_variants": json.dumps(query_variants, ensure_ascii=False),
        "search_url": query_url(spec, query),
        "method": method,
        "mode": mode.lower(),
        "attempt_status": "",
        "http_status": "",
        "final_url": "",
        "title": "",
        "content_type": "",
        "response_bytes": "",
        "response_sha256_16": "",
        "result_signal": "",
        "result_count": "",
        "result_snippet": "",
        "error": "",
    }
    if mode in {"BROWSER_MANUAL", "MANUAL", "NOT_MAPPED"}:
        base["attempt_status"] = "browser_manual" if mode != "NOT_MAPPED" else "not_mapped"
        if mode == "NOT_MAPPED":
            base["error"] = "public page observed, but no stable search endpoint was identified"
        else:
            base["error"] = "public search page requires interactive browser submission or session state"
        return base

    params = interpolate(spec.get("params", {}), query)
    url = base["search_url"]
    if method == "GET" and params:
        separator = "&" if "?" in url else "?"
        url = url + separator + urlencode(params)
        base["search_url"] = url
    response = fetch(url, method=method, params=params if method == "POST" else None)
    body = response.get("body", "")
    title = extract_title(body)
    base.update({
        "attempt_status": "executed" if response.get("transport_status") == "ok" else "executed_http_error",
        "http_status": response.get("http_status", ""),
        "final_url": response.get("final_url", ""),
        "title": title,
        "content_type": response.get("content_type", ""),
        "response_bytes": len(body.encode("utf-8")),
        "response_sha256_16": digest(body),
        "result_signal": result_signal(body, query, title),
        "result_count": result_count(body),
        "result_snippet": snippet(body, query),
        "error": response.get("error", ""),
    })
    if response.get("transport_status") == "ok" and is_public(response.get("http_status")):
        base["attempt_status"] = "executed"
    return base


def write_csv(path, rows):
    fields = [
        "source_id", "name", "scope", "basis", "query", "query_variants", "search_url", "method", "mode", "attempt_status", "http_status", "final_url", "title", "content_type", "response_bytes", "response_sha256_16", "result_signal", "result_count", "result_snippet", "error",
    ]
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows({field: row.get(field, "") for field in fields} for row in rows)


def build_report(rows, generated, query, audit_count):
    statuses = Counter(row.get("attempt_status", "") for row in rows)
    signals = Counter(row.get("result_signal", "") for row in rows)
    executed = [row for row in rows if row.get("attempt_status") == "executed"]
    lines = [
        "# 公开来源实际检索执行报告", "", f"> 生成时间：{generated} · 来源目录记录：{audit_count} · 主检索词：`{query}`", "",
        "## 1. 执行口径", "",
        "本报告记录的是每个公开来源的检索动作，而不是把入口页面误当作检索结果。`executed` 表示已提交只读 GET/POST 请求；`browser_manual` 表示已确认公开检索入口但需要网页脚本、浏览器会话、验证码或状态表单；`not_mapped` 表示来源页面可访问，但当前没有可靠的检索参数或直达端点。商业数据库登录、订阅和验证码均未绕过。", "",
        "## 2. 结果统计", "", "| 指标 | 数量 |", "|---|---:|",
        f"| 纳入检索执行台账的来源 | {len(rows)} |",
        f"| 已实际提交查询 | {statuses.get('executed', 0)} |",
        f"| 已提交但返回 HTTP 错误 | {statuses.get('executed_http_error', 0)} |",
        f"| 公开入口需浏览器人工提交 | {statuses.get('browser_manual', 0)} |",
        f"| 公开页面尚未映射检索端点 | {statuses.get('not_mapped', 0)} |", "",
        "### 检索信号", "", "| 响应信号 | 数量 |", "|---|---:|",
    ]
    for key, value in signals.most_common():
        lines.append(f"| {key or '—'} | {value} |")
    lines += ["", "## 3. 已实际提交查询的来源", "", "| 来源 | 方法 | 检索 URL | HTTP | 结果信号 | 结果数信号 |", "|---|---|---|---:|---|---:|"]
    for row in executed:
        lines.append(f"| {row['source_id']} {row['name']} | {row['method']} | [{row['search_url']}]({row['search_url']}) | {row['http_status'] or '—'} | {row['result_signal'] or '—'} | {row['result_count'] or '—'} |")
    lines += ["", "## 4. 浏览器人工检索入口", "", "这些来源不代表没有结果，而是代表当前执行器未冒充浏览器，也没有猜测网页脚本的隐藏参数。打开 `search_url`，将主检索词和扩展词逐一提交后，应把命中文献写入 `source-log.jsonl`。", "", "| 来源 | 入口 | 原因 |", "|---|---|---|"]
    for row in rows:
        if row.get("attempt_status") == "browser_manual":
            lines.append(f"| {row['source_id']} {row['name']} | [{row['search_url']}]({row['search_url']}) | {row['error']} |")
    lines += ["", "## 5. 未映射来源", "", "公开页面未必是专利数据库；对这类来源保留入口和原因，后续可在 `source-search-portals.json` 增加正式的搜索 URL、POST 参数或浏览器人工标记。", "", "| 来源 | 页面 | 原因 |", "|---|---|---|"]
    for row in rows:
        if row.get("attempt_status") == "not_mapped":
            lines.append(f"| {row['source_id']} {row['name']} | [{row['search_url']}]({row['search_url']}) | {row['error']} |")
    lines += ["", "## 6. 证据链限制", "", "- 响应信号只证明查询请求被接受或返回了搜索页，不等于已完成专利族去重、权利要求抽取或法律状态核验。", "- 结果数信号是页面文本启发式提取，不能替代逐条保存的文献号和检索截图。", "- FTO 结论必须回到目标法域的官方全文、独立权利要求、审查档案和法律事件。", "", "## 7. 机器可读产物", "", "- `public-source-search-results.csv`：逐来源执行台账。", "- `public-source-search-results.json`：查询配置、统计和响应摘要。", "- `source-search-portals.json`：本案例的公开入口和查询协议配置。"]
    return "\n".join(lines) + "\n", statuses, signals


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-dir", required=True)
    args = parser.parse_args()
    project = Path(args.project_dir).expanduser().resolve()
    audit = load_json(project / "public-source-search-audit.json", {})
    plan = load_json(project / "fto-search-plan.json", {})
    config = load_json(project / "source-search-portals.json", {})
    query = config.get("query", {}).get("primary", DEFAULT_QUERY) if isinstance(config, dict) else DEFAULT_QUERY
    variants = config.get("query", {}).get("variants", DEFAULT_QUERY_VARIANTS) if isinstance(config, dict) else DEFAULT_QUERY_VARIANTS
    specs = portal_specs(project, audit, plan, config)
    rows = []
    for idx, spec in enumerate(specs, 1):
        row = execute_spec(spec, query, variants)
        rows.append(row)
        if idx % 10 == 0:
            print(f"Processed {idx}/{len(specs)} public source records", flush=True)
    rows.sort(key=lambda row: row.get("source_id", ""))
    generated = datetime.now(timezone.utc).isoformat()
    report, statuses, signals = build_report(rows, generated, query, audit.get("source_count", ""))
    csv_path = project / "public-source-search-results.csv"
    json_path = project / "public-source-search-results.json"
    md_path = project / "public-source-search-results-report.md"
    write_csv(csv_path, rows)
    md_path.write_text(report, encoding="utf-8")
    json_path.write_text(json.dumps({
        "schema_version": "1.0",
        "generated_at": generated,
        "query": query,
        "query_variants": variants,
        "record_count": len(rows),
        "counts_by_attempt_status": dict(statuses),
        "counts_by_result_signal": dict(signals),
        "records": rows,
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"record_count": len(rows), "counts_by_attempt_status": dict(statuses), "counts_by_result_signal": dict(signals), "csv": str(csv_path), "report": str(md_path)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
