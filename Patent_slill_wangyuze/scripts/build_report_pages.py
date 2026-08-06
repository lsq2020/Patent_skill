#!/usr/bin/env python3
"""Render the modular Markdown reports as FTO-style standalone HTML pages."""

import argparse
import html
import json
import re
from pathlib import Path


REPORTS = [
    ("00-executive-summary", "执行摘要"),
    ("01-extraction-report", "权利要求与要素抽取"),
    ("02-patent-family-map-report", "专利族地图"),
    ("03-technology-roadmap-report", "技术路线图"),
    ("04-risk-and-fto-report", "风险 / FTO"),
    ("05-innovation-space-report", "创新空间假设"),
    ("06-evidence-chain-report", "证据链"),
    ("07-source-catalog-report", "来源目录"),
]


def load_json(path, default=None):
    if not path.exists():
        return default if default is not None else {}
    return json.loads(path.read_text(encoding="utf-8"))


def inline(text):
    text = html.escape(text, quote=False)
    text = re.sub(r"`([^`]+)`", r"<code>\1</code>", text)
    text = re.sub(r"!\[([^]]*)\]\(([^)]+)\)", r'<img src="\2" alt="\1">', text)
    text = re.sub(r"\[([^]]+)\]\(([^)]+)\)", r'<a href="\2">\1</a>', text)
    text = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", text)
    return text


def table_html(lines):
    rows = []
    for line in lines:
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if all(re.fullmatch(r":?-{3,}:?", cell) for cell in cells):
            continue
        rows.append(cells)
    if not rows:
        return ""
    head, body = rows[0], rows[1:]
    out = ["<table><thead><tr>"]
    out.extend(f"<th>{inline(cell)}</th>" for cell in head)
    out.append("</tr></thead><tbody>")
    for row in body:
        out.append("<tr>")
        out.extend(f"<td>{inline(cell)}</td>" for cell in row)
        out.append("</tr>")
    out.append("</tbody></table>")
    return "".join(out)


def markdown_html(text):
    lines = text.splitlines()
    out = []
    i = 0
    paragraph = []
    in_list = False

    def flush_paragraph():
        nonlocal paragraph
        if paragraph:
            out.append(f"<p>{inline(' '.join(paragraph))}</p>")
            paragraph = []

    def close_list():
        nonlocal in_list
        if in_list:
            out.append("</ul>")
            in_list = False

    while i < len(lines):
        line = lines[i]
        if not line.strip():
            flush_paragraph()
            close_list()
            i += 1
            continue
        if line.startswith("```"):
            flush_paragraph()
            close_list()
            code = []
            i += 1
            while i < len(lines) and not lines[i].startswith("```"):
                code.append(lines[i])
                i += 1
            out.append(f'<pre class="code">{html.escape(chr(10).join(code))}</pre>')
            i += 1
            continue
        heading = re.match(r"^(#{1,4})\s+(.*)$", line)
        if heading:
            flush_paragraph()
            close_list()
            level = min(4, len(heading.group(1)) + 1)
            out.append(f"<h{level}>{inline(heading.group(2))}</h{level}>")
            i += 1
            continue
        if line.startswith("| ") and i + 1 < len(lines) and lines[i + 1].lstrip().startswith("|---"):
            flush_paragraph()
            close_list()
            table_lines = [line]
            i += 1
            while i < len(lines) and lines[i].startswith("|"):
                table_lines.append(lines[i])
                i += 1
            out.append(table_html(table_lines))
            continue
        bullet = re.match(r"^\s*-\s+(.*)$", line)
        if bullet:
            flush_paragraph()
            if not in_list:
                out.append("<ul>")
                in_list = True
            out.append(f"<li>{inline(bullet.group(1))}</li>")
            i += 1
            continue
        if line.startswith(">"):
            flush_paragraph()
            close_list()
            out.append(f"<blockquote>{inline(line[1:].strip())}</blockquote>")
            i += 1
            continue
        if line.startswith("!["):
            flush_paragraph()
            close_list()
            out.append(f'<div class="figure">{inline(line)}</div>')
            i += 1
            continue
        paragraph.append(line)
        i += 1
    flush_paragraph()
    close_list()
    return "\n".join(out)


def metric(value, label, hint):
    return f'<div class="metric"><b>{html.escape(str(value))}</b><span>{html.escape(label)}</span><small>{html.escape(hint)}</small></div>'


