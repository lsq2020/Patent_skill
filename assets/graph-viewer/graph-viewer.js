(() => {
  "use strict";

  const DATA = window.PATENT_GRAPH_DATA;
  const QUALITY = window.PATENT_GRAPH_QUALITY;
  const nodesById = new Map(DATA.nodes.map((node) => [node.id, node]));
  const nodeTypeLabels = new Map(DATA.legend.node_types.map((row) => [row.value, row.label]));
  const presetById = new Map(DATA.presets.map((preset) => [preset.id, preset]));
  const params = new URLSearchParams(window.location.search);
  const initialPreset = presetById.has(params.get("view")) ? params.get("view") : "technology";
  const presetDefaultDepth = (presetId) => {
    const value = Number(presetById.get(presetId)?.default_depth ?? DATA.meta.default_depth ?? 1);
    return [1, 2, 3].includes(value) ? value : 1;
  };
  const initialDepth = ["1", "2", "3"].includes(params.get("depth"))
    ? Number(params.get("depth"))
    : presetDefaultDepth(initialPreset);

  const state = {
    preset: initialPreset,
    depth: initialDepth,
    focus: nodesById.has(params.get("focus")) ? params.get("focus") : DATA.meta.default_focus,
    query: params.get("q") || "",
    tab: "overview",
    nodeTypes: new Set(),
    relationTypes: new Set(),
    visibleNodeIds: new Set(),
    visibleEdgeIds: new Set(),
  };

  const $ = (selector) => document.querySelector(selector);
  const byId = (id) => document.getElementById(id);
  const escapeHtml = (value) => String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
  const formatValue = (value) => {
    if (Array.isArray(value)) return value.join("; ");
    if (value && typeof value === "object") return JSON.stringify(value, null, 2);
    return String(value ?? "");
  };
  const safeUrl = (value) => /^https?:\/\//i.test(String(value || "")) ? value : "";
  const compactLabel = (value, limit = 20) => {
    const text = String(value || "").trim();
    return text.length > limit ? `${text.slice(0, limit - 1)}…` : text;
  };
  const nodeDisplayLabel = (node) => {
    if (node.type !== "patent_family") return node.label;
    const properties = node.properties || {};
    const document = properties.representative_document || properties.representative_application || "";
    const priorityYear = String(properties.earliest_priority || "").slice(0, 4);
    const applicant = compactLabel(String(properties.applicant_or_assignee || "").split("/")[0], 22);
    const detail = [document, priorityYear ? `优先权 ${priorityYear}` : ""].filter(Boolean).join(" · ");
    return [node.label, detail, applicant].filter(Boolean).join("\n");
  };

  const cy = cytoscape({
    container: byId("graph-canvas"),
    elements: [],
    minZoom: 0.18,
    maxZoom: 2.8,
    selectionType: "single",
    boxSelectionEnabled: false,
    style: [
      {
        selector: "node",
        style: {
          "background-color": "#718096",
          "border-color": "#ffffff",
          "border-width": 2.5,
          color: "#24324a",
          label: "data(displayLabel)",
          "font-family": "Inter, Segoe UI, PingFang SC, sans-serif",
          "font-size": 9.5,
          "font-weight": 650,
          "min-zoomed-font-size": 3.5,
          "text-background-color": "#ffffff",
          "text-background-opacity": 0.94,
          "text-background-padding": 4,
          "text-margin-y": 7,
          "text-max-width": 118,
          "text-valign": "bottom",
          "text-wrap": "ellipsis",
          height: 28,
          width: 28,
        },
      },
      { selector: 'node[type = "research_object"]', style: { "background-color": "#101a2d", shape: "round-rectangle", width: 98, height: 44, color: "#ffffff", "text-valign": "center", "text-background-opacity": 0, "text-margin-y": 0, "font-size": 10.5 } },
      { selector: 'node[type = "target"]', style: { "background-color": "#f6f1ff", "border-color": "#7650c7", shape: "round-rectangle", width: 76, height: 38, color: "#573a98", "text-valign": "center", "text-background-opacity": 0, "text-margin-y": 0 } },
      { selector: 'node[type = "indication"]', style: { "background-color": "#fff1f5", "border-color": "#c84f7f", shape: "round-rectangle", width: 82, height: 38, color: "#9f315d", "text-valign": "center", "text-background-opacity": 0, "text-margin-y": 0 } },
      { selector: 'node[type = "patent_family"]', style: { "background-color": "#f7faff", "border-color": "#2f66d0", "border-width": 2.2, shape: "round-rectangle", width: 112, height: 54, color: "#17345f", "font-size": 8.3, "font-weight": 680, "text-valign": "center", "text-wrap": "wrap", "text-max-width": 100, "text-background-opacity": 0, "text-margin-y": 0 } },
      { selector: 'node[type = "patent_document"]', style: { "background-color": "#178176", shape: "hexagon" } },
      { selector: 'node[type = "claim"]', style: { "background-color": "#fff8e9", "border-color": "#d9962d", shape: "round-rectangle", width: 88, height: 38, color: "#805014", "text-valign": "center", "text-background-opacity": 0, "text-margin-y": 0, "text-max-width": 78 } },
      { selector: 'node[type = "evidence"]', style: { "background-color": "#d14b63", shape: "diamond", width: 31, height: 31 } },
      { selector: 'node[type = "applicant"]', style: { "background-color": "#334155", shape: "round-rectangle", width: 36, height: 27 } },
      { selector: 'node[type = "jurisdiction"]', style: { "background-color": "#0891b2", shape: "ellipse", width: 26, height: 26 } },
      { selector: 'node[type = "technology_theme"]', style: { "background-color": "#f4f8e9", "border-color": "#70952e", shape: "tag", width: 84, height: 34, color: "#4f6f1e", "text-valign": "center", "text-background-opacity": 0, "text-margin-y": 0, "text-max-width": 72 } },
      { selector: 'node[type = "source"]', style: { "background-color": "#94a3b8", shape: "vee", width: 27, height: 27 } },
      {
        selector: "edge",
        style: {
          width: 1.2,
          "line-color": "#a5afbd",
          "target-arrow-color": "#a5afbd",
          "target-arrow-shape": "triangle",
          "arrow-scale": 0.72,
          "curve-style": "bezier",
          opacity: 0.72,
        },
      },
      { selector: 'edge[assertion = "rule_derived"]', style: { "line-style": "dashed" } },
      { selector: 'edge[assertion = "model_inference"]', style: { "line-style": "dotted", opacity: 0.58 } },
      { selector: 'edge[type = "SUPPORTED_BY"]', style: { "line-color": "#d14b63", "target-arrow-color": "#d14b63" } },
      { selector: 'edge[type = "PROTECTS"]', style: { "line-color": "#6d932f", "target-arrow-color": "#6d932f" } },
      { selector: 'edge[type = "FILED_BY"]', style: { "line-color": "#475569", "target-arrow-color": "#475569" } },
      { selector: "edge.edge-active", style: { label: "data(label)", width: 2.1, opacity: 1, color: "#344054", "font-size": 8, "font-weight": 650, "text-rotation": "autorotate", "text-background-color": "#ffffff", "text-background-opacity": 0.96, "text-background-padding": 2, "text-margin-y": -7, "z-index": 8 } },
      { selector: "node:selected", style: { "border-color": "#101a2d", "border-width": 4, "underlay-color": "#2f66d0", "underlay-opacity": 0.16, "underlay-padding": 7 } },
      { selector: "edge:selected", style: { width: 2.4, opacity: 1, "overlay-color": "#2f66d0", "overlay-opacity": 0.08 } },
      { selector: ".faded", style: { opacity: 0.11, "text-opacity": 0.08 } },
    ],
  });

  function configurePreset(presetId, useDefaultDepth = false) {
    const preset = presetById.get(presetId) || DATA.presets[0];
    state.preset = preset.id;
    if (useDefaultDepth) {
      state.depth = presetDefaultDepth(preset.id);
      byId("depth-control").value = String(state.depth);
    }
    state.nodeTypes = new Set(preset.node_types);
    state.relationTypes = new Set(preset.relation_types);
    byId("view-preset").value = preset.id;
    renderFilters();
    renderContext();
  }

  function collectNeighborhood(seedIds, depth, eligibleNodes, eligibleEdges) {
    const selected = new Set(seedIds.filter((id) => eligibleNodes.has(id)));
    let frontier = new Set(selected);
    for (let step = 0; step < depth; step += 1) {
      const next = new Set();
      eligibleEdges.forEach((edge) => {
        if (frontier.has(edge.source) && eligibleNodes.has(edge.target)) next.add(edge.target);
        if (frontier.has(edge.target) && eligibleNodes.has(edge.source)) next.add(edge.source);
      });
      next.forEach((id) => selected.add(id));
      frontier = next;
      if (!frontier.size) break;
    }
    return selected;
  }

  function computeVisibleElements() {
    const eligibleNodes = new Set(
      DATA.nodes.filter((node) => state.nodeTypes.has(node.type)).map((node) => node.id)
    );
    const eligibleEdges = DATA.edges.filter(
      (edge) => state.relationTypes.has(edge.type) && eligibleNodes.has(edge.source) && eligibleNodes.has(edge.target)
    );
    let seedIds = [];
    const query = state.query.trim().toLowerCase();
    if (query) {
      seedIds = DATA.nodes
        .filter((node) => eligibleNodes.has(node.id) && node.search_text.includes(query))
        .map((node) => node.id);
    } else if (eligibleNodes.has(state.focus)) {
      seedIds = [state.focus];
    }
    let selected = seedIds.length
      ? collectNeighborhood(seedIds, state.depth, eligibleNodes, eligibleEdges)
      : new Set(eligibleNodes);

    const limit = Number(DATA.meta.visible_node_limit || 80);
    const degrees = new CounterMap();
    eligibleEdges.forEach((edge) => {
      degrees.increment(edge.source);
      degrees.increment(edge.target);
    });
    const ordered = [...selected].sort((a, b) => {
      const seedDelta = Number(seedIds.includes(b)) - Number(seedIds.includes(a));
      return seedDelta || degrees.get(b) - degrees.get(a) || a.localeCompare(b);
    });
    const truncated = ordered.length > limit;
    selected = new Set(ordered.slice(0, limit));
    const edges = eligibleEdges.filter((edge) => selected.has(edge.source) && selected.has(edge.target));
    return {
      nodes: DATA.nodes.filter((node) => selected.has(node.id)),
      edges,
      truncated,
      totalEligible: eligibleNodes.size,
      matchCount: seedIds.length,
    };
  }

  function CounterMap() {
    this.values = new Map();
    this.increment = (key) => this.values.set(key, (this.values.get(key) || 0) + 1);
    this.get = (key) => this.values.get(key) || 0;
  }

  function cytoscapeElements(view) {
    return [
      ...view.nodes.map((node) => ({
        group: "nodes",
        data: {
          id: node.id,
          label: node.label,
          displayLabel: nodeDisplayLabel(node),
          type: node.type,
          summary: node.summary,
          properties: node.properties,
          sourceUrl: node.source_url,
        },
      })),
      ...view.edges.map((edge) => ({
        group: "edges",
        data: {
          id: edge.id,
          source: edge.source,
          target: edge.target,
          type: edge.type,
          label: edge.label,
          assertion: edge.assertion,
          linkMethods: edge.link_methods,
          evidenceIds: edge.evidence_ids,
        },
      })),
    ];
  }

  function semanticPositions(preset) {
    const lanes = preset?.lanes || [];
    const width = Math.max(cy.width(), 640);
    const height = Math.max(cy.height(), 600);
    const maxRows = Math.max(6, Math.floor((height - 180) / 54));
    const columnGap = 126;
    const laneGap = 54;
    const top = 124;
    const positions = new Map();
    let cursorX = 72;

    lanes.forEach((lane) => {
      const laneTypes = new Set(lane.node_types || []);
      const laneNodes = cy.nodes()
        .filter((node) => laneTypes.has(node.data("type")))
        .sort((left, right) => String(left.data("label")).localeCompare(String(right.data("label"))));
      const columnCount = Math.max(1, Math.ceil(laneNodes.length / maxRows));
      laneNodes.forEach((node, nodeIndex) => {
        const column = Math.floor(nodeIndex / maxRows);
        const row = nodeIndex % maxRows;
        const rowsInColumn = Math.min(maxRows, laneNodes.length - column * maxRows);
        const rowGap = Math.min(58, (height - top - 60) / Math.max(rowsInColumn - 1, 1));
        const blockHeight = rowGap * Math.max(rowsInColumn - 1, 0);
        const y = top + (height - top - 60 - blockHeight) / 2 + row * rowGap;
        positions.set(node.id(), { x: cursorX + column * columnGap, y });
      });
      cursorX += columnCount * columnGap + laneGap;
    });
    return (node) => positions.get(node.id()) || { x: width / 2, y: height / 2 };
  }

  function runLayout() {
    const preset = presetById.get(state.preset);
    const name = preset?.layout === "semantic"
      ? "semantic"
      : cy.nodes().length > 55 ? "cose" : (preset?.layout || "cose");
    const options = name === "semantic"
      ? { name: "preset", positions: semanticPositions(preset), fit: true, padding: 56, animate: false }
      : name === "breadthfirst"
        ? { name, directed: true, spacingFactor: 1.25, padding: 42, animate: false }
        : { name: "cose", idealEdgeLength: 82, nodeRepulsion: 5200, gravity: 0.16, padding: 42, animate: false, randomize: true };
    cy.layout(options).run();
    if (name === "semantic" && cy.zoom() < 0.58) {
      cy.zoom(0.58);
      cy.center();
    }
  }

  function renderTechnologyLanes(view) {
    const container = byId("technology-lanes");
    const preset = presetById.get(state.preset);
    const lanes = preset?.layout === "semantic" ? (preset.lanes || []) : [];
    container.hidden = !lanes.length;
    container.textContent = "";
    if (!lanes.length) return;
    const maxRows = Math.max(6, Math.floor((Math.max(cy.height(), 600) - 180) / 54));
    const laneWeights = [];
    lanes.forEach((lane) => {
      const laneTypes = new Set(lane.node_types || []);
      const count = view.nodes.filter((node) => laneTypes.has(node.type)).length;
      laneWeights.push(Math.max(1, Math.ceil(count / maxRows)));
      const item = document.createElement("span");
      const label = document.createElement("b");
      const total = document.createElement("small");
      label.textContent = lane.label;
      total.textContent = `${count} 个节点`;
      item.append(label, total);
      container.append(item);
    });
    container.style.gridTemplateColumns = laneWeights.map((weight) => `minmax(0, ${weight}fr)`).join(" ");
  }

  function activateFocusEdges() {
    cy.edges().removeClass("edge-active");
    const focus = cy.getElementById(state.focus);
    if (focus.length) focus.connectedEdges().addClass("edge-active");
  }

  function renderGraph() {
    const view = computeVisibleElements();
    state.visibleNodeIds = new Set(view.nodes.map((node) => node.id));
    state.visibleEdgeIds = new Set(view.edges.map((edge) => edge.id));
    cy.elements().remove();
    cy.add(cytoscapeElements(view));
    renderTechnologyLanes(view);
    if (cy.nodes().length) {
      runLayout();
      const focus = cy.getElementById(state.focus);
      if (focus.length) {
        focus.select();
        activateFocusEdges();
      }
    }
    byId("empty-state").hidden = view.nodes.length > 0;
    const limitBanner = byId("limit-banner");
    limitBanner.hidden = !view.truncated;
    limitBanner.textContent = view.truncated
      ? `当前视图符合条件的节点为 ${view.totalEligible} 个；为保持可读性，仅显示优先级最高的 ${view.nodes.length} 个。请搜索、缩小类型或选择节点。`
      : "";
    byId("visible-count").textContent = `${view.nodes.length} 节点 · ${view.edges.length} 关系`;
    byId("graph-status").textContent = `图谱已更新，显示 ${view.nodes.length} 个节点和 ${view.edges.length} 条关系。`;
    renderRelationTable(view.edges);
    renderInspector();
    updateUrl();
  }

  function renderFilters() {
    renderFilterGroup("node-type-filters", DATA.facets.node_types, state.nodeTypes, nodeTypeLabels, () => renderGraph());
    renderFilterGroup("relation-type-filters", DATA.facets.relation_types, state.relationTypes, null, () => renderGraph());
    byId("node-filter-summary").textContent = `${state.nodeTypes.size} / ${DATA.facets.node_types.length}`;
    byId("relation-filter-summary").textContent = `${state.relationTypes.size} / ${DATA.facets.relation_types.length}`;
  }

  function renderFilterGroup(containerId, rows, selected, labels, onChange) {
    const container = byId(containerId);
    container.textContent = "";
    rows.forEach((row) => {
      const label = document.createElement("label");
      label.className = `filter-option${selected.has(row.value) ? " is-selected" : ""}`;
      const checkbox = document.createElement("input");
      checkbox.type = "checkbox";
      checkbox.value = row.value;
      checkbox.checked = selected.has(row.value);
      checkbox.addEventListener("change", () => {
        if (checkbox.checked) selected.add(row.value);
        else selected.delete(row.value);
        label.classList.toggle("is-selected", checkbox.checked);
        const summaryId = containerId === "node-type-filters" ? "node-filter-summary" : "relation-filter-summary";
        byId(summaryId).textContent = `${selected.size} / ${rows.length}`;
        onChange();
      });
      const text = document.createElement("span");
      text.textContent = labels?.get(row.value) || row.label;
      const count = document.createElement("span");
      count.className = "filter-count";
      count.textContent = row.count;
      label.append(checkbox, text, count);
      container.append(label);
    });
  }

  function renderQuality() {
    const banner = byId("quality-banner");
    banner.dataset.status = QUALITY.status;
    const label = QUALITY.status === "pass" ? "通过" : QUALITY.status === "error" ? "错误" : "需补录";
    const gapCount = QUALITY.gaps.reduce((sum, gap) => sum + gap.count, 0);
    const detail = QUALITY.gaps.length
      ? `${QUALITY.gaps.length} 类缺口，涉及 ${gapCount} 条记录。`
      : "未发现结构性缺口。";
    banner.innerHTML = `<div class="quality-heading"><span class="quality-dot" aria-hidden="true"></span><b>数据质量 · ${escapeHtml(label)}</b></div><p>${escapeHtml(detail)}</p><a href="graph-quality.json">查看完整质量报告 →</a>`;
    byId("total-node-count").textContent = DATA.meta.node_count;
    byId("total-edge-count").textContent = DATA.meta.edge_count;
  }

  function renderLegend() {
    const nodeColors = {
      research_object: "#111c31", target: "#7c3aed", indication: "#db2777",
      patent_family: "#2563eb", patent_document: "#0f766e", claim: "#f59e0b",
      evidence: "#e11d48", applicant: "#334155", jurisdiction: "#0891b2",
      technology_theme: "#65a30d", source: "#94a3b8",
    };
    byId("node-legend").innerHTML = DATA.legend.node_types
      .map((row) => `<div class="legend-row"><span class="legend-dot" style="background:${nodeColors[row.value] || "#64748b"}"></span>${escapeHtml(row.label)}</div>`)
      .join("");
    byId("edge-legend").innerHTML = DATA.legend.assertions
      .map((row) => `<div class="legend-row"><span class="legend-line ${escapeHtml(row.line_style)}"></span>${escapeHtml(row.label)}</div>`)
      .join("");
  }

  function renderRelationTable(edges) {
    const body = byId("relation-table-body");
    if (!edges.length) {
      body.innerHTML = '<tr><td colspan="5" class="empty-copy">当前筛选下没有关系边。</td></tr>';
      return;
    }
    body.innerHTML = edges.slice(0, 200).map((edge) => {
      const source = nodesById.get(edge.source);
      const target = nodesById.get(edge.target);
      return `<tr>
        <td><button type="button" data-focus="${escapeHtml(edge.source)}">${escapeHtml(source?.label || edge.source)}</button></td>
        <td>${escapeHtml(edge.label || edge.type)}</td>
        <td><button type="button" data-focus="${escapeHtml(edge.target)}">${escapeHtml(target?.label || edge.target)}</button></td>
        <td><span class="assertion">${escapeHtml(edge.assertion)}</span></td>
        <td>${escapeHtml((edge.evidence_ids || []).join("; ") || "—")}</td>
      </tr>`;
    }).join("");
  }

  function incidentEdges(nodeId, direction = "both") {
    return DATA.edges.filter((edge) => {
      if (direction === "out") return edge.source === nodeId;
      if (direction === "in") return edge.target === nodeId;
      return edge.source === nodeId || edge.target === nodeId;
    });
  }

  function relatedNodes(nodeId, type, maxDepth = 1) {
    let frontier = new Set([nodeId]);
    const visited = new Set([nodeId]);
    for (let step = 0; step < maxDepth; step += 1) {
      const next = new Set();
      DATA.edges.forEach((edge) => {
        if (frontier.has(edge.source) && !visited.has(edge.target)) next.add(edge.target);
        if (frontier.has(edge.target) && !visited.has(edge.source)) next.add(edge.source);
      });
      next.forEach((id) => visited.add(id));
      frontier = next;
    }
    return [...visited]
      .filter((id) => id !== nodeId && nodesById.get(id)?.type === type)
      .map((id) => nodesById.get(id));
  }

  function propertyList(properties) {
    const entries = Object.entries(properties || {})
      .filter(([, value]) => value !== "" && value !== null && value !== undefined && !(Array.isArray(value) && !value.length))
      .slice(0, 28);
    if (!entries.length) return '<p class="empty-copy">没有更多结构化属性。</p>';
    return `<dl class="property-list">${entries.map(([key, value]) => `<dt>${escapeHtml(key)}</dt><dd>${escapeHtml(formatValue(value))}</dd>`).join("")}</dl>`;
  }

  function nodeList(nodes, emptyMessage) {
    if (!nodes.length) return `<p class="empty-copy">${escapeHtml(emptyMessage)}</p>`;
    return `<div class="node-list">${nodes.map((node) => `<button class="node-link" type="button" data-focus="${escapeHtml(node.id)}"><span class="node-link-copy"><b>${escapeHtml(node.label)}</b><small>${escapeHtml(nodeTypeLabels.get(node.type) || node.type)} · ${escapeHtml(node.id)}</small></span><span class="node-link-arrow" aria-hidden="true">→</span></button>`).join("")}</div>`;
  }

  function edgeList(edges, direction) {
    if (!edges.length) return '<p class="empty-copy">当前节点没有对应关系。</p>';
    return `<div class="node-list">${edges.map((edge) => {
      const otherId = direction === "in" ? edge.source : edge.target;
      const other = nodesById.get(otherId);
      return `<button class="node-link" type="button" data-focus="${escapeHtml(otherId)}"><span class="node-link-copy"><b>${escapeHtml(edge.label)} · ${escapeHtml(other?.label || otherId)}</b><small>${escapeHtml(edge.assertion)} · ${escapeHtml((edge.link_methods || []).join(" + ") || "未标注")}</small></span><span class="node-link-arrow" aria-hidden="true">→</span></button>`;
    }).join("")}</div>`;
  }

  function renderContext(node = nodesById.get(state.focus)) {
    const preset = presetById.get(state.preset) || DATA.presets[0];
    byId("context-view-label").textContent = preset?.label || "自定义视图";
    byId("context-view-description").textContent = preset?.description || "按当前筛选条件浏览图谱。";
    const focusLabel = node?.label || "未选择节点";
    const focusId = node?.id || "—";
    byId("context-focus-label").textContent = focusLabel;
    byId("context-focus-id").textContent = focusId;
    byId("canvas-focus-label").textContent = focusLabel;
    byId("canvas-focus-id").textContent = focusId;
  }

  function renderInspector() {
    const node = nodesById.get(state.focus);
    renderContext(node);
    if (!node) {
      byId("inspector-type").textContent = "未选择";
      byId("inspector-title").textContent = "选择一个节点";
      byId("inspector-id").textContent = "点击图中节点或搜索结果查看双向链接";
      byId("inspector-outgoing-count").textContent = "0";
      byId("inspector-backlink-count").textContent = "0";
      byId("inspector-evidence-count").textContent = "0";
      byId("inspector-content").innerHTML = '<p class="empty-copy">检查器会显示属性、claim、证据、出链和反向链接。</p>';
      return;
    }
    const outgoing = incidentEdges(node.id, "out");
    const backlinks = incidentEdges(node.id, "in");
    const evidenceNodes = relatedNodes(node.id, "evidence", 2);
    byId("inspector-type").dataset.type = node.type;
    byId("inspector-type").textContent = nodeTypeLabels.get(node.type) || node.type;
    byId("inspector-title").textContent = node.label;
    byId("inspector-id").textContent = node.id;
    byId("inspector-outgoing-count").textContent = outgoing.length;
    byId("inspector-backlink-count").textContent = backlinks.length;
    byId("inspector-evidence-count").textContent = evidenceNodes.length;
    document.querySelectorAll("#inspector-tabs button").forEach((button) => {
      button.setAttribute("aria-selected", String(button.dataset.tab === state.tab));
    });
    let content = "";
    if (state.tab === "overview") {
      const url = safeUrl(node.source_url);
      content = `<div class="summary-card"><span>节点摘要</span><p>${escapeHtml(node.summary || "暂无摘要。")}</p></div>${url ? `<a class="source-action" href="${escapeHtml(url)}" target="_blank" rel="noopener noreferrer"><span>打开原始来源</span><span aria-hidden="true">↗</span></a>` : ""}<h3>结构化属性</h3>${propertyList(node.properties)}`;
    } else if (state.tab === "claims") {
      content = nodeList(relatedNodes(node.id, "claim", 2), "两跳范围内没有 claim 节点。");
    } else if (state.tab === "evidence") {
      content = nodeList(evidenceNodes, "两跳范围内没有 evidence 节点。");
    } else if (state.tab === "outgoing") {
      content = edgeList(outgoing, "out");
    } else {
      content = edgeList(backlinks, "in");
    }
    byId("inspector-content").innerHTML = content;
  }

  function updateUrl() {
    const next = new URLSearchParams();
    if (state.focus) next.set("focus", state.focus);
    next.set("view", state.preset);
    next.set("depth", String(state.depth));
    if (state.query) next.set("q", state.query);
    history.replaceState(null, "", `${window.location.pathname}?${next.toString()}${window.location.hash}`);
  }

  function selectNode(nodeId) {
    const node = nodesById.get(nodeId);
    if (!node) return;
    state.focus = nodeId;
    state.query = "";
    byId("graph-search").value = "";
    if (!state.nodeTypes.has(node.type)) state.nodeTypes.add(node.type);
    incidentEdges(nodeId).forEach((edge) => state.relationTypes.add(edge.type));
    renderFilters();
    renderGraph();
  }

  function renderSearchResults() {
    const container = byId("search-results");
    const query = state.query.trim().toLowerCase();
    if (!query) {
      container.hidden = true;
      container.textContent = "";
      return;
    }
    const results = DATA.nodes.filter((node) => node.search_text.includes(query)).slice(0, 8);
    container.innerHTML = results.length
      ? results.map((node) => `<button class="search-result" type="button" data-focus="${escapeHtml(node.id)}"><b>${escapeHtml(node.label)}</b><small>${escapeHtml(nodeTypeLabels.get(node.type) || node.type)} · ${escapeHtml(node.id)}</small></button>`).join("")
      : '<div class="search-result"><small>没有匹配节点</small></div>';
    container.hidden = false;
  }

  function exportVisible() {
    const payload = {
      meta: { ...DATA.meta, exported_at: new Date().toISOString(), focus: state.focus, view: state.preset, depth: state.depth },
      nodes: DATA.nodes.filter((node) => state.visibleNodeIds.has(node.id)),
      edges: DATA.edges.filter((edge) => state.visibleEdgeIds.has(edge.id)),
    };
    const blob = new Blob([JSON.stringify(payload, null, 2)], { type: "application/json" });
    const link = document.createElement("a");
    link.href = URL.createObjectURL(blob);
    link.download = `${DATA.meta.case_id}-${state.preset}-graph.json`;
    link.click();
    URL.revokeObjectURL(link.href);
  }

  function resetView() {
    state.focus = DATA.meta.default_focus;
    state.query = "";
    state.tab = "overview";
    byId("graph-search").value = "";
    configurePreset("technology", true);
    renderGraph();
  }

  let searchTimer;
  byId("graph-search").value = state.query;
  byId("graph-search").addEventListener("input", (event) => {
    state.query = event.target.value;
    renderSearchResults();
    window.clearTimeout(searchTimer);
    searchTimer = window.setTimeout(renderGraph, 180);
  });
  byId("graph-search").addEventListener("keydown", (event) => {
    if (event.key === "Escape") {
      byId("search-results").hidden = true;
      event.target.blur();
    }
    if (event.key === "Enter") {
      const first = DATA.nodes.find((node) => node.search_text.includes(state.query.trim().toLowerCase()));
      if (first) selectNode(first.id);
    }
  });
  byId("view-preset").addEventListener("change", (event) => {
    configurePreset(event.target.value, true);
    renderGraph();
  });
  byId("depth-control").value = String(state.depth);
  byId("depth-control").addEventListener("change", (event) => {
    state.depth = Number(event.target.value);
    renderGraph();
  });
  byId("fit-button").addEventListener("click", () => cy.fit(undefined, 44));
  byId("layout-button").addEventListener("click", runLayout);
  byId("reset-button").addEventListener("click", resetView);
  byId("export-button").addEventListener("click", exportVisible);
  byId("select-all-nodes").addEventListener("click", () => {
    state.nodeTypes = new Set(DATA.facets.node_types.map((row) => row.value));
    renderFilters();
    renderGraph();
  });
  byId("inspector-tabs").addEventListener("click", (event) => {
    const button = event.target.closest("button[data-tab]");
    if (!button) return;
    state.tab = button.dataset.tab;
    renderInspector();
  });
  document.addEventListener("click", (event) => {
    const focusTarget = event.target.closest("[data-focus]");
    if (focusTarget) {
      selectNode(focusTarget.dataset.focus);
      byId("search-results").hidden = true;
    } else if (!event.target.closest(".search-wrap")) {
      byId("search-results").hidden = true;
    }
  });
  cy.on("tap", "node", (event) => selectNode(event.target.id()));
  cy.on("mouseover", "node", (event) => {
    const neighborhood = event.target.closedNeighborhood();
    cy.elements().addClass("faded");
    neighborhood.removeClass("faded");
    event.target.connectedEdges().addClass("edge-active");
  });
  cy.on("mouseout", "node", () => {
    cy.elements().removeClass("faded");
    activateFocusEdges();
  });
  cy.on("mouseover", "edge", (event) => event.target.addClass("edge-active"));
  cy.on("mouseout", "edge", () => activateFocusEdges());
  window.addEventListener("resize", () => cy.resize());
  window.addEventListener("keydown", (event) => {
    if ((event.ctrlKey || event.metaKey) && event.key.toLowerCase() === "k") {
      event.preventDefault();
      byId("graph-search").focus();
    }
  });

  DATA.presets.forEach((preset) => {
    const option = document.createElement("option");
    option.value = preset.id;
    option.textContent = preset.label;
    byId("view-preset").append(option);
  });
  configurePreset(initialPreset);
  renderQuality();
  renderLegend();
  renderSearchResults();
  renderGraph();
})();
