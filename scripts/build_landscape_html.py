#!/usr/bin/env python3
"""Build a reusable WIPO-style patent-landscape HTML from a family CSV."""

import argparse
import csv
import html
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _report_theme as theme


def _first(row, *keys):
    for key in keys:
        value = row.get(key, "")
        if value:
            return value.strip()
    return ""


def _split(value):
    return [x.strip() for x in value.replace(",", ";").split(";") if x.strip()]


def _theme(row):
    text = (row.get("claim_theme", "") + " " + row.get("claim_categories", "") + " " + row.get("notes", "")).lower()
    if any(x in text for x in ("resistance", "耐药", "mutation", "突变")):
        return "resistance"
    if any(x in text for x in ("formulation", "制剂", "tablet", "片剂")):
        return "formulation"
    if any(x in text for x in ("indication", "combination", "use", "用途", "联合")):
        return "indication"
    return "compound"


def _status(row):
    text = (" ".join(row.values())).lower()
    if any(x in text for x in ("watch", "观察", "target-country status not established", "status not established", "national-phase status not established")):
        return "watch"
    if any(x in text for x in ("pending", "公开申请", "审查中")):
        return "pending"
    if any(x in text for x in ("abandoned", "ceased", "expired", "withdrawn", "revoked", "放弃", "终止", "到期", "撤回")):
        return "watch"
    return "grant"


def load_families(path):
    families = []
    with path.open(newline="", encoding="utf-8") as f:
        for raw_row in csv.DictReader(f):
            row = {(key or "").strip(): (value or "") for key, value in raw_row.items()}
            family_id = _first(row, "family_id")
            if not family_id:
                continue
            families.append({
                "id": family_id,
                "doc": _first(row, "representative_document", "representative_publication"),
                "title": _first(row, "claim_theme", "notes") or "Patent family",
                "theme": _theme(row),
                "year": _first(row, "earliest_priority")[:4] or "?",
                "juris": _split(_first(row, "jurisdictions")),
                "status": _status(row),
                "applicant": _first(row, "applicant_or_assignee", "applicant"),
                "mutation": _first(row, "mutation_or_biomarker"),
                "status_note": _first(row, "status_screen_as_of", "official_status", "status_source"),
                "url": _first(row, "source_url"),
            })
    return families


