#!/usr/bin/env python3
"""Rank existing claim-element records against an FTO search plan."""

import argparse
import csv
import json
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path


WEIGHTS = {"core": 4.0, "necessary": 3.0, "support": 1.5, "context": 0.5}


def load_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def norm(value):
    return " ".join(str(value or "").lower().replace("-", " ").split())


def csv_rows(path):
    if not path or not path.exists():
        return []
    with path.open(newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        return [{str(k).strip(): (v or "").strip() for k, v in row.items()} for row in reader]


def find_file(project, pattern):
    matches = sorted(project.glob(pattern))
    return matches[0] if matches else None


def portable_path(path, project):
    if not path:
        return None
    try:
        return path.resolve().relative_to(project.resolve()).as_posix()
    except ValueError:
        return str(path)


def family_index(rows):
    return {row.get("family_id", ""): row for row in rows if row.get("family_id")}


def build_feature_matches(plan, text):
    matches = []
    for feature in plan.get("features", []):
        cluster_hits = []
        for cluster in plan.get("keyword_expansion", []):
            if cluster.get("id") in feature.get("keyword_clusters", []):
                # Technical prose is useful for a human but is intentionally not
                # used as a hidden semantic model; each declared keyword cluster
                # must contribute separately to feature coverage.
                hit_terms = [term for term in cluster.get("terms", []) if norm(term) and norm(term) in text]
                cluster_hits.append({"cluster_id": cluster["id"], "label": cluster.get("label", cluster["id"]), "terms": hit_terms[:12]})
        if not cluster_hits:
            continue
        hit_clusters = [item for item in cluster_hits if item["terms"]]
        coverage = len(hit_clusters) / len(cluster_hits)
        threshold = {"core": 0.75, "necessary": 0.75, "support": 0.5, "context": 0.5}.get(feature.get("importance", "support"), 0.5)
        if coverage > 0:
            matches.append({
                "feature_id": feature["id"],
                "importance": feature.get("importance", "support"),
                "coverage": round(coverage, 4),
                "qualified": coverage >= threshold,
                "terms": [term for item in hit_clusters for term in item["terms"]][:16],
                "clusters": [item["label"] for item in hit_clusters],
            })
    return matches


def rank(plan, claim_rows, family_rows):
    families = family_index(family_rows)
    total_weight = sum(WEIGHTS.get(feature.get("importance", "support"), 1.0) for feature in plan.get("features", [])) or 1.0
    grouped = defaultdict(list)
    for row in claim_rows:
        grouped[row.get("family_id", "unassigned")].append(row)

    ranked = []
    for family_id, rows in grouped.items():
        family = families.get(family_id, {})
        family_text = " ".join(norm(family.get(key, "")) for key in ("claim_theme", "claim_categories", "key_claim_elements", "mutation_or_biomarker", "relevance"))
        text = " ".join(norm(row.get(key, "")) for row in rows for key in ("element", "claim_category", "claim_location", "notes")) + " " + family_text
        feature_matches = build_feature_matches(plan, text)
        qualified_matches = [item for item in feature_matches if item["qualified"]]
        matched_ids = {item["feature_id"] for item in qualified_matches}
        partial_ids = {item["feature_id"] for item in feature_matches if not item["qualified"]}
        matched_weight = sum(WEIGHTS.get(item["importance"], 1.0) * item["coverage"] for item in feature_matches)
        categories = sorted({row.get("claim_category", "") for row in rows if row.get("claim_category")})
        status_text = norm(family.get("official_status", "") + " " + family.get("status_confidence", ""))
        relevance = norm(family.get("relevance", ""))
        core_hits = sum(1 for item in qualified_matches if item["importance"] == "core")
        necessary_hits = sum(1 for item in qualified_matches if item["importance"] == "necessary")
        score = matched_weight / total_weight
        if core_hits:
            score += 0.15
        if necessary_hits:
            score += 0.08
        if relevance == "core":
            score += 0.08
        if any(token in status_text for token in ("active", "pending", "granted", "authorized", "授权", "审查中")):
            score += 0.03
        score = min(score, 1.0)
        if core_hits >= 1 and necessary_hits >= 1:
            priority = "HIGH"
        elif core_hits or necessary_hits >= 2:
            priority = "MEDIUM"
        else:
            priority = "LOW"
        ranked.append({
            "family_id": family_id,
            "representative_document": family.get("representative_document", rows[0].get("document", "")),
            "relevance": family.get("relevance", "unknown"),
            "review_priority": priority,
            "screen_score": round(score, 4),
            "feature_coverage": round(matched_weight / total_weight, 4),
            "matched_features": ", ".join(sorted(matched_ids)),
            "partial_features": ", ".join(sorted(partial_ids)),
            "matched_terms": "; ".join(f'{item["feature_id"]}: {", ".join(item["terms"])}' for item in feature_matches),
            "matched_feature_coverage": "; ".join(f'{item["feature_id"]}={item["coverage"]:.2f} ({", ".join(item["clusters"])})' for item in feature_matches),
            "claim_categories": "; ".join(categories),
            "official_status_signal": family.get("official_status", "not available"),
            "status_source": family.get("status_source", ""),
            "source_url": family.get("source_url", rows[0].get("evidence_url", "")),
            "notes": "关键词/要素初筛，不等于权利要求覆盖；需核对完整独立权利要求、法域成员和官方状态。",
        })
    return sorted(ranked, key=lambda row: (-row["screen_score"], row["family_id"]))


def write_csv(path, rows):
    fields = ["family_id", "representative_document", "relevance", "review_priority", "screen_score", "feature_coverage", "matched_features", "partial_features", "matched_feature_coverage", "matched_terms", "claim_categories", "official_status_signal", "status_source", "source_url", "notes"]
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def write_markdown(path, rows, claim_path, family_path):
    lines = ["# FTO 候选专利初筛", "", "> 这是透明的关键词/权利要求要素排序，不是侵权结论。", "", f"- 权利要求要素来源：`{claim_path.name if claim_path else '未找到'}`", f"- 专利族来源：`{family_path.name if family_path else '未找到'}`", f"- 生成时间：{datetime.now(timezone.utc).isoformat()}", "", "| 家族 | 代表文献 | 优先级 | 初筛分数 | 命中特征 | 权利要求类别 |", "|---|---|---|---:|---|---|"]
    for row in rows:
        lines.append(f"| {row['family_id']} | {row['representative_document']} | {row['review_priority']} | {row['screen_score']:.2f} | {row['matched_features'] or '—'} | {row['claim_categories'] or '—'} |")
    lines += ["", "## 阅读方式", "", "- HIGH/MEDIUM 仅表示优先核对，不表示存在侵权。", "- 需要把候选族的每一项独立权利要求与拟实施方案逐要素比对。", "- `official_status_signal` 是已有案例数据的状态字段；缺少官方登记簿时必须回填核验。"]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-dir", required=True)
    parser.add_argument("--claims", default="")
    parser.add_argument("--families", default="")
    parser.add_argument("--output", default="fto-candidate-ranking.csv")
    args = parser.parse_args()
    project = Path(args.project_dir).expanduser().resolve()
    plan = load_json(project / "fto-search-plan.json")
    claim_path = Path(args.claims).expanduser().resolve() if args.claims else find_file(project, "*-claim-elements.csv")
    family_path = Path(args.families).expanduser().resolve() if args.families else find_file(project, "*-patent-families.csv")
    ranked = rank(plan, csv_rows(claim_path), csv_rows(family_path))
    out = project / args.output
    write_csv(out, ranked)
    md = project / "fto-candidate-ranking.md"
    write_markdown(md, ranked, claim_path, family_path)
    plan["stage_summary"]["candidate_count"] = len(ranked)
    plan["stage_summary"]["comparison_count"] = sum(1 for row in ranked if row["matched_features"])
    plan["candidate_screen"] = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "input_claims": portable_path(claim_path, project),
        "input_families": portable_path(family_path, project),
        "ranking_file": portable_path(out, project),
        "method": "declared keyword cluster overlap + claim category/relevance/status signals",
        "disclaimer": "Screening only; no infringement or validity conclusion.",
    }
    (project / "fto-search-plan.json").write_text(json.dumps(plan, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Generated {out}")
    print(f"Generated {md}")
    print(json.dumps({"candidate_count": len(ranked), "comparison_count": plan["stage_summary"]["comparison_count"]}, ensure_ascii=False))


if __name__ == "__main__":
    main()
