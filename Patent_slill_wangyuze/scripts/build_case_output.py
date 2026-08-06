#!/usr/bin/env python3
"""Build the stable machine-readable output contract for one research case."""

import argparse
import csv
import hashlib
import json
import platform
import sys
from datetime import datetime, timezone
from pathlib import Path


REPORT_PATHS = [
    "00-executive-summary.md",
    "01-extraction-report.md",
    "02-patent-family-map-report.md",
    "03-technology-roadmap-report.md",
    "04-risk-and-fto-report.md",
    "05-innovation-space-report.md",
    "06-evidence-chain-report.md",
    "07-source-catalog-report.md",
    "report-index.md",
    "report-index.html",
    "report-visuals.html",
    "00-executive-summary.html",
    "01-extraction-report.html",
    "02-patent-family-map-report.html",
    "03-technology-roadmap-report.html",
    "04-risk-and-fto-report.html",
    "05-innovation-space-report.html",
    "06-evidence-chain-report.html",
    "07-source-catalog-report.html",
]


def load_json(path, default=None):
    if not path.exists():
        return default if default is not None else {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return default if default is not None else {}


def load_csv(path):
    if not path or not path.exists():
        return []
    with path.open(newline="", encoding="utf-8-sig") as handle:
        return [{str(k).strip(): (v or "").strip() for k, v in row.items()} for row in csv.DictReader(handle)]


def load_jsonl(path):
    if not path.exists():
        return []
    rows = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            rows.append(json.loads(line))
        except json.JSONDecodeError:
            rows.append({"raw": line, "parse_error": True})
    return rows


def first_match(project, pattern):
    matches = sorted(project.glob(pattern))
    return matches[0] if matches else None


def sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def relative_path(project, path):
    return str(path.relative_to(project)) if path.is_relative_to(project) else str(path)


def input_paths(project):
    paths = [
        project / "research_scope.json",
        project / "identity.json",
        project / "fto-search-plan.json",
        project / "source-log.jsonl",
        project / "public-source-search-audit.json",
        project / "public-source-search-results.json",
        project / "source-search-portals.json",
        project / "source-portal-overrides.json",
        project / "patent-database-sources.json",
        project / "fto-candidate-ranking.csv",
    ]
    paths.extend(sorted(project.glob("*-patent-families.csv")))
    paths.extend(sorted(project.glob("*-claim-elements.csv")))
    paths.extend(sorted(project.glob("*-evidence.csv")))
    return [path for path in paths if path.exists()]


def source_urls(*collections):
    urls = set()
    for collection in collections:
        for row in collection or []:
            if not isinstance(row, dict):
                continue
            for value in row.values():
                if isinstance(value, str) and value.startswith(("http://", "https://")):
                    urls.add(value)
    return sorted(urls)


def add_uncertainty(items, category, statement, impact, confidence, linked_ids, next_action, evidence_keys):
    items.append({
        "id": f"U-{len(items) + 1:03d}",
        "category": category,
        "statement": statement,
        "impact": impact,
        "confidence": confidence,
        "linked_ids": sorted(set(linked_ids)),
        "next_action": next_action,
        "evidence_keys": evidence_keys,
    })


def build_uncertainty(families, claims, audit, public_search):
    items = []
    status_families = [
        row.get("family_id")
        for row in families
        if "official" not in (row.get("status_source", "") + row.get("official_status", "")).lower()
    ]
    if status_families:
        add_uncertainty(
            items,
            "official_status",
            "部分状态信号来自公开镜像或未明确标注目标法域官方登记簿。",
            "不能仅凭聚合页面判断当前有效性、到期、放弃或国家阶段状态。",
            "medium",
            status_families,
            "逐族下载 CN/US 官方登记簿和审查/法律事件记录，保存核验日期。",
            ["family.official_status", "family.status_source"],
        )
    incomplete_claims = [
        row.get("family_id")
        for row in claims
        if not row.get("claim_location") or "pending" in row.get("claim_location", "").lower() or "independent" not in row.get("claim_location", "").lower()
    ]
    if incomplete_claims:
        add_uncertainty(
            items,
            "claim_scope",
            "部分 claim 要素来自摘要、说明书或快速抽取定位，完整独立权利要求范围尚未逐项核对。",
            "不能把公开披露、功能描述或说明书内容直接升级为可执行的权利要求覆盖。",
            "medium",
            incomplete_claims,
            "对高优先族建立逐项 claim chart，记录独立权利要求、从属项和审查后文本。",
            ["claim.claim_location", "claim.coverage", "claim.notes"],
        )
    national_phase = [
        row.get("family_id")
        for row in families
        if not row.get("jurisdictions") or "CN" not in row.get("jurisdictions", "") or "US" not in row.get("jurisdictions", "")
    ]
    if national_phase:
        add_uncertainty(
            items,
            "national_phase",
            "族级公开记录不等于 CN/US 均已进入、仍在审查或具有相同权利要求范围。",
            "目标法域成员、分案/继续申请和国家阶段差异可能改变 FTO 复核顺序。",
            "low",
            national_phase,
            "按优先权链逐项核对 CN/US 成员、分案/继续申请和官方事件。",
            ["family.jurisdictions", "family.earliest_priority", "family.status_as_of"],
        )
    if not families or not any(row.get("key_claim_elements") for row in families):
        add_uncertainty(
            items,
            "structure_or_claim_data",
            "当前输入没有足够的结构/组成或权利要求要素记录。",
            "只能输出召回线索，不能支持结构层或权利要求层结论。",
            "low",
            [],
            "补充结构、序列、盐型/晶型或官方权利要求文本，并降低报告级别。",
            ["family.key_claim_elements", "records.claims"],
        )
    audit_records = audit.get("records", []) if isinstance(audit, dict) else []
    search_records = public_search.get("records", []) if isinstance(public_search, dict) else []
    has_manual = any(
        str(row.get("attempt_status") or row.get("search_attempt") or row.get("mode")).lower() in {"browser_manual", "not_mapped", "manual_interactive_or_endpoint_unknown"}
        for row in audit_records + search_records
    )
    if has_manual:
        add_uncertainty(
            items,
            "source_access",
            "部分公开来源需要浏览器会话、JavaScript、验证码或尚未建立稳定检索端点。",
            "来源访问已记录，但不能把页面打开、结果数字或入口存在误写成完成了逐条检索。",
            "high",
            [],
            "保留 browser_manual/not_mapped 台账，人工提交只读检索并回写文献号、截图和来源日志。",
            ["public-source-search-audit.json", "public-source-search-results.json"],
        )
    return items


def build_failure_cases(families, claims, audit, public_search):
    status_ids = [row.get("family_id") for row in families if "official" not in (row.get("status_source", "") + row.get("official_status", "")).lower()]
    claim_incomplete = [row.get("family_id") for row in claims if not row.get("claim_location") or "pending" in row.get("claim_location", "").lower()]
    audit_records = audit.get("records", []) if isinstance(audit, dict) else []
    search_records = public_search.get("records", []) if isinstance(public_search, dict) else []
    manual_records = [
        row for row in audit_records + search_records
        if str(row.get("attempt_status") or row.get("search_attempt") or row.get("mode")).lower() in {"browser_manual", "not_mapped", "manual_interactive_or_endpoint_unknown"}
    ]
    timeout_records = [row for row in audit_records + search_records if any(token in str(row.get("error", "")).lower() for token in ("timeout", "timed out", "connection"))]
    return [
        {
            "id": "official_status_unavailable",
            "title": "目标法域官方状态不可用",
            "observed": bool(status_ids),
            "trigger": "官方登记簿、法律事件或国家阶段记录未采集，或当前只有公开镜像状态。",
            "impact": "不得将 active/inactive/pending 标签写成法律结论。",
            "fallback": "保留 status_unknown，输出官方核验任务并降低风险结论强度。",
            "linked_ids": status_ids,
        },
        {
            "id": "claim_text_incomplete",
            "title": "完整独立权利要求不可得",
            "observed": bool(claim_incomplete),
            "trigger": "claim_location 缺失、定位为摘要/说明书，或审查后文本未采集。",
            "impact": "不能完成逐项 claim chart，也不能判断法律等同。",
            "fallback": "标记待核验，回退到代表文献和要素级初筛，不输出侵权判断。",
            "linked_ids": claim_incomplete,
        },
        {
            "id": "browser_or_unmapped_source",
            "title": "来源只能人工操作或尚未映射",
            "observed": bool(manual_records),
            "trigger": "来源依赖 JavaScript、会话、验证码、POST 状态或没有可靠端点。",
            "impact": "不能把搜索页加载或启发式结果数字当作正式命中数量。",
            "fallback": "记录 browser_manual/not_mapped，人工执行只读检索并保存文献号和截图。",
            "linked_ids": [row.get("source_id") for row in manual_records if row.get("source_id")],
        },
        {
            "id": "network_or_endpoint_failure",
            "title": "网络或检索端点失败",
            "observed": bool(timeout_records),
            "trigger": "请求超时、连接失败、跳转失效或响应无法解析。",
            "impact": "该来源不能进入已执行结果集，召回可能存在系统性缺口。",
            "fallback": "保留错误摘要和时间戳，改用官方镜像/浏览器入口，不绕过访问控制。",
            "linked_ids": [row.get("source_id") for row in timeout_records if row.get("source_id")],
        },
    ]


def build_case_output(project):
    scope = load_json(project / "research_scope.json")
    identity = load_json(project / "identity.json")
    plan = load_json(project / "fto-search-plan.json")
    families_path = first_match(project, "*-patent-families.csv")
    claims_path = first_match(project, "*-claim-elements.csv")
    evidence_path = first_match(project, "*-evidence.csv")
    families = load_csv(families_path)
    claims = load_csv(claims_path)
    evidence = load_csv(evidence_path)
    ranking = load_csv(project / "fto-candidate-ranking.csv")
    source_log = load_jsonl(project / "source-log.jsonl")
    audit = load_json(project / "public-source-search-audit.json", {})
    public_search = load_json(project / "public-source-search-results.json", {})
    catalog = plan.get("source_catalog") or load_json(project / "patent-database-sources.json", {})
    visual_manifest = load_json(project / "visuals" / "manifest.json", {})
    generated = datetime.now(timezone.utc).isoformat()
    skill_root = Path(__file__).resolve().parents[1]
    version_path = skill_root / "VERSION"
    skill_version = version_path.read_text(encoding="utf-8").strip() if version_path.exists() else "unknown"
    files = input_paths(project)
    uncertainty = build_uncertainty(families, claims, audit, public_search)
    failure_cases = build_failure_cases(families, claims, audit, public_search)
    urls = source_urls(families, claims, evidence, ranking, source_log)
    report_rows = []
    for report in REPORT_PATHS:
        path = project / report
        report_rows.append({"path": report, "format": path.suffix.lstrip(".") or "binary", "exists": path.exists(), "status": "complete" if path.exists() else "missing"})
    for path in sorted(project.glob("*-fto-report.docx")):
        report_rows.append({"path": path.name, "format": "docx", "exists": True, "status": "complete"})
    visual_count = len(visual_manifest.get("charts", [])) if isinstance(visual_manifest, dict) else 0
    search_counts = public_search.get("counts_by_attempt_status", {}) if isinstance(public_search, dict) else {}
    metrics = {
        "family_count": len(families),
        "claim_count": len(claims),
        "evidence_count": len(evidence),
        "ranking_count": len(ranking),
        "source_url_count": len(urls),
        "source_log_count": len(source_log),
        "report_count": sum(1 for row in report_rows if row["exists"]),
        "visual_count": visual_count,
        "executed_source_count": search_counts.get("executed", 0),
        "manual_source_count": search_counts.get("browser_manual", 0),
        "unmapped_source_count": search_counts.get("not_mapped", 0),
        "uncertainty_count": len(uncertainty),
        "observed_failure_count": sum(1 for row in failure_cases if row["observed"]),
    }
    input_hashes = {relative_path(project, path): sha256(path) for path in files}
    output_candidates = [project / row["path"] for row in report_rows if row["exists"]]
    output_hashes = {relative_path(project, path): sha256(path) for path in output_candidates}
    commands = [
        "python3 scripts/validate_case.py --project-dir <case-dir>",
        "python3 scripts/build_modular_reports.py --project-dir <case-dir>",
        "python3 scripts/build_case_output.py --project-dir <case-dir>",
        "python3 scripts/run_reproducibility.py --project-dir <case-dir> --runs 3",
    ]
    output = {
        "schema_version": "1.0",
        "case": {
            "case_id": project.name,
            "research_object": scope.get("research_object", {}),
            "jurisdictions": scope.get("jurisdictions", []),
            "related_jurisdictions": scope.get("related_jurisdictions", []),
            "as_of": scope.get("as_of"),
            "depth": scope.get("depth"),
            "focus": scope.get("focus", []),
        },
        "run": {
            "run_id": f"{project.name}-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}",
            "generated_at": generated,
            "skill_version": skill_version,
            "pipeline": ["scope", "identity", "source_catalog", "family_normalization", "claim_extraction", "evidence_chain", "fto_triage", "modular_reports"],
            "python": platform.python_version(),
        },
        "metrics": metrics,
        "records": {"families": families, "claims": claims, "evidence": evidence, "ranking": ranking},
        "uncertainty": {
            "summary": "当前输出保留来源、法域、claim 范围和访问层级的不确定性；未核验内容不得升级为法律或科学确定结论。",
            "items": uncertainty,
        },
        "failure_cases": failure_cases,
        "reports": report_rows,
        "reproducibility": {
            "commands": commands,
            "inputs": [{"path": path, "sha256": digest} for path, digest in sorted(input_hashes.items())],
            "output_hashes": output_hashes,
            "source_catalog_snapshot": catalog.get("upstream_readme_sha256") if isinstance(catalog, dict) else None,
        },
        "contract": {
            "schema_version": "1.0",
            "schema_path": "references/output-schema.json",
        },
        "identity": identity,
        "plan_summary": {
            "search_round_count": len(plan.get("search_rounds", [])),
            "feature_count": len(plan.get("features", [])),
            "keyword_cluster_count": len(plan.get("keyword_expansion", [])),
            "classification_count": len(plan.get("classifications", [])),
        },
    }
    output_path = project / "case-output.json"
    output_path.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return output


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-dir", required=True)
    args = parser.parse_args()
    project = Path(args.project_dir).expanduser().resolve()
    output = build_case_output(project)
    print(json.dumps({"output": str(project / "case-output.json"), "metrics": output["metrics"]}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
