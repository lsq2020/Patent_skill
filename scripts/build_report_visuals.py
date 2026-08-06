#!/usr/bin/env python3
"""Build dependency-free SVG statistics and an FTO-style visual report hub.

The charts are deliberately generated from the case CSV/JSON files instead of
being embedded as hand-written numbers.  SVG keeps the output portable and
crisp in Markdown, Word-to-PDF workflows, and the local browser.
"""

import argparse
import csv
import html
import json
import re
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path


PALETTE = ["#1264d9", "#3c8eea", "#72b7f5", "#9bd4f7", "#f2a93b", "#e3655b", "#6d7892", "#4ab39a"]


def load_json(path, default=None):
    if not path.exists():
        return default if default is not None else {}
    return json.loads(path.read_text(encoding="utf-8"))


def load_csv(path):
    if not path or not path.exists():
        return []
    with path.open(newline="", encoding="utf-8-sig") as handle:
        return [{str(k).strip(): (v or "").strip() for k, v in row.items()} for row in csv.DictReader(handle)]


def first_match(project, pattern):
    matches = sorted(project.glob(pattern))
    return matches[0] if matches else None


def split_values(value):
    return [x.strip() for x in re.split(r"[;,|/]+", str(value or "")) if x.strip()]


def compact(value, limit=56):
    value = " ".join(str(value or "").split())
    return value if len(value) <= limit else value[: limit - 1] + "…"


def family_stage(family):
    text = " ".join([
        family.get("claim_theme", ""), family.get("claim_categories", ""),
        family.get("key_claim_elements", ""), family.get("mutation_or_biomarker", ""),
    ]).lower()
    has_combo = any(token in text for token in ("combination", "regimen", "method of treatment", "联合", "给药"))
    has_selection = any(token in text for token in ("patient selection", "biomarker", "diagnostic", "标志物", "诊断"))
    if any(token in text for token in ("composition", "antibody", "sequence", "compound", "化合物", "抗体")):
        return "结构/组成"
    if any(token in text for token in ("formulation", "制剂", "excipient", "晶型", "salt")):
        return "制剂/工艺"
    if has_combo and has_selection:
        return "联合/患者分层"
    if has_selection:
        return "标志物/诊断"
    if any(token in text for token in ("regimen", "combination", "method", "治疗", "联合", "给药")):
        return "治疗用途/方案"
    return "邻近技术/待归类"


def status_bucket(value):
    text = str(value or "").lower()
    if any(token in text for token in ("pending", "申请", "公开", "审查")):
        return "公开/待审查"
    if any(token in text for token in ("active", "有效", "granted", "授权")):
        return "授权/状态较强"
    if any(token in text for token in ("expired", "失效", "abandoned", "放弃")):
        return "失效/放弃信号"
    if any(token in text for token in ("unknown", "需", "require", "未", "核验")):
        return "待官方核验"
    return "未分类"


def count_values(rows, field, transform=None):
    counter = Counter()
    for row in rows:
        values = transform(row) if transform else split_values(row.get(field, ""))
        for value in values:
            counter[value] += 1
    return counter


def year_counts(families):
    counter = Counter()
    for row in families:
        match = re.match(r"(\d{4})", row.get("earliest_priority", ""))
        if match:
            counter[match.group(1)] += 1
    return counter


