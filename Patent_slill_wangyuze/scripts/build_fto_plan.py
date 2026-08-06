#!/usr/bin/env python3
"""Build a reusable, explainable FTO search plan from a case directory."""

import argparse
import json
from datetime import datetime, timezone
from html import escape
from pathlib import Path


def load_json(path, default=None):
    if not path.exists():
        return default if default is not None else {}
    return json.loads(path.read_text(encoding="utf-8"))


def load_source_registry(project):
    """Load the case override first, then the skill's CNIPA source snapshot."""
    candidates = [
        project / "patent-database-sources.json",
        Path(__file__).resolve().parents[1] / "references" / "patent-database-sources.json",
    ]
    for path in candidates:
        if path.exists():
            return load_json(path, {})
    return {"sources": [], "counts": {}, "source_policy": {}}


def source_routing(registry):
    routes = {}
    for source in registry.get("sources", []):
        routes.setdefault(source.get("default_use", "discovery_and_cross_check"), []).append(source.get("source_id"))
    return routes


def unique(values):
    out, seen = [], set()
    for value in values or []:
        if value is None:
            continue
        value = " ".join(str(value).split())
        if value and value.lower() not in seen:
            out.append(value)
            seen.add(value.lower())
    return out


def or_expr(terms, limit=16):
    terms = unique(terms)[:limit]
    return "(" + " OR ".join(f'"{term}"' for term in terms) + ")" if terms else "()"


def fallback_input(scope, identity):
    obj = scope.get("research_object", {})
    molecule = obj.get("molecule", "subject molecule")
    target = obj.get("target", "subject target")
    indication = obj.get("indication", "subject indication")
    drug_terms = unique([molecule] + obj.get("synonyms", []) + identity.get("molecule", {}).get("synonyms", []))
    target_terms = unique([target] + identity.get("target", {}).get("aliases", []))
    indication_terms = unique([indication] + identity.get("indication", {}).get("aliases", []))
    clusters = [
        {"id": "drug", "label": "研究对象", "base_terms": [molecule], "expanded_terms": drug_terms[1:], "source": "scope/identity"},
        {"id": "target", "label": "靶点/机制", "base_terms": [target], "expanded_terms": target_terms[1:], "source": "scope/identity"},
        {"id": "indication", "label": "适应症", "base_terms": [indication], "expanded_terms": indication_terms[1:], "source": "scope/identity"},
        {"id": "use", "label": "用途与治疗", "base_terms": ["method of treatment", "治疗方法"], "expanded_terms": ["combination", "regimen", "给药方案"], "source": "generic claim vocabulary"},
    ]
    return {
        "technical_solution": f"围绕 {molecule}、{target} 和 {indication} 的拟实施技术方案，进行组成、用途、给药、检测或组合治疗的 FTO 初筛。",
        "features": [
            {"id": "F01", "feature_type": "core", "importance": "core", "text": f"{molecule} 用于 {indication}，作用于 {target}。", "keyword_clusters": ["drug", "target", "indication"], "classifications": []},
            {"id": "F02", "feature_type": "necessary", "importance": "necessary", "text": "治疗或检测步骤包含给药对象、方案或患者分层。", "keyword_clusters": ["use"], "classifications": []},
        ],
        "keyword_clusters": clusters,
        "notes": ["这是由范围文件自动生成的保守模板，请在正式检索前人工补充技术特征、阈值和分类号。"],
    }


def normalize_input(raw, scope, identity):
    if not raw:
        raw = fallback_input(scope, identity)
    clusters = []
    for item in raw.get("keyword_clusters", []):
        item = dict(item)
        item["id"] = str(item.get("id", f"cluster-{len(clusters)+1}"))
        item["label"] = item.get("label", item["id"])
        item["base_terms"] = unique(item.get("base_terms", []))
        item["expanded_terms"] = unique(item.get("expanded_terms", []))
        item["terms"] = unique(item["base_terms"] + item["expanded_terms"])
        item["source"] = item.get("source", "user_provided / normalized")
        clusters.append(item)
    cluster_ids = {c["id"] for c in clusters}
    features = []
    for index, item in enumerate(raw.get("features", []), start=1):
        feature = dict(item)
        feature["id"] = str(feature.get("id", f"F{index:02d}"))
        feature["feature_type"] = feature.get("feature_type", "support")
        feature["importance"] = feature.get("importance", feature["feature_type"])
        feature["text"] = " ".join(str(feature.get("text", "")).split())
        feature["keyword_clusters"] = [x for x in feature.get("keyword_clusters", []) if x in cluster_ids]
        feature["classifications"] = unique(feature.get("classifications", []))
        feature["claim_test"] = feature.get("claim_test", "回到独立权利要求核验，不以说明书单独推定覆盖")
        features.append(feature)
    classifications = unique([code for feature in features for code in feature.get("classifications", [])])
    return {
        "technical_solution": raw.get("technical_solution", ""),
        "features": features,
        "keyword_clusters": clusters,
        "classifications": classifications,
        "notes": raw.get("notes", []),
    }


