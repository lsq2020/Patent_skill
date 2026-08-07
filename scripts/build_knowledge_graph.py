#!/usr/bin/env python3
"""Build a standalone offline Cytoscape.js patent evidence graph page."""

import argparse
import html
import json
from pathlib import Path


CYTOSCAPE_VERSION = "3.34.0"


def script_json(value):
    return (
        json.dumps(value, ensure_ascii=False, separators=(",", ":"))
        .replace("</", "<\\/")
        .replace("\u2028", "\\u2028")
        .replace("\u2029", "\\u2029")
    )


def load_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def build_knowledge_graph(
    project,
    graph_path=None,
    quality_path=None,
    output_path=None,
):
    project = Path(project).expanduser().resolve()
    graph_path = Path(graph_path or project / "graph-data.json").resolve()
    quality_path = Path(quality_path or project / "graph-quality.json").resolve()
    output_path = Path(output_path or project / "knowledge-graph.html").resolve()
    skill_root = Path(__file__).resolve().parents[1]
    asset_root = skill_root / "assets" / "graph-viewer"
    vendor_path = asset_root / "cytoscape.min.js"
    css_path = asset_root / "graph-viewer.css"
    js_path = asset_root / "graph-viewer.js"
    required = [graph_path, quality_path, vendor_path, css_path, js_path]
    missing = [str(path) for path in required if not path.exists()]
    if missing:
        raise FileNotFoundError(f"missing knowledge-graph inputs: {', '.join(missing)}")

    graph = load_json(graph_path)
    quality = load_json(quality_path)
    title = graph.get("meta", {}).get("title") or project.name
    css = css_path.read_text(encoding="utf-8")
    vendor = vendor_path.read_text(encoding="utf-8")
    app_js = js_path.read_text(encoding="utf-8")
    document = f'''<!doctype html>
<html lang="zh-CN" data-cytoscape-version="{CYTOSCAPE_VERSION}">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <meta name="color-scheme" content="light">
  <title>{html.escape(title)} · 专利证据双链图</title>
  <style>{css}</style>
</head>
<body>
  <a class="skip-link" href="#graph-canvas">跳到关系图</a>
  <header class="appbar">
    <div class="brand">
      <span class="brand-kicker">Patent Evidence Graph</span>
      <span class="brand-title">{html.escape(title)} · 专利证据双链图</span>
    </div>
    <div class="search-wrap">
      <label for="graph-search" class="brand-kicker">搜索节点</label>
      <input id="graph-search" type="search" autocomplete="off" placeholder="搜索 family_id、claim、申请人、技术主题或 finding…">
      <span class="search-key" aria-hidden="true">Ctrl K</span>
      <div id="search-results" class="search-results" role="listbox" hidden></div>
    </div>
    <div class="app-actions">
      <label for="view-preset" class="brand-kicker">视图</label>
      <select id="view-preset" aria-label="图谱视图"></select>
      <label for="depth-control" class="brand-kicker">深度</label>
      <select id="depth-control" aria-label="关系展开深度">
        <option value="1">1 跳</option>
        <option value="2">2 跳</option>
        <option value="3">3 跳</option>
      </select>
      <button id="reset-button" type="button">重置</button>
      <button id="export-button" type="button">导出当前图</button>
    </div>
  </header>

  <div class="workspace">
    <aside class="filter-panel" aria-label="图谱筛选器">
      <div class="panel-heading"><h2>数据与筛选</h2><button id="select-all-nodes" class="small-button" type="button">全部类型</button></div>
      <div class="summary-strip">
        <div class="summary-stat"><b id="total-node-count">—</b><span>全部节点</span></div>
        <div class="summary-stat"><b id="total-edge-count">—</b><span>全部关系</span></div>
      </div>
      <div id="quality-banner" class="quality-banner" role="status" aria-live="polite"></div>
      <section class="filter-section">
        <h3>节点类型</h3>
        <div id="node-type-filters" class="filter-list"></div>
      </section>
      <section class="filter-section">
        <h3>关系类型</h3>
        <div id="relation-type-filters" class="filter-list"></div>
      </section>
      <section class="filter-section">
        <h3>节点图例</h3>
        <div id="node-legend"></div>
      </section>
      <section class="filter-section">
        <h3>边的证据口径</h3>
        <div id="edge-legend"></div>
      </section>
    </aside>

    <main id="main-content" class="graph-panel">
      <div class="canvas-toolbar">
        <div class="canvas-meta"><span id="visible-count">加载图谱…</span></div>
        <div class="canvas-tools">
          <button id="layout-button" type="button">重新布局</button>
          <button id="fit-button" type="button">适合窗口</button>
        </div>
      </div>
      <div id="graph-canvas" class="graph-canvas" role="img" aria-label="专利证据关系图" tabindex="0"></div>
      <div id="empty-state" class="empty-state" hidden>
        <h2>当前筛选没有节点</h2>
        <p>清空搜索词、恢复节点类型或切换预设视图。</p>
      </div>
      <div id="limit-banner" class="limit-banner" role="status" hidden></div>
      <div id="graph-status" class="skip-link" aria-live="polite"></div>
    </main>

    <aside class="inspector-panel" aria-label="节点检查器">
      <span id="inspector-type" class="inspector-type">未选择</span>
      <h2 id="inspector-title" class="inspector-title">选择一个节点</h2>
      <p id="inspector-id" class="inspector-id">点击图中节点查看双向链接</p>
      <div id="inspector-tabs" class="inspector-tabs" role="tablist" aria-label="节点详情">
        <button type="button" role="tab" data-tab="overview" aria-selected="true">摘要</button>
        <button type="button" role="tab" data-tab="claims" aria-selected="false">Claims</button>
        <button type="button" role="tab" data-tab="evidence" aria-selected="false">证据</button>
        <button type="button" role="tab" data-tab="outgoing" aria-selected="false">出链</button>
        <button type="button" role="tab" data-tab="backlinks" aria-selected="false">反向链接</button>
      </div>
      <div id="inspector-content" class="inspector-content" role="tabpanel"></div>
    </aside>
  </div>

  <section class="relation-ledger" aria-labelledby="relation-ledger-title">
    <div class="ledger-head">
      <div><h2 id="relation-ledger-title">当前可见关系</h2><p>边只存一次；反向链接由入边动态计算。最多显示 200 条。</p></div>
      <a href="graph-data.json">打开机器可读图数据</a>
    </div>
    <div class="table-scroll">
      <table class="relation-table">
        <thead><tr><th>源节点</th><th>关系</th><th>目标节点</th><th>口径</th><th>finding_id</th></tr></thead>
        <tbody id="relation-table-body"></tbody>
      </table>
    </div>
  </section>
  <footer class="page-footer">
    <a href="report-index.html">返回模块化报告</a> · <a href="graph-quality.json">图谱质量报告</a> · <a href="case-output.json">case-output.json</a><br>
    关系图用于检索、证据回溯和复核导航，不以节点颜色或距离表达法律有效性、侵权概率或科学确定性。Cytoscape.js {CYTOSCAPE_VERSION}（MIT）已内嵌，可离线打开。
  </footer>
  <script>window.PATENT_GRAPH_DATA={script_json(graph)};window.PATENT_GRAPH_QUALITY={script_json(quality)};</script>
  <script>{vendor}</script>
  <script>{app_js}</script>
</body>
</html>
'''
    output_path.write_text(document, encoding="utf-8")
    return output_path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-dir", required=True)
    parser.add_argument("--graph")
    parser.add_argument("--quality")
    parser.add_argument("--output")
    args = parser.parse_args()
    output = build_knowledge_graph(
        args.project_dir,
        graph_path=args.graph,
        quality_path=args.quality,
        output_path=args.output,
    )
    print(json.dumps({"output": str(output), "cytoscape_version": CYTOSCAPE_VERSION}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