def bar_svg(title, values, *, width=760, label_width=210, color_index=0, note=""):
    values = [(str(k), int(v)) for k, v in values if str(k).strip()]
    values = values[:12]
    row_height = 34
    top = 74
    bottom = 36
    height = max(190, top + max(1, len(values)) * row_height + bottom)
    max_value = max([v for _, v in values] or [1])
    safe_title = html.escape(title)
    lines = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" role="img" aria-label="{safe_title}">',
        f"<title>{safe_title}</title>",
        f'<rect width="{width}" height="{height}" rx="16" fill="#ffffff"/>',
        f'<text x="28" y="34" font-family="-apple-system,BlinkMacSystemFont,Segoe UI,sans-serif" font-size="18" font-weight="700" fill="#17233b">{safe_title}</text>',
    ]
    if note:
        lines.append(f'<text x="28" y="56" font-family="-apple-system,BlinkMacSystemFont,Segoe UI,sans-serif" font-size="11" fill="#71809a">{html.escape(note)}</text>')
    if not values:
        lines.append('<text x="28" y="105" font-family="-apple-system,BlinkMacSystemFont,Segoe UI,sans-serif" font-size="14" fill="#71809a">当前数据集暂无可绘制记录</text>')
    for idx, (label, value) in enumerate(values):
        y = top + idx * row_height
        bar_x = label_width
        bar_max = width - bar_x - 84
        bar_w = 0 if max_value == 0 else max(2, bar_max * value / max_value)
        fill = PALETTE[(color_index + idx) % len(PALETTE)]
        lines.extend([
            f'<text x="28" y="{y + 16}" font-family="-apple-system,BlinkMacSystemFont,Segoe UI,sans-serif" font-size="12" fill="#44536c">{html.escape(compact(label, 30))}</text>',
            f'<rect x="{bar_x}" y="{y + 3}" width="{bar_max}" height="18" rx="9" fill="#edf2fa"/>',
            f'<rect x="{bar_x}" y="{y + 3}" width="{bar_w:.1f}" height="18" rx="9" fill="{fill}"/>',
            f'<text x="{width - 54}" y="{y + 16}" text-anchor="end" font-family="-apple-system,BlinkMacSystemFont,Segoe UI,sans-serif" font-size="13" font-weight="700" fill="#17233b">{value}</text>',
        ])
    lines.append("</svg>")
    return "\n".join(lines)


def metric_card(label, value, hint):
    return f'<div class="metric"><div class="metric-value">{html.escape(str(value))}</div><div class="metric-label">{html.escape(label)}</div><div class="metric-hint">{html.escape(hint)}</div></div>'