def build_queries(data, scope):
    clusters = {c["id"]: c for c in data["keyword_clusters"]}

    def terms(*ids, base=False):
        result = []
        for cluster_id in ids:
            cluster = clusters.get(cluster_id, {})
            result.extend(cluster.get("base_terms", []) if base else cluster.get("terms", []))
        return unique(result)

    def formula(groups, classification=False, base=False):
        pieces = [or_expr(terms(*group, base=base)) for group in groups if terms(*group, base=base)]
        if classification and data["classifications"]:
            pieces.append(or_expr(data["classifications"], limit=24))
        return " AND ".join(pieces)

    rounds = [
        {"id": "R1", "kind": "high_precision", "title": "关键词组合检索", "objective": "锁定研究对象、靶点、适应症和风险/监测场景同时出现的文献。", "fields": ["title", "abstract", "claims"], "formula": formula([["drug"], ["target"], ["indication"], ["irae", "organ"]], base=True), "source_routes": ["primary_or_status_check", "discovery_and_cross_check"]},
        {"id": "R2", "kind": "iterative_expansion", "title": "机制与通路扩展", "objective": "扩大到 PD-1/PD-L1 结合、阻断、免疫毒性和器官损伤表述。", "fields": ["full_text", "claims", "CPC/IPC"], "formula": formula([["drug"], ["target", "blockade"], ["irae", "organ"]]), "source_routes": ["primary_or_status_check", "discovery_and_cross_check"]},
        {"id": "R3", "kind": "iterative_expansion", "title": "肺部不良事件专项", "objective": "覆盖免疫相关性肺炎、间质性肺病、肺毒性和呼吸体征连续监测。", "fields": ["claims", "description"], "formula": formula([["drug", "indication"], ["pneumonitis"], ["monitoring", "imaging", "ggo"]]), "source_routes": ["primary_or_status_check", "discovery_and_cross_check", "context_only"]},
        {"id": "R4", "kind": "iterative_expansion", "title": "生化指标与内分泌监测", "objective": "覆盖 ALT/AST、肌酐、TSH、游离 T4、血糖等基线和治疗期监测。", "fields": ["claims", "abstract", "full_text"], "formula": formula([["drug", "indication"], ["biochemical", "analyte"]]), "source_routes": ["primary_or_status_check", "discovery_and_cross_check", "context_only"]},
        {"id": "R5", "kind": "iterative_expansion", "title": "结肠炎与处置方案", "objective": "覆盖腹泻分级、结肠炎、皮质类固醇和治疗决策。", "fields": ["claims", "description"], "formula": formula([["drug"], ["colitis"], ["steroid"]]), "source_routes": ["primary_or_status_check", "discovery_and_cross_check", "context_only"]},
        {"id": "R6", "kind": "classification_expansion", "title": "IPC/CPC 组合检索", "objective": "用分类号补足检测、抗体、免疫治疗和医疗数据分析类漏检。", "fields": ["IPC", "CPC", "claims"], "formula": formula([["target", "indication"], ["monitoring", "biochemical", "imaging"]], classification=True), "source_routes": ["classification_navigation", "primary_or_status_check", "discovery_and_cross_check"]},
        {"id": "R7", "kind": "relationship_expansion", "title": "关系与边界扩展", "objective": "从高相关文献扩展同族、申请人、引用、分案/继续申请和邻近技术。", "fields": ["family", "assignee", "citations", "legal_events"], "formula": "已命中文献的 family / assignee / citation / continuity expansion; 不使用自由文本替代权利要求核验", "source_routes": ["primary_or_status_check", "discovery_and_cross_check"]},
    ]
    for row in rounds:
        row["status"] = "planned"
        row["jurisdictions"] = scope.get("jurisdictions", []) + scope.get("related_jurisdictions", [])
        row["result_count"] = None
    return rounds