def css():
    return """
:root{--blue:#1264d9;--ink:#17233b;--muted:#71809a;--line:#dce6f2;--bg:#f5f8fc;--panel:#fff}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);font-family:-apple-system,BlinkMacSystemFont,"Segoe UI","PingFang SC","Microsoft YaHei",sans-serif}.layout{display:grid;grid-template-columns:250px minmax(0,1fr);min-height:100vh}.side{padding:26px 16px;background:#fff;border-right:1px solid var(--line);position:sticky;top:0;height:100vh}.brand{color:var(--blue);font-size:13px;font-weight:800;letter-spacing:.07em;margin:4px 10px 24px}.side h3{font-size:13px;color:var(--muted);margin:18px 10px 10px}.side a{display:flex;align-items:center;gap:9px;color:var(--ink);text-decoration:none;padding:10px;border-radius:10px;font-size:13px}.side a:hover,.side a.active{background:#eaf4ff;color:var(--blue);font-weight:700}.side i{font-style:normal;color:var(--blue);font-size:11px;font-weight:800;width:22px}.main{max-width:1220px;width:100%;padding:30px 42px 56px;margin:0 auto}.hero{background:linear-gradient(135deg,#f8fbff,#eaf4ff);border:1px solid #d4e6fb;border-radius:20px;padding:26px 30px;margin-bottom:18px}.eyebrow{color:var(--blue);font-size:12px;font-weight:800;letter-spacing:.08em}.hero h1{margin:9px 0 7px;font-size:29px}.hero p{margin:0;color:var(--muted);line-height:1.7}.metrics{display:grid;grid-template-columns:repeat(5,minmax(0,1fr));gap:12px;margin:18px 0}.metric{background:var(--panel);border:1px solid var(--line);border-radius:14px;padding:14px}.metric b{display:block;color:var(--blue);font-size:23px}.metric span{display:block;margin-top:5px;font-size:13px;font-weight:700}.metric small{display:block;color:var(--muted);margin-top:5px;font-size:11px}.notice{background:#fff8e8;border:1px solid #f4d993;border-radius:12px;padding:13px 16px;color:#71531b;font-size:12px;line-height:1.7;margin:18px 0}.report-card{background:#fff;border:1px solid var(--line);border-radius:18px;padding:28px 32px;box-shadow:0 6px 20px rgba(25,63,115,.04)}.report-card h2{font-size:22px;border-bottom:1px solid #edf1f7;padding-bottom:10px;margin:24px 0 13px}.report-card h3{font-size:17px;margin:22px 0 10px;color:#233754}.report-card p,.report-card li{line-height:1.75;font-size:14px}.report-card a{color:var(--blue)}.report-card code{background:#edf2fa;border-radius:5px;padding:1px 4px;font-size:12px}.report-card blockquote{margin:12px 0;padding:11px 15px;background:#f6f9fd;border-left:3px solid #8cc5f2;color:var(--muted)}.report-card table{width:100%;border-collapse:collapse;display:block;overflow:auto;margin:12px 0 18px;font-size:12px}.report-card th,.report-card td{border:1px solid var(--line);padding:8px 9px;text-align:left;vertical-align:top;min-width:90px}.report-card th{background:#f5f8fc;color:#44536c}.report-card img{max-width:100%;height:auto;border:1px solid #edf1f7;border-radius:12px}.figure{margin:15px 0}.code{white-space:pre-wrap;background:#f5f8fc;border:1px solid var(--line);border-radius:10px;padding:14px;overflow:auto;font-size:12px}.index-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:14px}.index-card{display:block;color:var(--ink);text-decoration:none;background:#fff;border:1px solid var(--line);border-radius:14px;padding:16px}.index-card:hover{border-color:var(--blue);box-shadow:0 4px 14px rgba(18,100,217,.1)}.index-card b{display:block;font-size:16px}.index-card span{display:block;color:var(--muted);margin-top:7px;font-size:12px}.footer{color:var(--muted);font-size:12px;margin-top:18px;line-height:1.7}@media(max-width:900px){.layout{display:block}.side{position:static;height:auto;border-right:0;border-bottom:1px solid var(--line)}.side nav{display:flex;flex-wrap:wrap;gap:4px}.main{padding:20px 14px 40px}.metrics{grid-template-columns:repeat(2,minmax(0,1fr))}.report-card{padding:20px 16px}.index-grid{grid-template-columns:1fr}}
"""