def build_dataset(project):
    families = load_csv(first_match(project, "*-patent-families.csv"))
    claims = load_csv(first_match(project, "*-claim-elements.csv"))
    evidence = load_csv(first_match(project, "*-evidence.csv"))
    ranking = load_csv(project / "fto-candidate-ranking.csv")
    plan = load_json(project / "fto-search-plan.json")
    catalog = plan.get("source_catalog") or load_json(project / "patent-database-sources.json")
    source_log = []
    log_path = project / "source-log.jsonl"
    if log_path.exists():
        for line in log_path.read_text(encoding="utf-8").splitlines():
            if line.strip():
                try:
                    source_log.append(json.loads(line))
                except json.JSONDecodeError:
                    pass
    source_rows = catalog.get("sources", [])

    chart_defs = [
        {
            "id": "family-theme", "title": "专利族技术主题分布", "metric_definition": "按 family_id 统计，每族归入一个主技术阶段。",
            "source_fields": ["claim_theme", "claim_categories", "key_claim_elements", "mutation_or_biomarker"],
            "values": sorted(Counter(family_stage(f) for f in families).items(), key=lambda x: (-x[1], x[0])),
        },
        {
            "id": "priority-year", "title": "最早优先权年度分布", "metric_definition": "按族级 earliest_priority 的年份统计。",
            "source_fields": ["earliest_priority"], "values": sorted(year_counts(families).items()),
        },
        {
            "id": "applicant", "title": "申请人/受让人分布", "metric_definition": "按当前族 CSV 的 applicant_or_assignee 字段统计；未做集团级消歧。",
            "source_fields": ["applicant_or_assignee"], "values": sorted(count_values(families, "applicant_or_assignee").items(), key=lambda x: (-x[1], x[0])),
        },
        {
            "id": "jurisdiction", "title": "法域覆盖", "metric_definition": "按族 CSV 的 jurisdictions 字段统计存在成员记录的族数。",
            "source_fields": ["jurisdictions"], "values": sorted(count_values(families, "jurisdictions").items(), key=lambda x: (-x[1], x[0])),
        },
        {
            "id": "claim-category", "title": "权利要求类别分布", "metric_definition": "按 claim-elements.csv 的 claim_category 记录数统计。",
            "source_fields": ["claim_category"], "values": sorted(count_values(claims, "claim_category").items(), key=lambda x: (-x[1], x[0])),
        },
        {
            "id": "status", "title": "状态信号分布", "metric_definition": "把官方状态和状态来源文字归入研究阶段信号，不替代官方法律状态。",
            "source_fields": ["official_status", "status_source", "official_status_signal"],
            "values": sorted(Counter(status_bucket(f"{f.get('official_status', '')} {f.get('status_source', '')}") for f in families).items(), key=lambda x: (-x[1], x[0])),
        },
        {
            "id": "risk-priority", "title": "FTO 复核优先级", "metric_definition": "按 fto-candidate-ranking.csv 的 review_priority 统计；是复核队列，不是侵权概率。",
            "source_fields": ["review_priority"], "values": sorted(count_values(ranking, "review_priority").items(), key=lambda x: ({"HIGH": 0, "MEDIUM": 1, "LOW": 2}.get(x[0], 9), x[0])),
        },
        {
            "id": "evidence-confidence", "title": "证据置信度分布", "metric_definition": "按 evidence.csv 的 confidence 字段统计。",
            "source_fields": ["confidence"], "values": sorted(count_values(evidence, "confidence").items(), key=lambda x: (-x[1], x[0])),
        },
        {
            "id": "evidence-type", "title": "证据类型分布", "metric_definition": "按 evidence.csv 的 evidence_type 字段统计。",
            "source_fields": ["evidence_type"], "values": sorted(count_values(evidence, "evidence_type").items(), key=lambda x: (-x[1], x[0])),
        },
        {
            "id": "source-kind", "title": "来源角色分布", "metric_definition": "按 CNIPA/PatentDatabases 来源目录中的 source_kind 统计。",
            "source_fields": ["source_catalog.sources[].source_kind"], "values": sorted(Counter(s.get("source_kind", "未分类") for s in source_rows).items(), key=lambda x: (-x[1], x[0])),
        },
        {
            "id": "search-round", "title": "检索轮次覆盖", "metric_definition": "按 FTO 搜索计划的 search_rounds 统计每轮主题的任务数量。",
            "source_fields": ["fto-search-plan.search_rounds"], "values": [(f"R{idx + 1}", 1) for idx, _ in enumerate(plan.get("search_rounds", []))],
        },
    ]
    metrics = {
        "families": len(families), "claims": len(claims), "evidence": len(evidence),
        "fto_candidates": len(ranking), "search_rounds": len(plan.get("search_rounds", [])),
        "source_urls": catalog.get("counts", {}).get("unique_urls", "—"),
        "source_records": catalog.get("counts", {}).get("upstream_listings", "—"),
        "source_log_entries": len(source_log),
    }
    return families, claims, evidence, ranking, plan, catalog, source_log, chart_defs, metrics


