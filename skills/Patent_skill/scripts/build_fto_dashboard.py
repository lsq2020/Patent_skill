#!/usr/bin/env python3
"""Render the FTO plan and candidate ranking as a dependency-free HTML dashboard."""

import argparse
import csv
import json
from html import escape
from pathlib import Path


def load_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def load_csv(path):
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8-sig") as handle:
        return [{str(k).strip(): (v or "").strip() for k, v in row.items()} for row in csv.DictReader(handle)]


def cell(value):
    return escape(str(value or "—"))


def render(plan, candidates):
    summary = plan.get("stage_summary", {})
    feature_counts = summary.get("feature_counts", {})
    feature_count = summary.get("feature_count", len(plan.get("features", [])))
    keyword_count = summary.get("keyword_term_count", 0)
    class_count = summary.get("classification_count", 0)
    source_catalog = plan.get("source_catalog", {})
    source_counts = source_catalog.get("counts", {})
    source_count = source_counts.get("unique_urls", len(source_catalog.get("sources", [])))
    candidate_count = len(candidates)
    comparison_count = sum(1 for row in candidates if row.get("matched_features"))
    steps = [
        ("1", "技术方案与技术特征", f"{feature_count} 个特征", "done"),
        ("2", "扩展关键词", f"{keyword_count} 个词", "done"),
        ("3", "构建防侵权检索策略", f"{len(plan.get('search_rounds', []))} 轮检索", "done"),
        ("4", "专利初筛", f"{candidate_count} 个候选族", "done" if candidate_count else "todo"),
        ("5", "比对技术特征", f"{comparison_count} 个待复核", "done" if comparison_count else "todo"),
    ]
    step_html = "".join(f'<div class="step {status}"><div class="circle">{num}</div><div><strong>{escape(title)}</strong><span>{escape(subtitle)}</span></div></div>' for num, title, subtitle, status in steps)
    feature_rows = "".join(f'<tr><td><b>{cell(f["id"])}</b></td><td>{cell(f.get("feature_type"))}</td><td><span class="tag {cell(f.get("importance"))}">{cell(f.get("importance"))}</span></td><td>{cell(f.get("text"))}</td><td>{cell(", ".join(f.get("classifications", [])))}</td></tr>' for f in plan.get("features", []))
    keyword_html = "".join(f'<div class="keyword-card"><h4>{cell(c.get("label"))}</h4><div class="small">基础词</div><p>{" · ".join(cell(x) for x in c.get("base_terms", [])) or "—"}</p><div class="small">扩展词</div><p>{" · ".join(cell(x) for x in c.get("expanded_terms", [])) or "—"}</p></div>' for c in plan.get("keyword_expansion", []))
    class_html = "".join(f'<span class="class-chip">{cell(x)}</span>' for x in plan.get("classifications", [])) or '<span class="muted">未提供</span>'
    round_rows = "".join(f'<tr><td><b>{cell(r.get("id"))}</b><br><span class="muted">{cell(r.get("title"))}</span></td><td>{cell(r.get("objective"))}</td><td><code>{cell(r.get("formula"))}</code></td><td>{cell(r.get("status"))}</td></tr>' for r in plan.get("search_rounds", []))
    candidate_rows = "".join(f'<tr data-search="{cell(" ".join(row.values()))}"><td><b>{cell(row.get("family_id"))}</b></td><td>{cell(row.get("representative_document"))}</td><td><span class="priority {cell(row.get("review_priority"))}">{cell(row.get("review_priority"))}</span></td><td>{cell(row.get("screen_score"))}</td><td>{cell(row.get("matched_features"))}<br><span class="muted">部分命中：{cell(row.get("partial_features"))}</span></td><td>{cell(row.get("claim_categories"))}</td><td><a href="{cell(row.get("source_url"))}" target="_blank" rel="noreferrer">来源</a></td></tr>' for row in candidates) or '<tr><td colspan="7" class="muted">尚未导入 claim-elements.csv，暂不显示候选族。</td></tr>'
    source_rows = "".join(
        f'<tr data-search="{cell(source.get("name"))} {cell(source.get("url"))} {cell(source.get("source_kind"))}">'
        f'<td><b>{cell(source.get("source_id"))}</b></td><td>{cell(source.get("name"))}</td>'
        f'<td>{cell(source.get("source_kind"))}</td><td>{cell(source.get("default_use"))}</td>'
        f'<td><a href="{cell(source.get("url"))}" target="_blank" rel="noreferrer">打开来源</a></td></tr>'
        for source in source_catalog.get("sources", [])
    ) or '<tr><td colspan="5" class="muted">未加载来源目录。</td></tr>'
    stage_bars = "".join(f'<div class="bar-row"><span>{escape(label)}</span><div class="bar"><i style="width:{min(100, value * 100 / max(1, feature_count)):.0f}%"></i></div><b>{value}</b></div>' for label, value in [("核心", feature_counts.get("core", 0)), ("必要", feature_counts.get("necessary", 0)), ("支撑", feature_counts.get("support", 0)), ("背景", feature_counts.get("context", 0))])
    return f'''<!doctype html>
<html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>FTO防侵权检索 · {cell(plan.get("case"))}</title>
<style>
:root{{--blue:#1261d6;--ink:#182235;--muted:#71809a;--line:#e4eaf3;--bg:#f7f9fc;--soft:#eef5ff}}*{{box-sizing:border-box}}body{{margin:0;font-family:-apple-system,BlinkMacSystemFont,"Segoe UI","PingFang SC","Microsoft YaHei",sans-serif;color:var(--ink);background:var(--bg)}}header{{background:#fff;border-bottom:1px solid var(--line);padding:24px 36px;position:sticky;top:0;z-index:3}}header h1{{font-size:22px;margin:0 0 6px}}header p{{color:var(--muted);margin:0}}.layout{{display:grid;grid-template-columns:280px 1fr;min-height:calc(100vh - 90px)}}aside{{background:#fff;border-right:1px solid var(--line);padding:24px 18px}}.step{{display:flex;gap:13px;padding:16px 10px;border-radius:12px;margin-bottom:8px;align-items:flex-start}}.step.done{{background:#f6f9ff}}.step.todo{{opacity:.58}}.circle{{width:29px;height:29px;border-radius:50%;background:#dce8fb;color:var(--blue);font-weight:700;display:flex;align-items:center;justify-content:center;flex:0 0 auto}}.step.done .circle{{background:var(--blue);color:#fff}}.step strong,.step span{{display:block}}.step span{{font-size:12px;color:var(--muted);margin-top:4px}}main{{padding:30px;max-width:1500px;width:100%;margin:auto}}.hero,.panel{{background:#fff;border:1px solid var(--line);border-radius:16px;box-shadow:0 8px 24px #18223508;margin-bottom:22px}}.hero{{padding:24px 26px;background:linear-gradient(135deg,#fff,#f2f7ff)}}.hero h2{{margin:0 0 10px;font-size:20px}}.hero p{{line-height:1.7;margin:0;color:#4a5870}}.stats{{display:grid;grid-template-columns:repeat(5,1fr);gap:12px;margin-top:18px}}.stat{{background:#fff;border:1px solid var(--line);border-radius:12px;padding:14px}}.stat b{{font-size:25px;color:var(--blue);display:block}}.stat span{{font-size:12px;color:var(--muted)}}.panel h3{{font-size:18px;margin:0;padding:20px 22px;border-bottom:1px solid var(--line)}}.panel-body{{padding:20px 22px}}table{{border-collapse:collapse;width:100%;font-size:13px}}th{{background:#f6f8fb;text-align:left;color:#63718a;font-weight:600}}th,td{{padding:12px;border-bottom:1px solid var(--line);vertical-align:top;line-height:1.5}}.tag,.priority,.class-chip{{display:inline-block;border-radius:999px;padding:3px 9px;font-size:12px;background:#edf1f7;color:#4a5870}}.tag.core{{background:#e7f0ff;color:#0f5acb}}.tag.necessary{{background:#e9f7ef;color:#147543}}.tag.support{{background:#fff5df;color:#9a6400}}.keyword-grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:12px}}.keyword-card{{border:1px solid var(--line);border-radius:12px;padding:14px;background:#fbfcfe}}.keyword-card h4{{margin:0 0 10px}}.keyword-card p{{font-size:13px;line-height:1.7;margin:6px 0 12px;color:#3e4d65}}.small,.muted{{font-size:12px;color:var(--muted)}}.class-chip{{margin:4px;background:#eef5ff;color:#185fc7;border-radius:6px;font-family:ui-monospace,monospace}}code{{white-space:pre-wrap;word-break:break-word;color:#34435c}}.priority.HIGH{{background:#ffe7e7;color:#bd2929}}.priority.MEDIUM{{background:#fff3d9;color:#986000}}.priority.LOW{{background:#e9f6ee;color:#257144}}a{{color:var(--blue);text-decoration:none}}.toolbar{{display:flex;gap:10px;justify-content:space-between;align-items:center;margin-bottom:12px}}input{{border:1px solid var(--line);border-radius:9px;padding:10px 12px;min-width:280px}}.bar-row{{display:flex;gap:10px;align-items:center;margin:11px 0;font-size:13px}}.bar-row>span{{width:50px;color:#63718a}}.bar{{height:9px;background:#edf1f7;border-radius:9px;overflow:hidden;flex:1}}.bar i{{display:block;height:100%;background:linear-gradient(90deg,#1261d6,#75b5ff);border-radius:9px}}.bar-row b{{width:24px;text-align:right}}.notice{{border-left:4px solid #f1ad34;background:#fffaf0;padding:12px 14px;color:#6d572d;font-size:13px;line-height:1.6}}@media(max-width:900px){{.layout{{grid-template-columns:1fr}}aside{{position:static;border-right:0;border-bottom:1px solid var(--line)}}.stats{{grid-template-columns:repeat(2,1fr)}}main{{padding:16px}}header{{padding:18px}}table{{display:block;overflow-x:auto;white-space:nowrap}}}}
</style></head><body><header><h1>专利防侵权检索 · {cell(plan.get("case"))}</h1><p>技术特征工程、扩展检索式、候选族初筛与权利要求比对准备</p></header><div class="layout"><aside>{step_html}<div class="notice">当前页面展示的是可复核的检索准备与初筛结果，不构成法律意见。</div></aside><main>
<section class="hero"><h2>技术方案</h2><p>{cell(plan.get("technical_solution"))}</p><div class="stats"><div class="stat"><b>{feature_count}</b><span>技术特征</span></div><div class="stat"><b>{keyword_count}</b><span>扩展关键词</span></div><div class="stat"><b>{class_count}</b><span>IPC/CPC</span></div><div class="stat"><b>{len(plan.get("search_rounds", []))}</b><span>检索轮次</span></div><div class="stat"><b>{candidate_count}</b><span>候选专利族</span></div><div class="stat"><b>{source_count}</b><span>来源 URL</span></div></div></section>
<section class="panel"><h3>1. 技术方案与技术特征</h3><div class="panel-body"><table><thead><tr><th>ID</th><th>类型</th><th>重要性</th><th>技术特征</th><th>IPC/CPC</th></tr></thead><tbody>{feature_rows}</tbody></table><div style="margin-top:18px"><div class="small">特征分布</div>{stage_bars}</div></div></section>
<section class="panel"><h3>2. 扩展关键词</h3><div class="panel-body"><div class="keyword-grid">{keyword_html}</div></div></section>
<section class="panel"><h3>3. IPC/CPC 与分类号</h3><div class="panel-body">{class_html}<p class="muted">分类号用于提高召回和寻找邻近技术，必须回到权利要求核验。</p></div></section>
<section class="panel"><h3>4. 防侵权检索策略</h3><div class="panel-body"><table><thead><tr><th>轮次</th><th>目标</th><th>检索式</th><th>状态</th></tr></thead><tbody>{round_rows}</tbody></table></div></section>
<section class="panel"><h3>来源目录（CNIPA/PatentDatabases）</h3><div class="panel-body"><div class="notice">当前目录快照包含上游 {cell(source_counts.get("upstream_listings"))} 条记录、去重后 {cell(source_count)} 个 URL。来源目录用于选择检索入口；收费、旧链接、需注册或仅能显示著录项的来源，不能自动升级为官方法律状态证据。官方核验仍需回到目标法域登记簿。</div><p class="muted">上游仓库：<a href="{cell(source_catalog.get("upstream_repo"))}" target="_blank" rel="noreferrer">CNIPA/PatentDatabases</a></p><div class="toolbar"><span class="muted">完整来源清单（可按名称、URL 或来源角色筛选）</span><input id="source-filter" placeholder="筛选来源" oninput="filterSources()"></div><table><thead><tr><th>ID</th><th>来源</th><th>来源角色</th><th>默认用途</th><th>链接</th></tr></thead><tbody id="source-body">{source_rows}</tbody></table></div></section>
<section class="panel"><h3>5. 专利初筛与技术特征比对</h3><div class="panel-body"><div class="toolbar"><span class="muted">排序分数是透明筛选信号，不是侵权概率。</span><input id="filter" placeholder="筛选家族、文献、特征或类别" oninput="filterRows()"></div><table><thead><tr><th>专利族</th><th>代表文献</th><th>复核优先级</th><th>分数</th><th>命中特征</th><th>权利要求类别</th><th>来源</th></tr></thead><tbody id="candidate-body">{candidate_rows}</tbody></table></div></section>
<section class="panel"><h3>边界与待核验事项</h3><div class="panel-body"><ul>{''.join(f'<li>{cell(gap)}</li>' for gap in plan.get('gaps', []))}</ul></div></section>
</main></div><script>function filterRows(){{const q=document.getElementById('filter').value.toLowerCase();document.querySelectorAll('#candidate-body tr').forEach(r=>{{r.style.display=r.innerText.toLowerCase().includes(q)?'':'none'}})}}function filterSources(){{const q=document.getElementById('source-filter').value.toLowerCase();document.querySelectorAll('#source-body tr').forEach(r=>{{r.style.display=r.innerText.toLowerCase().includes(q)?'':'none'}})}}</script></body></html>'''


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-dir", required=True)
    parser.add_argument("--ranking", default="fto-candidate-ranking.csv")
    parser.add_argument("--output", default="fto-search.html")
    args = parser.parse_args()
    project = Path(args.project_dir).expanduser().resolve()
    plan = load_json(project / "fto-search-plan.json")
    candidates = load_csv(project / args.ranking)
    out = project / args.output
    out.write_text(render(plan, candidates), encoding="utf-8")
    print(f"Generated {out}")


if __name__ == "__main__":
    main()