def shell(project, current, body, scope, manifest, is_index=False):
    obj = scope.get("research_object", {})
    case_title = obj.get("molecule", project.name)
    metrics = manifest.get("metrics", {})
    links = []
    for idx, (stem, label) in enumerate(REPORTS, 1):
        links.append(f'<a class="{"active" if stem == current else ""}" href="{stem}.html"><i>{idx:02d}</i>{html.escape(label)}</a>')
    links.append('<a href="report-visuals.html"><i>V</i>统计总览</a>')
    title = "模块化报告索引" if is_index else next((label for stem, label in REPORTS if stem == current), current)
    return f'''<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{html.escape(case_title)} · {html.escape(title)}</title><style>{css()}</style></head><body><div class="layout"><aside class="side"><div class="brand">MEDTECH PATENT ROADMAP</div><h3>模块报告</h3><nav>{"".join(links)}</nav><h3>案例</h3><a href="report-visuals.html"><i>↗</i>FTO 风格统计看板</a><a href="report-index.md"><i>MD</i>Markdown 索引</a></aside><main class="main"><header class="hero"><div class="eyebrow">FTO-STYLE MODULAR REPORT</div><h1>{html.escape(case_title)} · {html.escape(title)}</h1><p>研究对象：{html.escape(case_title)} · 靶点：{html.escape(obj.get('target','未指定'))} · 适应症：{html.escape(obj.get('indication','未指定'))}<br>统计口径和图表均来自案例结构化数据；本报告为研究资料，不构成法律意见。</p></header><div class="metrics">{metric(metrics.get('families','—'),'专利族','family_id')}{metric(metrics.get('claims','—'),'claim 要素','逐条记录')}{metric(metrics.get('evidence','—'),'证据条目','可回溯链条')}{metric(metrics.get('fto_candidates','—'),'FTO 候选','复核优先队列')}{metric(metrics.get('source_urls','—'),'来源 URL','目录快照')}</div><div class="notice">状态信号、族关系、FTO 排序和统计图用于复核导航。进入许可、开发或诉讼决策前，仍需核对目标法域官方文本、完整独立权利要求、审查档案及法律事件。</div><article class="report-card">{body}</article><div class="footer">生成目录：<a href="report-visuals.html">统计总览</a> · <a href="visuals/manifest.json">图表数据清单</a> · <a href="report-index.md">Markdown 版本</a></div></main></div></body></html>'''


def build_pages(project):
    project = Path(project).expanduser().resolve()
    scope = load_json(project / "research_scope.json")
    manifest = load_json(project / "visuals" / "manifest.json", {})
    generated = {}
    for stem, label in REPORTS:
        md_path = project / f"{stem}.md"
        if not md_path.exists():
            continue
        html_path = project / f"{stem}.html"
        html_path.write_text(shell(project, stem, markdown_html(md_path.read_text(encoding="utf-8")), scope, manifest), encoding="utf-8")
        generated[html_path.name] = str(html_path)
    cards = []
    for stem, label in REPORTS:
        cards.append(f'<a class="index-card" href="{stem}.html"><b>{html.escape(label)}</b><span>打开 FTO 风格独立页面 · Markdown：{stem}.md</span></a>')
    index_body = '<h2>模块化交付</h2><p>每个模块均有独立页面、Markdown 正文和对应统计图；风险/FTO、技术路线、创新空间和证据链保留各自的研究边界。</p><div class="index-grid">' + "".join(cards) + '</div><h2>统计入口</h2><p><a href="report-visuals.html">打开交互式统计总览</a>，查看族主题、优先权、法域、claim 类别、FTO 优先级、证据和来源角色等图表。</p><p><a href="public-source-search-report.md">公开来源访问与检索审计</a>，查看目录 URL 的逐来源访问状态和检索端点。</p><p><a href="public-source-search-results-report.md">公开来源实际检索执行</a>，查看已提交查询、浏览器人工入口和未映射来源的执行台账。</p>'
    index_path = project / "report-index.html"
    index_path.write_text(shell(project, "", index_body, scope, manifest, is_index=True), encoding="utf-8")
    generated[index_path.name] = str(index_path)
    return generated


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-dir", required=True)
    args = parser.parse_args()
    outputs = build_pages(Path(args.project_dir))
    print(json.dumps({"page_count": len(outputs), "files": sorted(outputs)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