def build_html(project, chart_defs, metrics, scope, manifest):
    obj = scope.get("research_object", {})
    title = f"{obj.get('molecule', project.name)} · 专利分析统计总览"
    chart_map = {c["id"]: c for c in chart_defs}
    cards = [
        metric_card("专利族", metrics["families"], "family_id 去重单位"),
        metric_card("claim 要素", metrics["claims"], "逐条抽取记录"),
        metric_card("证据条目", metrics["evidence"], "可回溯事实/推断"),
        metric_card("FTO 候选", metrics["fto_candidates"], "复核优先队列"),
        metric_card("来源 URL", metrics["source_urls"], "目录去重快照"),
    ]
    steps = [
        ("01", "抽取", "01-extraction-report.md"), ("02", "族地图", "02-patent-family-map-report.md"),
        ("03", "技术路线", "03-technology-roadmap-report.md"), ("04", "风险 / FTO", "04-risk-and-fto-report.md"),
        ("05", "创新空间", "05-innovation-space-report.md"), ("06", "证据链", "06-evidence-chain-report.md"),
        ("07", "来源目录", "07-source-catalog-report.md"),
    ]
    step_html = "".join(f'<a class="step" href="{href}"><span>{num}</span><b>{label}</b></a>' for num, label, href in steps)
    sections = [
        ("核心布局", ["family-theme", "priority-year", "applicant", "jurisdiction"]),
        ("权利要求与路线", ["claim-category", "status", "search-round"]),
        ("FTO、证据与来源", ["risk-priority", "evidence-confidence", "evidence-type", "source-kind"]),
    ]
    chart_html = []
    for section_title, ids in sections:
        chart_html.append(f'<section class="section"><div class="section-title"><h2>{html.escape(section_title)}</h2><span>数据驱动 · 可回溯</span></div><div class="chart-grid">')
        for chart_id in ids:
            chart = chart_map.get(chart_id)
            if not chart:
                continue
            svg = bar_svg(chart["title"], chart["values"], note=chart["metric_definition"])
            chart_html.append(f'<article class="chart-card">{svg}<div class="chart-note">口径：{html.escape(chart["metric_definition"])}</div></article>')
        chart_html.append("</div></section>")
    generated = manifest["generated_at"]
    return f'''<!doctype html>
<html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{html.escape(title)}</title>
<style>
:root {{ --blue:#1264d9; --blue2:#eaf4ff; --ink:#17233b; --muted:#71809a; --line:#dce6f2; --bg:#f5f8fc; }}
* {{ box-sizing:border-box; }} body {{ margin:0; color:var(--ink); background:var(--bg); font-family:-apple-system,BlinkMacSystemFont,"Segoe UI","PingFang SC","Microsoft YaHei",sans-serif; }}
.page {{ max-width:1480px; margin:0 auto; padding:34px 40px 60px; }}
.hero {{ background:linear-gradient(135deg,#f8fbff,#eaf4ff); border:1px solid #d4e6fb; border-radius:22px; padding:30px 34px 26px; box-shadow:0 8px 24px rgba(18,100,217,.06); }}
.eyebrow {{ color:var(--blue); font-weight:700; letter-spacing:.08em; font-size:13px; }} h1 {{ margin:10px 0 8px; font-size:32px; }} .hero p {{ margin:0; color:var(--muted); line-height:1.7; }}
.metrics {{ display:grid; grid-template-columns:repeat(5,minmax(0,1fr)); gap:14px; margin:20px 0; }} .metric {{ background:#fff; border:1px solid var(--line); border-radius:16px; padding:18px; }} .metric-value {{ color:var(--blue); font-size:27px; font-weight:800; }} .metric-label {{ margin-top:5px; font-size:14px; font-weight:700; }} .metric-hint {{ margin-top:7px; color:var(--muted); font-size:12px; }}
.steps {{ display:flex; flex-wrap:wrap; gap:10px; margin:18px 0 26px; }} .step {{ display:flex; align-items:center; gap:9px; color:var(--ink); text-decoration:none; background:#fff; border:1px solid var(--line); border-radius:999px; padding:8px 14px 8px 9px; }} .step span {{ width:27px; height:27px; display:grid; place-items:center; border-radius:50%; color:#fff; background:var(--blue); font-size:11px; font-weight:800; }} .step:hover {{ border-color:var(--blue); color:var(--blue); }}
.section {{ margin:26px 0; }} .section-title {{ display:flex; justify-content:space-between; align-items:baseline; margin:0 2px 12px; }} .section-title h2 {{ margin:0; font-size:22px; }} .section-title span {{ color:var(--muted); font-size:12px; }} .chart-grid {{ display:grid; grid-template-columns:repeat(2,minmax(0,1fr)); gap:16px; }} .chart-card {{ background:#fff; border:1px solid var(--line); border-radius:18px; padding:14px; box-shadow:0 4px 14px rgba(25,63,115,.04); }} .chart-card svg {{ display:block; width:100%; height:auto; }} .chart-note {{ border-top:1px solid #edf1f7; padding:10px 12px 3px; color:var(--muted); font-size:12px; line-height:1.6; }}
.footer {{ margin-top:30px; padding:18px 20px; background:#fff; border:1px solid var(--line); border-radius:16px; color:var(--muted); font-size:12px; line-height:1.7; }} .footer a {{ color:var(--blue); }}
@media (max-width:900px) {{ .page {{ padding:20px 16px 40px; }} .metrics {{ grid-template-columns:repeat(2,minmax(0,1fr)); }} .chart-grid {{ grid-template-columns:1fr; }} h1 {{ font-size:25px; }} }}
</style></head><body><main class="page">
<header class="hero"><div class="eyebrow">MEDTECH PATENT ROADMAP · FTO-STYLE VISUAL REPORT</div><h1>{html.escape(title)}</h1><p>案例范围：{html.escape(obj.get('molecule', '未指定'))} · {html.escape(obj.get('target', '未指定'))} · {html.escape(obj.get('indication', '未指定'))}<br>生成时间：{html.escape(generated)} · 图表均由案例结构化数据自动生成。</p></header>
<div class="metrics">{"".join(cards)}</div><nav class="steps">{step_html}</nav>
{"".join(chart_html)}
<div class="footer">口径提示：统计图用于导航、比较和复核排序，不等同于权利要求覆盖、法律有效性或侵权概率。<br>交付入口：<a href="report-index.md">模块化报告索引</a> · <a href="04-risk-and-fto-report.md">风险 / FTO 报告</a> · <a href="visuals/manifest.json">图表数据清单</a></div>
</main></body></html>'''