def render(title, as_of, families):
    data = json.dumps(families, ensure_ascii=False).replace("</", "<\\/")
    title_safe = html.escape(title)
    asof_safe = html.escape(as_of)
    return f'''<!doctype html>
<html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title_safe}</title>
<style>
{theme.css_tokens()}
*{{box-sizing:border-box}}body{{margin:0;background:var(--bg);color:var(--ink);font:14px/1.55 -apple-system,BlinkMacSystemFont,"Segoe UI","PingFang SC","Microsoft YaHei",sans-serif}}
main{{max-width:1280px;margin:0 auto;padding:28px 22px 50px}}header{{display:flex;justify-content:space-between;gap:20px;margin-bottom:20px}}h1{{font-size:28px;margin:0 0 5px}}h2{{font-size:18px;margin:0 0 14px}}.muted{{color:var(--muted)}}.notice{{background:color-mix(in srgb,var(--warning) 14%,var(--surface));border:1px solid color-mix(in srgb,var(--warning) 45%,var(--surface));border-radius:10px;padding:11px 13px;color:#6d5000;margin-bottom:18px}}
.controls{{display:flex;flex-wrap:wrap;gap:10px;margin-bottom:18px}}label{{font-size:12px;color:var(--muted);display:flex;gap:6px;align-items:center}}select{{border:1px solid var(--line);border-radius:8px;padding:8px 10px;background:var(--surface);min-width:150px}}
.metrics{{display:grid;grid-template-columns:repeat(4,1fr);gap:12px;margin-bottom:18px}}.metric,.panel{{background:var(--surface);border:1px solid var(--line);border-radius:12px}}.metric{{padding:14px 16px}}.metric span{{display:block;color:var(--muted);font-size:12px}}.metric strong{{font-size:26px;color:var(--accent)}}
.grid{{display:grid;grid-template-columns:1.1fr .9fr;gap:16px}}.panel{{padding:17px;margin-bottom:16px}}.full{{grid-column:1/-1}}table{{width:100%;border-collapse:collapse}}th,td{{text-align:left;padding:9px 7px;border-bottom:1px solid var(--line);vertical-align:top}}th{{font-size:12px;color:var(--muted);font-weight:500}}a{{color:var(--accent);text-decoration:none}}.tag{{display:inline-block;background:var(--accent-soft);color:#174ea6;border-radius:999px;padding:2px 7px;font-size:11px;margin-right:4px}}.tag.teal{{background:color-mix(in srgb,var(--cat-3) 18%,var(--surface));color:#0a6b52}}.tag.amber{{background:color-mix(in srgb,var(--warning) 20%,var(--surface));color:#7a5600}}
.timeline{{display:grid;gap:9px}}.tr{{display:grid;grid-template-columns:62px 1fr;gap:10px;align-items:center}}.track{{display:flex;align-items:center;gap:8px;border-bottom:1px solid var(--line);min-height:28px}}.dot{{width:11px;height:11px;border-radius:50%;background:var(--accent);box-shadow:0 0 0 4px var(--accent-soft)}}.dot.resistance{{background:var(--cat-3);box-shadow:0 0 0 4px color-mix(in srgb,var(--cat-3) 18%,var(--surface))}}.dot.watch{{background:var(--warning);box-shadow:0 0 0 4px color-mix(in srgb,var(--warning) 20%,var(--surface))}}
.roadmap{{display:flex;align-items:center;gap:7px;flex-wrap:wrap}}.node{{background:var(--accent-soft);border:1px solid var(--seq-200);border-radius:9px;padding:9px;text-align:center}}.arrow{{font-size:20px;color:var(--muted)}}.foot{{font-size:12px;color:var(--muted);margin-top:10px}}@media(max-width:900px){{.grid{{grid-template-columns:1fr}}.metrics{{grid-template-columns:repeat(2,1fr)}}header{{display:block}}}}@media(max-width:560px){{main{{padding:18px 12px}}.family-table{{display:block;overflow-x:auto;white-space:nowrap}}}}
</style></head><body><main>
<header><div><h1>{title_safe}</h1><p class="muted">可复核专利族景观；支持按技术主题、法域和状态筛选。</p></div><div class="muted">案例快照<br>{asof_safe}</div></header>
<div class="notice">状态和风险为研究快照，不构成法律意见或 FTO 结论。来源应回到专利文本和目标法域官方登记簿复核。</div>
<div class="controls"><label>技术主题<select id="theme"><option value="all">全部</option><option value="compound">化合物</option><option value="formulation">制剂</option><option value="indication">适应症/联合</option><option value="resistance">耐药/突变</option></select></label><label>法域<select id="juris"><option value="all">全部</option><option value="CN">中国</option><option value="US">美国</option><option value="WO">国际/PCT</option><option value="EP">欧洲</option></select></label><label>状态<select id="status"><option value="all">全部</option><option value="grant">授权记录</option><option value="pending">公开/审查中</option><option value="watch">观察项</option></select></label></div>
<section class="metrics" id="metrics"></section>
<div class="grid"><section class="panel"><h2>优先权时间线</h2><div class="timeline" id="timeline"></div><p class="foot">同一专利族按 family_id 计数，不把国家成员重复计为独立创新。</p></section>
<section class="panel"><h2>通用技术路线</h2><div class="roadmap"><div class="node">疾病/未满足需求</div><div class="arrow">→</div><div class="node">靶点与机制</div><div class="arrow">→</div><div class="node">化合物/候选物</div><div class="arrow">→</div><div class="node">适应症/方案</div><div class="arrow">→</div><div class="node">耐药/下一代技术</div></div><p class="foot">每个节点应回溯到 family_id、claim 要素或上下文证据。</p></section>
<section class="panel full"><h2>专利族明细</h2><table class="family-table"><thead><tr><th>族</th><th>代表文献</th><th>技术主题</th><th>优先权</th><th>法域</th><th>状态</th><th>申请人</th></tr></thead><tbody id="families"></tbody></table></section></div>
</main><script>const data={data};const labels={{compound:'化合物',formulation:'制剂',indication:'适应症/联合',resistance:'耐药/突变'}};const statuses={{grant:'授权记录',pending:'公开/审查中',watch:'观察项'}};const q=id=>document.getElementById(id);function filtered(){{const t=q('theme').value,j=q('juris').value,s=q('status').value;return data.filter(x=>(t==='all'||x.theme===t)&&(j==='all'||x.juris.includes(j))&&(s==='all'||x.status===s))}}function render(){{const rows=filtered(),res=rows.filter(x=>x.theme==='resistance').length,gr=rows.filter(x=>x.status==='grant').length,js=[...new Set(rows.flatMap(x=>x.juris))].length;q('metrics').innerHTML=[['可见专利族',rows.length],['授权记录',gr],['耐药/突变族',res],['覆盖法域',js]].map(x=>`<div class="metric"><span>${{x[0]}}</span><strong>${{x[1]}}</strong></div>`).join('');q('families').innerHTML=rows.map(x=>`<tr><td><strong>${{x.id}}</strong></td><td><a href="${{x.url||'#'}}" target="_blank" rel="noreferrer">${{x.doc||'—'}}</a></td><td><span class="tag ${{x.theme==='resistance'?'teal':x.theme==='watch'?'amber':''}}">${{labels[x.theme]||x.theme}}</span><br>${{x.title}}</td><td>${{x.year}}</td><td>${{x.juris.join(' / ')||'—'}}</td><td>${{statuses[x.status]||x.status}}<br><span class="muted">${{x.status_note||''}}</span></td><td>${{x.applicant||'—'}}</td></tr>`).join('')||'<tr><td colspan="7">当前筛选条件没有匹配族。</td></tr>';q('timeline').innerHTML=[...rows].sort((a,b)=>Number(a.year)-Number(b.year)).map(x=>`<div class="tr"><span class="muted">${{x.year}}</span><div class="track"><span class="dot ${{x.theme==='resistance'?'resistance':x.status==='watch'?'watch':''}}"></span><span><strong>${{x.id}}</strong> ${{x.title}} <span class="muted">${{x.applicant||''}}</span></span></div></div>`).join('')||'<p class="muted">当前筛选条件没有匹配事件。</p>'}}['theme','juris','status'].forEach(id=>q(id).addEventListener('change',render));render();</script></body></html>'''


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--families", required=True)
    p.add_argument("--output", required=True)
    p.add_argument("--title", required=True)
    p.add_argument("--as-of", required=True)
    args = p.parse_args()
    families = load_families(Path(args.families).expanduser().resolve())
    out = Path(args.output).expanduser().resolve()
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(render(args.title, args.as_of, families), encoding="utf-8")
    print(f"Generated {out} from {len(families)} patent families")


if __name__ == "__main__":
    main()
