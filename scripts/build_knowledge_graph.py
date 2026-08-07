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
<html lang="zh-CN" data-theme="dark" data-cytoscape-version="{CYTOSCAPE_VERSION}">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <meta name="color-scheme" content="dark">
  <title>{html.escape(title)} · 专利证据双链图</title>
  <script>
    if (new URLSearchParams(window.location.search).get("embed") === "report") {{
      document.documentElement.dataset.embed = "report";
    }}
  </script>
  <style>{css}</style>
</head>
<body>
  <a class="skip-link" href="#graph-canvas">跳到关系图</a>
  <header class="app-header">
    <div class="appbar">
      <div class="brand">
        <span class="brand-mark" aria-hidden="true">PE</span>
        <div class="brand-copy">
          <span class="brand-kicker">Patent Evidence Graph</span>
          <span class="brand-title">{html.escape(title)} · 专利证据双链图</span>
        </div>
      </div>
      <div class="search-wrap">
        <label for="graph-search" class="sr-only">搜索节点</label>
        <span class="search-icon" aria-hidden="true"></span>
        <input id="graph-search" type="search" autocomplete="off" placeholder="搜索 family_id、claim、申请人、技术主题或 finding…">
        <span class="search-key" aria-hidden="true">Ctrl K</span>
        <div id="search-results" class="search-results" role="listbox" hidden></div>
      </div>
      <div class="app-actions">
        <div class="control-field">
          <label for="view-preset">分析视图</label>
          <select id="view-preset" aria-label="图谱视图"></select>
        </div>
        <div class="control-field control-field-compact">
          <label for="depth-control">展开范围</label>
          <select id="depth-control" aria-label="关系展开深度">
            <option value="1">1 跳</option>
            <option value="2">2 跳</option>
            <option value="3">3 跳</option>
          </select>
        </div>
        <button id="reset-button" class="ghost-action" type="button">重置</button>
        <button id="export-button" class="primary-action" type="button">导出 JSON</button>
      </div>
    </div>
    <div id="case-context" class="context-bar" aria-label="当前分析上下文">
      <div class="context-primary">
        <span class="context-label">当前焦点</span>
        <strong id="context-focus-label">正在载入…</strong>
        <code id="context-focus-id">—</code>
      </div>
      <span class="context-divider" aria-hidden="true"></span>
      <div class="context-view">
        <strong id="context-view-label">正在载入视图…</strong>
        <span id="context-view-description">正在读取分析口径</span>
      </div>
      <div class="context-meta">
        <span><small>数据截至</small><b>{html.escape(str(graph.get("meta", {}).get("as_of") or "—"))}</b></span>
        <span><small>Case ID</small><b>{html.escape(str(graph.get("meta", {}).get("case_id") or project.name))}</b></span>
      </div>
    </div>
  </header>

  <div class="workspace-shell">
    <nav class="graph-rail" aria-label="图谱工具">
      <button id="layer-toggle" class="rail-action" type="button" aria-controls="filter-panel" aria-expanded="false" title="打开图层与筛选">
        <span class="rail-glyph rail-glyph-layers" aria-hidden="true"></span><span>图层</span>
      </button>
      <div class="rail-divider" aria-hidden="true"></div>
      <button id="focus-back" class="rail-action" type="button" title="返回上一个焦点" disabled>
        <span class="rail-glyph rail-glyph-back" aria-hidden="true"></span><span>返回</span>
      </button>
      <button id="focus-forward" class="rail-action" type="button" title="前往下一个焦点" disabled>
        <span class="rail-glyph rail-glyph-forward" aria-hidden="true"></span><span>前进</span>
      </button>
      <button id="focus-neighborhood" class="rail-action" type="button" aria-pressed="false" title="只显示当前节点的局部关系">
        <span class="rail-glyph rail-glyph-focus" aria-hidden="true"></span><span>局部</span>
      </button>
      <button id="galaxy-toggle" class="rail-action" type="button" aria-controls="galaxy-panel" aria-expanded="false" title="打开银河视图实验室">
        <span class="rail-glyph rail-glyph-galaxy" aria-hidden="true"></span><span>星图</span>
      </button>
      <div class="rail-spacer"></div>
      <button id="inspector-toggle" class="rail-action" type="button" aria-controls="inspector-panel" aria-expanded="false" title="打开节点检查器">
        <span class="rail-glyph rail-glyph-detail" aria-hidden="true"></span><span>详情</span>
      </button>
      <button id="ledger-toggle" class="rail-action" type="button" aria-controls="relation-ledger" aria-expanded="false" title="打开关系账本">
        <span class="rail-glyph rail-glyph-ledger" aria-hidden="true"></span><span>关系</span>
      </button>
    </nav>

    <div id="workspace" class="workspace">
    <aside id="filter-panel" class="filter-panel" aria-label="图谱筛选器" aria-hidden="true">
      <div class="panel-heading">
        <div><span class="section-eyebrow">Data layers</span><h2>图层与筛选</h2></div>
        <div class="panel-actions">
          <button id="select-all-nodes" class="small-button" type="button">恢复全部</button>
          <button id="filter-close" class="panel-close" type="button" aria-label="关闭图层与筛选">×</button>
        </div>
      </div>
      <p class="panel-copy">控制画布上出现的实体与证据关系。</p>
      <div class="summary-strip">
        <div class="summary-stat"><b id="total-node-count">—</b><span>全部节点</span></div>
        <div class="summary-stat"><b id="total-edge-count">—</b><span>全部关系</span></div>
      </div>
      <div id="quality-banner" class="quality-banner" role="status" aria-live="polite"></div>
      <section class="filter-section">
        <div class="section-heading"><h3>节点类型</h3><span id="node-filter-summary">—</span></div>
        <div id="node-type-filters" class="filter-list"></div>
      </section>
      <section class="filter-section">
        <div class="section-heading"><h3>关系类型</h3><span id="relation-filter-summary">—</span></div>
        <div id="relation-type-filters" class="filter-list"></div>
      </section>
      <details class="legend-section" open>
        <summary>节点图例</summary>
        <div id="node-legend" class="legend-grid"></div>
      </details>
      <details class="legend-section">
        <summary>边的证据口径</summary>
        <div id="edge-legend"></div>
      </details>
    </aside>

    <aside id="galaxy-panel" class="galaxy-panel" aria-label="银河视图实验室" aria-hidden="true">
      <div class="panel-heading galaxy-panel-heading">
        <div><span class="section-eyebrow">Galaxy laboratory</span><h2>银河视图</h2></div>
        <button id="galaxy-close" class="panel-close" type="button" aria-label="关闭银河视图实验室">×</button>
      </div>
      <p class="panel-copy">用连接度、实体群组和证据关系构造专利星系；所有参数均可实时预览。</p>

      <section class="galaxy-section" aria-labelledby="galaxy-preset-title">
        <div class="section-heading"><h3 id="galaxy-preset-title">视觉预设</h3><span id="galaxy-preset-status">Galaxy</span></div>
        <div class="galaxy-presets" role="group" aria-label="银河视觉预设">
          <button type="button" data-galaxy-preset="atlas" aria-pressed="true"><i aria-hidden="true"></i><b>星轨</b><small>视频巡航</small></button>
          <button type="button" data-galaxy-preset="galaxy" aria-pressed="false"><i aria-hidden="true"></i><b>银河</b><small>均衡层级</small></button>
          <button type="button" data-galaxy-preset="spiral" aria-pressed="false"><i aria-hidden="true"></i><b>旋臂</b><small>强化轨道</small></button>
          <button type="button" data-galaxy-preset="nebula" aria-pressed="false"><i aria-hidden="true"></i><b>星云</b><small>辉光团簇</small></button>
          <button type="button" data-galaxy-preset="minimal" aria-pressed="false"><i aria-hidden="true"></i><b>极简</b><small>证据优先</small></button>
        </div>
      </section>

      <section class="galaxy-section" aria-labelledby="galaxy-readability-title">
        <div class="section-heading"><h3 id="galaxy-readability-title">可读性</h3><span>实时</span></div>
        <label class="galaxy-select-row" for="galaxy-size-mode"><span><b>节点大小</b><small>中心节点的视觉权重</small></span>
          <select id="galaxy-size-mode">
            <option value="degree">按连接数</option>
            <option value="type">按实体类型</option>
            <option value="uniform">统一大小</option>
          </select>
        </label>
        <label class="galaxy-range-row" for="galaxy-node-scale"><span><b>节点缩放</b><small>整体节点与标签比例</small></span><output id="galaxy-node-scale-value">1.00×</output>
          <input id="galaxy-node-scale" type="range" min="0.65" max="1.8" value="1" step="0.05">
        </label>
        <label class="galaxy-range-row" for="galaxy-edge-opacity"><span><b>链接透明度</b><small>降低密集关系的视觉噪声</small></span><output id="galaxy-edge-opacity-value">34%</output>
          <input id="galaxy-edge-opacity" type="range" min="0.08" max="0.82" value="0.34" step="0.02">
        </label>
        <label class="galaxy-range-row" for="galaxy-glow-strength"><span><b>辉光强度</b><small>突出高连接度 hub</small></span><output id="galaxy-glow-strength-value">62%</output>
          <input id="galaxy-glow-strength" type="range" min="0" max="1" value="0.62" step="0.02">
        </label>
        <label class="galaxy-range-row" for="galaxy-trail-density"><span><b>星轨密度</b><small>每条真实关系的光轨束数量</small></span><output id="galaxy-trail-density-value">4 股</output>
          <input id="galaxy-trail-density" type="range" min="0" max="5" value="4" step="1">
        </label>
      </section>

      <section class="galaxy-section" aria-labelledby="galaxy-physics-title">
        <div class="section-heading"><h3 id="galaxy-physics-title">空间与力场</h3><span>物理</span></div>
        <label class="galaxy-range-row" for="galaxy-link-distance"><span><b>链接距离</b><small>关系两端的目标距离</small></span><output id="galaxy-link-distance-value">94</output>
          <input id="galaxy-link-distance" type="range" min="52" max="168" value="94" step="2">
        </label>
        <label class="galaxy-range-row" for="galaxy-pressure"><span><b>星系斥力</b><small>控制团簇之间的呼吸空间</small></span><output id="galaxy-pressure-value">1.00×</output>
          <input id="galaxy-pressure" type="range" min="0.55" max="1.8" value="1" step="0.05">
        </label>
        <label class="galaxy-range-row" for="galaxy-orbit-strength"><span><b>旋臂强度</b><small>控制轨道弯曲与环绕幅度</small></span><output id="galaxy-orbit-strength-value">36%</output>
          <input id="galaxy-orbit-strength" type="range" min="0" max="1" value="0.36" step="0.02">
        </label>
        <div class="galaxy-switches">
          <label><input id="galaxy-starfield" type="checkbox" checked><span><b>星空背景</b><small>深度星尘</small></span></label>
          <label><input id="galaxy-twinkle" type="checkbox" checked><span><b>星星眨眼</b><small>轻微闪烁</small></span></label>
          <label><input id="galaxy-auto-orbit" type="checkbox"><span><b>自动环绕</b><small>空闲时慢速旋转</small></span></label>
          <label><input id="galaxy-camera-cruise" type="checkbox" checked><span><b>镜头巡航</b><small>缓慢推拉与漂移</small></span></label>
        </div>
      </section>

      <section class="galaxy-section" aria-labelledby="galaxy-diagnostics-title">
        <div class="section-heading"><h3 id="galaxy-diagnostics-title">星图诊断</h3><span>可见图</span></div>
        <div id="galaxy-stats" class="galaxy-stats" role="status" aria-live="polite">
          <span><b id="galaxy-fps">—</b><small>FPS</small></span>
          <span><b id="galaxy-stat-nodes">0</b><small>节点</small></span>
          <span><b id="galaxy-stat-links">0</b><small>关系</small></span>
          <span><b id="galaxy-stat-hubs">0</b><small>Hub</small></span>
        </div>
        <div class="galaxy-analysis-actions">
          <button id="galaxy-top-hubs" class="small-button" type="button">查看 Top Hub</button>
          <button id="galaxy-bridge-nodes" class="small-button" type="button">检查桥接节点</button>
        </div>
      </section>

      <section class="galaxy-section galaxy-actions-section" aria-label="银河视图操作">
        <button id="galaxy-replay" class="small-button" type="button">重播入场</button>
        <button id="galaxy-save" class="small-button" type="button">保存我的预设</button>
        <button id="galaxy-reset" class="small-button" type="button">全部重置</button>
      </section>
    </aside>

    <main id="main-content" class="graph-panel" data-galaxy-mode="atlas" data-starfield="true" data-twinkle="true">
      <div class="graph-depth-field" aria-hidden="true">
        <span class="depth-plane depth-plane-far"></span>
        <span class="depth-plane depth-plane-mid"></span>
        <span class="depth-plane depth-plane-near"></span>
      </div>
      <div class="canvas-toolbar">
        <div class="focus-stack">
          <div class="focus-card">
            <span class="focus-mark" aria-hidden="true"></span>
            <span class="focus-copy"><small>画布焦点</small><strong id="canvas-focus-label">正在载入…</strong><code id="canvas-focus-id">—</code></span>
          </div>
          <div class="path-legend" aria-label="焦点关系方向">
            <span data-path="incoming"><i aria-hidden="true"></i>入链</span>
            <span data-path="outgoing"><i aria-hidden="true"></i>出链</span>
            <span data-path="derived"><i aria-hidden="true"></i>推导关系</span>
          </div>
        </div>
        <div class="canvas-tools">
          <span id="visible-count" class="visible-count">加载图谱…</span>
          <span class="zoom-readout"><small>Zoom</small><output id="zoom-level" aria-label="当前缩放比例">100%</output></span>
          <div class="button-group" aria-label="画布工具">
            <button id="motion-toggle" type="button" aria-pressed="true" title="开关弹簧联动、阻尼震动与轻微漂浮">力场 开</button>
            <button id="layout-button" type="button">重新布局</button>
            <button id="fit-button" type="button">适合窗口</button>
          </div>
        </div>
      </div>
      <div id="technology-lanes" class="technology-lanes" aria-hidden="true" hidden></div>
      <canvas id="star-trail-canvas" class="star-trail-canvas" aria-hidden="true"></canvas>
      <div id="graph-canvas" class="graph-canvas" role="img" aria-label="专利证据关系图" tabindex="0"></div>
      <div class="canvas-hint" aria-hidden="true"><b>操作提示</b><span>拖动节点触发弹簧联动 · 滚轮/双指快速缩放 · 点击重叠节点逐层选择</span></div>
      <div id="empty-state" class="empty-state" hidden>
        <h2>当前筛选没有节点</h2>
        <p>清空搜索词、恢复节点类型或切换预设视图。</p>
      </div>
      <div id="limit-banner" class="limit-banner" role="status" hidden></div>
      <div id="graph-status" class="skip-link" aria-live="polite"></div>
    </main>

    <aside id="inspector-panel" class="inspector-panel" aria-label="节点检查器" aria-hidden="true">
      <div class="inspector-heading">
        <div><span class="section-eyebrow">Node inspector</span><span id="inspector-type" class="inspector-type">未选择</span></div>
        <button id="inspector-close" class="panel-close" type="button" aria-label="关闭节点检查器">×</button>
      </div>
      <h2 id="inspector-title" class="inspector-title">选择一个节点</h2>
      <p id="inspector-id" class="inspector-id">点击图中节点查看双向链接</p>
      <div class="inspector-stats" aria-label="节点关系统计">
        <span><b id="inspector-outgoing-count">0</b><small>出链</small></span>
        <span><b id="inspector-backlink-count">0</b><small>反向链接</small></span>
        <span><b id="inspector-evidence-count">0</b><small>关联证据</small></span>
      </div>
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

  <section class="relation-ledger" id="relation-ledger" aria-labelledby="relation-ledger-title" aria-hidden="true">
    <div class="ledger-head">
      <div><h2 id="relation-ledger-title">当前可见关系</h2><p>边只存一次；反向链接由入边动态计算。最多显示 200 条。</p></div>
      <div class="ledger-actions"><a href="graph-data.json">打开机器可读图数据</a><button id="ledger-close" class="panel-close" type="button" aria-label="关闭关系账本">×</button></div>
    </div>
    <div class="table-scroll">
      <table class="relation-table">
        <thead><tr><th>源节点</th><th>关系</th><th>目标节点</th><th>关系语义</th><th>因果状态 / 证据等级</th><th>finding_id</th></tr></thead>
        <tbody id="relation-table-body"></tbody>
      </table>
    </div>
  </section>
  </div>
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