def build_visuals(project):
    project = Path(project).expanduser().resolve()
    scope = load_json(project / "research_scope.json")
    families, claims, evidence, ranking, plan, catalog, source_log, chart_defs, metrics = build_dataset(project)
    visuals_dir = project / "visuals"
    visuals_dir.mkdir(parents=True, exist_ok=True)
    generated = datetime.now(timezone.utc).isoformat()
    manifest = {
        "schema_version": "1.0",
        "case": project.name,
        "generated_at": generated,
        "metrics": metrics,
        "charts": [],
        "limitations": [
            "统计单位依图表说明而异：族图通常按 family_id，claim 图按要素记录，证据图按 evidence.csv 条目。",
            "状态图是文本信号分类，必须回到目标法域官方登记簿核验。",
            "来源图是 CNIPA/PatentDatabases 目录快照，不等于本案已访问结果集。",
        ],
    }
    for index, chart in enumerate(chart_defs):
        svg_name = f"{chart['id']}-distribution.svg"
        svg_path = visuals_dir / svg_name
        svg_path.write_text(bar_svg(chart["title"], chart["values"], color_index=index, note=chart["metric_definition"]), encoding="utf-8")
        manifest["charts"].append({
            "id": chart["id"], "title": chart["title"], "filename": svg_name,
            "metric_definition": chart["metric_definition"], "source_fields": chart["source_fields"],
            "values": [[str(k), int(v)] for k, v in chart["values"]],
        })
    (visuals_dir / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (project / "report-visuals.html").write_text(build_html(project, chart_defs, metrics, scope, manifest), encoding="utf-8")
    return manifest


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-dir", required=True)
    args = parser.parse_args()
    project = Path(args.project_dir).expanduser().resolve()
    manifest = build_visuals(project)
    print(f"Generated {project / 'report-visuals.html'}")
    print(f"Generated {len(manifest['charts'])} SVG charts under {project / 'visuals'}")
    print(json.dumps({"case": project.name, "chart_count": len(manifest["charts"]), "metrics": manifest["metrics"]}, ensure_ascii=False))


if __name__ == "__main__":
    main()