def build_plan(project, input_path=None):
    scope = load_json(project / "research_scope.json")
    identity = load_json(project / "identity.json")
    raw = load_json(input_path or project / "fto-input.json")
    registry = load_source_registry(project)
    data = normalize_input(raw, scope, identity)
    rounds = build_queries(data, scope)
    feature_counts = {key: sum(1 for f in data["features"] if f.get("importance") == key) for key in ("core", "necessary", "support", "context")}
    plan = {
        "schema_version": "1.0",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "case": project.name,
        "scope": scope,
        "entity_resolution": identity,
        "technical_solution": data["technical_solution"],
        "features": data["features"],
        "keyword_expansion": data["keyword_clusters"],
        "classifications": data["classifications"],
        "search_rounds": rounds,
        "source_catalog": {
            "upstream_repo": registry.get("upstream_repo"),
            "upstream_readme": registry.get("upstream_readme"),
            "upstream_readme_sha256": registry.get("upstream_readme_sha256"),
            "snapshot_at": registry.get("snapshot_at"),
            "counts": registry.get("counts", {}),
            "source_policy": registry.get("source_policy", {}),
            "sources": registry.get("sources", []),
        },
        "source_routing": source_routing(registry),
        "triage_rules": [
            "核心特征命中 + 权利要求类别相关：进入高优先级人工复核。",
            "必要特征命中但缺少核心对象或法域成员：标记为边界候选。",
            "仅说明书/摘要或相邻分类号命中：作为线索，不升级为覆盖结论。",
            "状态来自聚合镜像时标记待核验；以目标法域官方登记簿和审查档案为准。",
        ],
        "stage_summary": {
            "feature_count": len(data["features"]),
            "feature_counts": feature_counts,
            "keyword_cluster_count": len(data["keyword_clusters"]),
            "keyword_term_count": sum(len(c["terms"]) for c in data["keyword_clusters"]),
            "classification_count": len(data["classifications"]),
            "search_round_count": len(rounds),
            "candidate_count": 0,
            "comparison_count": 0,
        },
        "gaps": data["notes"] + [
            "每一轮的真实结果数量、纳排决定和官方法律状态需要在检索后回填。",
            "FTO 风险必须基于目标法域的完整独立权利要求和截至日期状态复核。",
        ],
    }
    return plan


def render_markdown(plan):
    lines = [f"# FTO 防侵权检索计划：{plan['case']}", "", "> 本文件用于公开专利候选初筛与后续 claim chart 准备，不构成侵权/不侵权法律意见。", "", "## 1. 技术方案", "", plan["technical_solution"], "", "## 2. 技术特征", "", "| ID | 类型 | 重要性 | 技术特征 | 分类号 |", "|---|---|---|---|---|"]
    for feature in plan["features"]:
        lines.append(f"| {feature['id']} | {feature.get('feature_type','')} | {feature.get('importance','')} | {feature['text']} | {', '.join(feature.get('classifications', [])) or '—'} |")
    lines += ["", "## 3. 扩展关键词", "", "| 词簇 | 基础词 | 扩展词 | 关联特征 | 来源 |", "|---|---|---|---|---|"]
    feature_map = {}
    for feature in plan["features"]:
        for cluster_id in feature.get("keyword_clusters", []):
            feature_map.setdefault(cluster_id, []).append(feature["id"])
    for cluster in plan["keyword_expansion"]:
        linked = ", ".join(unique(feature_map.get(cluster["id"], []))) or "—"
        lines.append(f"| {cluster['label']} | {'、'.join(cluster.get('base_terms', [])) or '—'} | {'、'.join(cluster.get('expanded_terms', [])) or '—'} | {linked} | {cluster.get('source','')} |")
    catalog = plan.get("source_catalog", {})
    counts = catalog.get("counts", {})
    lines += ["", "## 4. IPC/CPC", "", ", ".join(plan["classifications"]) or "未提供；需从高相关专利反向确认。", "", "## 5. 来源目录", "", f"本 Skill 纳入 CNIPA/PatentDatabases 的来源目录：上游列出 {counts.get('upstream_listings', '—')} 条，去重后 {counts.get('unique_urls', '—')} 个 URL。目录用于选择检索入口，不代表所有链接当前可访问或适合作为法律状态证据。", "", f"上游仓库：{catalog.get('upstream_repo', '—')}", "", "| 来源用途 | 数量 | 使用原则 |", "|---|---:|---|"]
    policy = catalog.get("source_policy", {})
    for route, count in sorted((counts.get("by_source_kind") or {}).items()):
        lines.append(f"| {route} | {count} | {policy.get(route, policy.get('description', '按来源角色核验'))} |")
    lines += ["", "## 6. 检索轮次", "", "| 轮次 | 目标 | 字段 | 来源路线 | 检索式 | 状态 |", "|---|---|---|---|---|---|"]
    for row in plan["search_rounds"]:
        lines.append(f"| {row['id']} {row['title']} | {row['objective']} | {', '.join(row['fields'])} | {', '.join(row.get('source_routes', []))} | `{row['formula']}` | {row['status']} |")
    lines += ["", "## 7. 初筛规则", ""] + [f"- {item}" for item in plan["triage_rules"]] + ["", "## 8. 待补证据", ""] + [f"- {item}" for item in plan["gaps"]]
    return "\n".join(lines) + "\n"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-dir", required=True)
    parser.add_argument("--input", default="")
    parser.add_argument("--output", default="fto-search-plan.json")
    args = parser.parse_args()
    project = Path(args.project_dir).expanduser().resolve()
    input_path = Path(args.input).expanduser().resolve() if args.input else None
    plan = build_plan(project, input_path)
    output = project / args.output
    output.write_text(json.dumps(plan, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    md_path = project / "fto-search-plan.md"
    md_path.write_text(render_markdown(plan), encoding="utf-8")
    print(f"Generated {output}")
    print(f"Generated {md_path}")
    print(json.dumps(plan["stage_summary"], ensure_ascii=False))


if __name__ == "__main__":
    main()
