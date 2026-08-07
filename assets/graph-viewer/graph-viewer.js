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
  const initialFocus = nodesById.has(params.get("focus")) ? params.get("focus") : DATA.meta.default_focus;
  const prefersReducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  const GOLDEN_ANGLE = Math.PI * (3 - Math.sqrt(5));
  const GALAXY_STORAGE_KEY = "patent-evidence-graph.galaxy-settings.v1";
  const DEFAULT_GALAXY_SETTINGS = Object.freeze({
    preset: "atlas",
    sizeMode: "degree",
    nodeScale: 1.02,
    edgeOpacity: 0.26,
    glowStrength: 0.9,
    trailDensity: 4,
    linkDistance: 104,
    pressure: 1.08,
    orbitStrength: 0.78,
    starfield: true,
    twinkle: true,
    autoOrbit: false,
    cameraCruise: true,
  });
  const GALAXY_PRESET_SETTINGS = {
    atlas: { ...DEFAULT_GALAXY_SETTINGS },
    galaxy: { ...DEFAULT_GALAXY_SETTINGS, preset: "galaxy", nodeScale: 1, edgeOpacity: 0.34, glowStrength: 0.62, trailDensity: 2, linkDistance: 94, pressure: 1, orbitStrength: 0.36, cameraCruise: false },
    spiral: { ...DEFAULT_GALAXY_SETTINGS, preset: "spiral", nodeScale: 0.96, edgeOpacity: 0.42, glowStrength: 0.74, trailDensity: 3, linkDistance: 108, pressure: 1.08, orbitStrength: 0.76, cameraCruise: false },
    nebula: { ...DEFAULT_GALAXY_SETTINGS, preset: "nebula", nodeScale: 1.08, edgeOpacity: 0.48, glowStrength: 0.9, trailDensity: 3, linkDistance: 86, pressure: 0.82, orbitStrength: 0.28, cameraCruise: false },
    minimal: { ...DEFAULT_GALAXY_SETTINGS, preset: "minimal", sizeMode: "type", nodeScale: 0.9, edgeOpacity: 0.2, glowStrength: 0, trailDensity: 0, linkDistance: 82, pressure: 0.9, orbitStrength: 0, starfield: false, twinkle: false, cameraCruise: false },
  };
  const GALAXY_TYPE_COLORS = {
    research_object: "#e5e0d6",
    target: "#a594cf",
    indication: "#d58aa1",
    patent_family: "#73a7cf",
    patent_document: "#62b6a6",
    claim: "#d7ab62",
    evidence: "#d77f73",
    applicant: "#9da7b0",
    jurisdiction: "#73a9b7",
    technology_theme: "#a8b66e",
    causal_concept: "#a9c7e3",
    source: "#7d858c",
  };
  const GALAXY_GROUP_BY_TYPE = new Map([
    ["research_object", 0], ["target", 0], ["indication", 0],
    ["patent_family", 1], ["patent_document", 1],
    ["claim", 2], ["evidence", 2], ["source", 2],
    ["applicant", 3], ["jurisdiction", 3],
    ["technology_theme", 4], ["causal_concept", 4],
  ]);

  function normalizeGalaxySettings(input = {}) {
    const preset = GALAXY_PRESET_SETTINGS[input.preset] ? input.preset : DEFAULT_GALAXY_SETTINGS.preset;
    const presetDefaults = GALAXY_PRESET_SETTINGS[preset];
    const numberSetting = (key, min, max) => {
      const value = Number(input[key]);
      return Number.isFinite(value) ? Math.min(max, Math.max(min, value)) : presetDefaults[key];
    };
    return {
      preset,
      sizeMode: ["degree", "type", "uniform"].includes(input.sizeMode) ? input.sizeMode : presetDefaults.sizeMode,
      nodeScale: numberSetting("nodeScale", 0.65, 1.8),
      edgeOpacity: numberSetting("edgeOpacity", 0.08, 0.82),
      glowStrength: numberSetting("glowStrength", 0, 1),
      trailDensity: numberSetting("trailDensity", 0, 5),
      linkDistance: numberSetting("linkDistance", 52, 168),
      pressure: numberSetting("pressure", 0.55, 1.8),
      orbitStrength: numberSetting("orbitStrength", 0, 1),
      starfield: typeof input.starfield === "boolean" ? input.starfield : presetDefaults.starfield,
      twinkle: typeof input.twinkle === "boolean" ? input.twinkle : presetDefaults.twinkle,
      autoOrbit: typeof input.autoOrbit === "boolean" ? input.autoOrbit : presetDefaults.autoOrbit,
      cameraCruise: typeof input.cameraCruise === "boolean" ? input.cameraCruise : presetDefaults.cameraCruise,
    };
  }

  function loadGalaxySettings() {
    try {
      const saved = JSON.parse(window.localStorage.getItem(GALAXY_STORAGE_KEY) || "null");
      if (!saved || typeof saved !== "object") return { ...DEFAULT_GALAXY_SETTINGS };
      return normalizeGalaxySettings(saved);
    } catch (_error) {
      return { ...DEFAULT_GALAXY_SETTINGS };
    }
  }

  const state = {
    preset: initialPreset,
    depth: initialDepth,
    focus: initialFocus,
    query: params.get("q") || "",
    tab: "overview",
    focusHistory: [initialFocus],
    focusIndex: 0,
    filterOpen: false,
    galaxyOpen: false,
    inspectorOpen: false,
    ledgerOpen: false,
    localFocus: params.get("local") === "1",
    motionEnabled: !prefersReducedMotion,
    galaxySettings: loadGalaxySettings(),
    nodeTypes: new Set(),
    relationTypes: new Set(),
    visibleNodeIds: new Set(),
    visibleEdgeIds: new Set(),
  };

  const $ = (selector) => document.querySelector(selector);
  const byId = (id) => document.getElementById(id);
  function setPanelState(panel, open) {
    const config = {
      filter: { stateKey: "filterOpen", className: "is-filter-open", panelId: "filter-panel", toggleId: "layer-toggle" },
      galaxy: { stateKey: "galaxyOpen", className: "is-galaxy-open", panelId: "galaxy-panel", toggleId: "galaxy-toggle" },
      inspector: { stateKey: "inspectorOpen", className: "is-inspector-open", panelId: "inspector-panel", toggleId: "inspector-toggle" },
      ledger: { stateKey: "ledgerOpen", className: "is-open", panelId: "relation-ledger", toggleId: "ledger-toggle" },
    }[panel];
    if (!config) return;
    state[config.stateKey] = open;
    const target = byId(config.panelId);
    const toggle = byId(config.toggleId);
    if (panel === "ledger") target.classList.toggle(config.className, open);
    else byId("workspace").classList.toggle(config.className, open);
    target.setAttribute("aria-hidden", String(!open));
    toggle.setAttribute("aria-expanded", String(open));
  }

  function updateFocusNavigation() {
    byId("focus-back").disabled = state.focusIndex <= 0;
    byId("focus-forward").disabled = state.focusIndex >= state.focusHistory.length - 1;
  }

  function navigateFocusHistory(offset) {
    const nextIndex = state.focusIndex + offset;
    if (nextIndex < 0 || nextIndex >= state.focusHistory.length) return;
    state.focusIndex = nextIndex;
    selectNode(state.focusHistory[nextIndex], { recordHistory: false, openInspector: state.inspectorOpen });
  }

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
    const applicant = compactLabel(String(properties.representative_document_assignee || properties.applicant_or_assignee || "").split("/")[0], 22);
    const detail = [document, priorityYear ? `优先权 ${priorityYear}` : ""].filter(Boolean).join(" · ");
    return [node.label, detail, applicant].filter(Boolean).join("\n");
  };
  const nodeBaseSizes = {
    research_object: 40,
    target: 24,
    indication: 24,
    patent_family: 32,
    patent_document: 19,
    claim: 23,
    evidence: 19,
    applicant: 18,
    jurisdiction: 16,
    technology_theme: 21,
    causal_concept: 26,
    source: 12,
  };

  const cy = cytoscape({
    container: byId("graph-canvas"),
    elements: [],
    minZoom: 0.18,
    maxZoom: 2.8,
    zoomingEnabled: true,
    userZoomingEnabled: true,
    panningEnabled: true,
    userPanningEnabled: true,
    autoungrabify: false,
    autolock: false,
    wheelSensitivity: 5,
    selectionType: "single",
    boxSelectionEnabled: false,
    style: [
      {
        selector: "node",
        style: {
          "background-color": "#666b70",
          "border-color": "#202326",
          "border-width": 1,
          shape: "ellipse",
          color: "#d9dde1",
          label: "data(displayLabel)",
          "font-family": "Inter, Segoe UI, PingFang SC, sans-serif",
          "font-size": 9,
          "font-weight": 500,
          "min-zoomed-font-size": 4,
          "text-background-color": "#1a1c1e",
          "text-background-opacity": 0,
          "text-background-padding": 2,
          "text-margin-y": 6,
          "text-max-width": 112,
          "text-valign": "bottom",
          "text-wrap": "ellipsis",
          "text-outline-color": "#1a1c1e",
          "text-outline-opacity": 0.72,
          "text-outline-width": 1,
          height: 15,
          width: 15,
        },
      },
      { selector: 'node.editorial-node[type = "research_object"]', style: { "background-color": "#d6d0c4", "border-color": "#eee9e1", "border-width": 1.5, width: 40, height: 40, color: "#f0f1f2", "font-size": 11.5, "font-weight": 600, "text-max-width": 150 } },
      { selector: 'node.editorial-node[type = "target"]', style: { "background-color": "#8f84b7", "border-color": "#b4acce", width: 24, height: 24 } },
      { selector: 'node.editorial-node[type = "indication"]', style: { "background-color": "#b56f86", "border-color": "#d49aab", width: 24, height: 24 } },
      { selector: 'node.editorial-node[type = "patent_family"]', style: { "background-color": "#6f8fb9", "border-color": "#9bb1ce", "border-width": 1.5, width: 32, height: 32, "font-size": 8.4, "font-weight": 600, "text-wrap": "wrap", "text-max-width": 108 } },
      { selector: 'node.editorial-node[type = "patent_document"]', style: { "background-color": "#5f9e92", "border-color": "#8cbab1", width: 19, height: 19 } },
      { selector: 'node.editorial-node[type = "claim"]', style: { "background-color": "#c49a5a", "border-color": "#d9ba86", width: 23, height: 23, "text-max-width": 96 } },
      { selector: 'node.editorial-node[type = "evidence"]', style: { "background-color": "#c97264", "border-color": "#dd9a90", width: 19, height: 19 } },
      { selector: 'node.editorial-node[type = "applicant"]', style: { "background-color": "#87909a", "border-color": "#a6adb5", width: 18, height: 18 } },
      { selector: 'node.editorial-node[type = "jurisdiction"]', style: { "background-color": "#668fa0", "border-color": "#8aabb8", width: 16, height: 16 } },
      { selector: 'node.editorial-node[type = "technology_theme"]', style: { "background-color": "#899f68", "border-color": "#adbc92", width: 21, height: 21, "text-max-width": 104 } },
      { selector: 'node.editorial-node[type = "causal_concept"]', style: { "background-color": "#9bb2d0", "border-color": "#c5d2e2", "border-width": 1.4, width: 26, height: 26, "font-size": 9.2, "font-weight": 600, "text-max-width": 116 } },
      { selector: 'node.editorial-node[type = "source"]', style: { "background-color": "#6e7378", "border-color": "#8a8f94", width: 12, height: 12, color: "#b9bec3", "font-size": 8 } },
      { selector: 'node.corridor-node[type = "research_object"]', style: { width: 46, height: 46 } },
      { selector: 'node.corridor-node[type = "target"]', style: { width: 27, height: 27 } },
      { selector: 'node.corridor-node[type = "indication"]', style: { width: 27, height: 27 } },
      { selector: 'node.corridor-node[type = "patent_family"]', style: { width: 36, height: 36, "border-width": 1.8 } },
      { selector: 'node.corridor-node[type = "technology_theme"]', style: { width: 24, height: 24 } },
      { selector: 'node.corridor-node[type = "claim"]', style: { width: 26, height: 26, "text-max-width": 102 } },
      { selector: "node.depth-aware", style: { width: "data(visualSize)", height: "data(visualSize)", opacity: "data(depthOpacity)", "text-opacity": "data(labelOpacity)", "z-index": "data(depthOrder)", "z-index-compare": "manual", "shadow-color": "#050607", "shadow-blur": "data(shadowBlur)", "shadow-opacity": "data(shadowOpacity)", "shadow-offset-x": 0, "shadow-offset-y": "data(shadowOffset)" } },
      {
        selector: "edge",
        style: {
          width: 0.8,
          "line-color": "#555b61",
          "target-arrow-color": "#555b61",
          "target-arrow-shape": "none",
          "arrow-scale": 0.62,
          "curve-style": "bezier",
          opacity: 0.34,
        },
      },
      { selector: 'edge[assertion = "rule_derived"]', style: { "line-style": "dashed" } },
      { selector: 'edge[assertion = "model_inference"]', style: { "line-style": "dotted", opacity: 0.25 } },
      { selector: 'edge[relationKind = "causal"]', style: { "line-color": "#9bb2d0", "target-arrow-color": "#9bb2d0", "target-arrow-shape": "triangle", "line-style": "solid", width: 1.8, opacity: 0.68 } },
      { selector: 'edge[relationKind = "mechanistic"]', style: { "line-color": "#5f9e92", "target-arrow-color": "#5f9e92", "target-arrow-shape": "triangle", "line-style": "solid", width: 1.45, opacity: 0.62 } },
      { selector: 'edge[relationKind = "associative"]', style: { "line-color": "#87909a", "target-arrow-color": "#87909a", "target-arrow-shape": "triangle-tee", "line-style": "dotted", width: 1.05, opacity: 0.48 } },
      { selector: 'edge[relationKind = "temporal"]', style: { "line-color": "#c49a5a", "target-arrow-color": "#c49a5a", "target-arrow-shape": "triangle", "line-style": "dashed", width: 1.05, opacity: 0.5 } },
      { selector: 'edge[relationKind = "evidentiary"]', style: { "line-color": "#c97264", "target-arrow-color": "#c97264", "line-style": "dashed", width: 0.95, opacity: 0.44 } },
      { selector: 'edge[type = "SUPPORTED_BY"]', style: { "line-color": "#655156", "target-arrow-color": "#655156" } },
      { selector: 'edge[type = "PROTECTS"]', style: { "line-color": "#5b6250", "target-arrow-color": "#5b6250" } },
      { selector: 'edge[type = "FILED_BY"]', style: { "line-color": "#555b61", "target-arrow-color": "#555b61" } },
      { selector: "edge.corridor-edge", style: { "curve-style": "straight", opacity: 0.3 } },
      { selector: "edge.depth-aware", style: { width: "data(visualWidth)", opacity: "data(depthOpacity)", "z-index": "data(depthOrder)", "z-index-compare": "manual" } },
      { selector: "node.galaxy-node", style: { "background-color": "data(galaxyColor)", "border-color": "data(galaxyBorderColor)", "border-width": "data(galaxyBorderWidth)", width: "data(galaxyNodeSize)", height: "data(galaxyNodeSize)", "font-size": "data(galaxyFontSize)", "font-weight": "data(galaxyFontWeight)", "text-opacity": "data(galaxyLabelOpacity)", "text-outline-opacity": 0.9, "text-outline-width": 1.4, "text-margin-y": "data(galaxyTextOffset)", "shadow-color": "data(galaxyColor)", "shadow-blur": "data(galaxyGlowBlur)", "shadow-opacity": "data(galaxyGlowOpacity)", "shadow-offset-x": 0, "shadow-offset-y": 0 } },
      { selector: "node.galaxy-node:selected", style: { "border-color": "#fff5e8", "border-width": 3, "shadow-color": "data(galaxyColor)", "shadow-blur": 38, "shadow-opacity": 0.94, "underlay-color": "data(galaxyColor)", "underlay-opacity": 0.22, "underlay-padding": 16, "font-weight": 700, "text-opacity": 1 } },
      { selector: "edge.galaxy-edge", style: { "curve-style": "unbundled-bezier", "control-point-distances": "data(galaxyCurveDistance)", "control-point-weights": 0.5, "line-color": "data(galaxyColor)", "target-arrow-color": "data(galaxyColor)", width: "data(galaxyEdgeWidth)", opacity: "data(galaxyEdgeOpacity)", "line-cap": "round", "target-arrow-shape": "none" } },
      { selector: "edge.edge-active", style: { label: "data(label)", width: 1.8, opacity: 0.96, color: "#c9ced3", "font-size": 8, "font-weight": 600, "target-arrow-shape": "triangle", "text-rotation": "autorotate", "text-background-color": "#1c1f22", "text-background-opacity": 0.92, "text-background-padding": 2, "text-margin-y": -7, "z-index": 8 } },
      { selector: "edge.incoming-active", style: { "line-color": "#5f9e92", "target-arrow-color": "#5f9e92" } },
      { selector: "edge.outgoing-active", style: { "line-color": "#c49a5a", "target-arrow-color": "#c49a5a" } },
      { selector: "node:selected", style: { "border-color": "#f0ede7", "border-width": 2.4, "underlay-color": "#d9dde1", "underlay-opacity": 0.13, "underlay-padding": 9, "z-index": 999, "z-index-compare": "manual" } },
      { selector: "edge:selected", style: { width: 2.2, opacity: 1, "overlay-color": "#d9dde1", "overlay-opacity": 0.06 } },
      { selector: ".faded", style: { opacity: 0.07, "text-opacity": 0.04 } },
    ],
  });

  const SPRING_STIFFNESS = 13.2;
  const DAMPING_COEFFICIENT = 5.1;
  const COULOMB_STRENGTH = 9200;
  const ANCHOR_STIFFNESS = 0.62;
  const COLLISION_STIFFNESS = 15;
  const WAVE_SPEED = 760;
  const WAVE_DECAY = 3.1;
  const WAVE_SPATIAL_DECAY = 0.0018;
  const WAVE_FREQUENCY = Math.PI * 13;
  const MAX_PHYSICS_SPEED = 390;
  const MAX_PHYSICS_OFFSET = 260;
  const DRAG_NEIGHBOR_COUPLING = 0.28;
  const DEPTH_TAP_RADIUS = 14;
  const DEPTH_TAP_WINDOW_MS = 1100;
  const STAR_TRAIL_FRAME_MS = 24;
  const CAMERA_CRUISE_FRAME_MS = 24;

  const motionAnchors = new Map();
  const motionVelocities = new Map();
  const springRestLengths = new Map();
  const physicsWaves = [];
  let motionFrame = 0;
  let lastMotionTick = 0;
  let lastPhysicsTimestamp = 0;
  let lastViewportInteraction = 0;
  let physicsActiveUntil = 0;
  let physicsStillMoving = false;
  let draggedNodeId = "";
  let lastDragSample = null;
  let lastWaveEmission = 0;
  let depthTapCycle = null;
  let motionCenter = { x: 0, y: 0 };
  let orbitStartedAt = performance.now();
  let galaxyStatsFrames = 0;
  let galaxyStatsWindowStarted = performance.now();
  let galaxyFps = 0;
  const starTrailCanvas = byId("star-trail-canvas");
  const starTrailContext = starTrailCanvas?.getContext("2d");
  let starTrailWidth = 0;
  let starTrailHeight = 0;
  let lastStarTrailFrame = 0;
  let starTrailEdges = [];
  const trailPointScratch = { x: 0, y: 0 };
  const trailControlScratch = { x: 0, y: 0 };
  let cruiseBaseline = null;
  let cruiseStartedAt = performance.now();
  let lastCameraCruiseFrame = 0;
  let programmaticViewportUntil = 0;

  function velocityFor(nodeId) {
    if (!motionVelocities.has(nodeId)) motionVelocities.set(nodeId, { x: 0, y: 0 });
    return motionVelocities.get(nodeId);
  }

  function coupleNeighborVelocity(node, dragVelocity) {
    node.connectedEdges().forEach((edge) => {
      const neighbor = edge.source().id() === node.id() ? edge.target() : edge.source();
      if (neighbor.grabbed()) return;
      const influence = DRAG_NEIGHBOR_COUPLING / Math.sqrt(Math.max(1, neighbor.degree()));
      const velocity = velocityFor(neighbor.id());
      velocity.x += (dragVelocity.x - velocity.x) * influence;
      velocity.y += (dragVelocity.y - velocity.y) * influence;
    });
  }

  function captureSpringRestLengths() {
    springRestLengths.clear();
    cy.edges().forEach((edge) => {
      const source = edge.source().position();
      const target = edge.target().position();
      springRestLengths.set(edge.id(), Math.max(24, Math.hypot(target.x - source.x, target.y - source.y)));
    });
  }

  function captureMotionAnchors() {
    motionAnchors.clear();
    motionVelocities.clear();
    cy.nodes().forEach((node) => {
      const position = node.position();
      motionAnchors.set(node.id(), { x: position.x, y: position.y });
      motionVelocities.set(node.id(), { x: 0, y: 0 });
    });
    const anchors = [...motionAnchors.values()];
    motionCenter = anchors.length
      ? anchors.reduce((center, position) => ({ x: center.x + position.x / anchors.length, y: center.y + position.y / anchors.length }), { x: 0, y: 0 })
      : { x: 0, y: 0 };
    captureSpringRestLengths();
    lastPhysicsTimestamp = 0;
  }

  function emitPhysicsWave(node, dragVelocity, amplitudeScale = 1) {
    const speed = Math.hypot(dragVelocity.x, dragVelocity.y);
    const phase = Number(node.data("motionPhase") || 0);
    const direction = speed > 0.01
      ? { x: dragVelocity.x / speed, y: dragVelocity.y / speed }
      : { x: Math.cos(phase), y: Math.sin(phase) };
    const position = node.position();
    physicsWaves.push({
      sourceId: node.id(),
      origin: { x: position.x, y: position.y },
      direction,
      startedAt: performance.now(),
      amplitude: clamp((150 + (speed * 0.72)) * amplitudeScale, 110, 620),
    });
    while (physicsWaves.length > 7) physicsWaves.shift();
    physicsActiveUntil = performance.now() + 2600;
  }

  // Hooke springs + Coulomb repulsion + viscous damping, integrated with a
  // bounded semi-implicit Euler step so interactive impulses remain stable.
  function stepGraphPhysics(timestamp) {
    const deltaTime = lastPhysicsTimestamp
      ? clamp((timestamp - lastPhysicsTimestamp) / 1000, 1 / 120, 1 / 30)
      : 1 / 60;
    lastPhysicsTimestamp = timestamp;
    const nodes = cy.nodes().toArray();
    const forces = new Map(nodes.map((node) => [node.id(), { x: 0, y: 0 }]));

    cy.edges().forEach((edge) => {
      const source = edge.source();
      const target = edge.target();
      const sourcePosition = source.position();
      const targetPosition = target.position();
      const dx = targetPosition.x - sourcePosition.x;
      const dy = targetPosition.y - sourcePosition.y;
      const distance = Math.max(0.001, Math.hypot(dx, dy));
      const restLength = springRestLengths.get(edge.id()) || distance;
      const extension = distance - restLength;
      const degreeScale = 1 / Math.sqrt(Math.max(1, Math.min(source.degree(), target.degree())));
      const springForce = SPRING_STIFFNESS * extension * (0.58 + (degreeScale * 0.42));
      const fx = (dx / distance) * springForce;
      const fy = (dy / distance) * springForce;
      const sourceForce = forces.get(source.id());
      const targetForce = forces.get(target.id());
      sourceForce.x += fx;
      sourceForce.y += fy;
      targetForce.x -= fx;
      targetForce.y -= fy;
    });

    for (let leftIndex = 0; leftIndex < nodes.length; leftIndex += 1) {
      const left = nodes[leftIndex];
      const leftPosition = left.position();
      for (let rightIndex = leftIndex + 1; rightIndex < nodes.length; rightIndex += 1) {
        const right = nodes[rightIndex];
        const rightPosition = right.position();
        let dx = rightPosition.x - leftPosition.x;
        let dy = rightPosition.y - leftPosition.y;
        let distance = Math.hypot(dx, dy);
        if (distance < 0.001) {
          const phase = Number(right.data("motionPhase") || 0);
          dx = Math.cos(phase) * 0.01;
          dy = Math.sin(phase) * 0.01;
          distance = 0.01;
        }
        const minimumDistance = 10 + ((Number(left.data("visualSize")) + Number(right.data("visualSize"))) * 0.55);
        const coulombForce = (COULOMB_STRENGTH * state.galaxySettings.pressure) / ((distance * distance) + 144);
        const collisionForce = distance < minimumDistance
          ? (minimumDistance - distance) * COLLISION_STIFFNESS
          : 0;
        const repulsion = coulombForce + collisionForce;
        const fx = (dx / distance) * repulsion;
        const fy = (dy / distance) * repulsion;
        forces.get(left.id()).x -= fx;
        forces.get(left.id()).y -= fy;
        forces.get(right.id()).x += fx;
        forces.get(right.id()).y += fy;
      }
    }

    nodes.forEach((node) => {
      const anchor = motionAnchors.get(node.id());
      if (!anchor) return;
      const position = node.position();
      const force = forces.get(node.id());
      force.x += (anchor.x - position.x) * ANCHOR_STIFFNESS;
      force.y += (anchor.y - position.y) * ANCHOR_STIFFNESS;
      const phase = Number(node.data("motionPhase") || 0);
      physicsWaves.forEach((wave) => {
        if (wave.sourceId === node.id()) return;
        const dx = position.x - wave.origin.x;
        const dy = position.y - wave.origin.y;
        const distance = Math.max(0.001, Math.hypot(dx, dy));
        const elapsed = (timestamp - wave.startedAt) / 1000;
        const localTime = elapsed - (distance / WAVE_SPEED);
        if (localTime < 0 || localTime > 1.8) return;
        const envelope = wave.amplitude
          * Math.exp(-WAVE_DECAY * localTime)
          * Math.exp(-WAVE_SPATIAL_DECAY * distance);
        const oscillation = Math.sin((WAVE_FREQUENCY * localTime) - (distance * 0.034) + phase);
        const radialX = dx / distance;
        const radialY = dy / distance;
        force.x += ((radialX * 0.68) + (wave.direction.x * 0.32)) * envelope * oscillation;
        force.y += ((radialY * 0.68) + (wave.direction.y * 0.32)) * envelope * oscillation;
      });
    });

    for (let index = physicsWaves.length - 1; index >= 0; index -= 1) {
      if ((timestamp - physicsWaves[index].startedAt) > 2600) physicsWaves.splice(index, 1);
    }

    const damping = Math.exp(-DAMPING_COEFFICIENT * deltaTime);
    let kineticEnergy = 0;
    cy.batch(() => {
      nodes.forEach((node) => {
        if (node.grabbed()) return;
        const anchor = motionAnchors.get(node.id());
        const force = forces.get(node.id());
        if (!anchor || !force) return;
        const velocity = velocityFor(node.id());
        const mass = 0.72 + (Number(node.data("visualSize") || 15) / 34);
        velocity.x = (velocity.x + ((force.x / mass) * deltaTime)) * damping;
        velocity.y = (velocity.y + ((force.y / mass) * deltaTime)) * damping;
        const speed = Math.hypot(velocity.x, velocity.y);
        if (speed > MAX_PHYSICS_SPEED) {
          const scale = MAX_PHYSICS_SPEED / speed;
          velocity.x *= scale;
          velocity.y *= scale;
        }
        const position = node.position();
        let nextX = position.x + (velocity.x * deltaTime);
        let nextY = position.y + (velocity.y * deltaTime);
        const offsetX = nextX - anchor.x;
        const offsetY = nextY - anchor.y;
        const offset = Math.hypot(offsetX, offsetY);
        if (offset > MAX_PHYSICS_OFFSET) {
          const scale = MAX_PHYSICS_OFFSET / offset;
          nextX = anchor.x + (offsetX * scale);
          nextY = anchor.y + (offsetY * scale);
          velocity.x *= 0.45;
          velocity.y *= 0.45;
        }
        node.position({ x: nextX, y: nextY });
        kineticEnergy += (velocity.x * velocity.x) + (velocity.y * velocity.y);
      });
    });
    return draggedNodeId || physicsWaves.length || timestamp < physicsActiveUntil || kineticEnergy > 0.8;
  }

  function applyAmbientDrift(timestamp) {
    const seconds = timestamp / 1000;
    const orbitAngle = state.galaxySettings.autoOrbit && !prefersReducedMotion
      ? ((timestamp - orbitStartedAt) / 1000) * (0.004 + (state.galaxySettings.orbitStrength * 0.012))
      : 0;
    const orbitCosine = Math.cos(orbitAngle);
    const orbitSine = Math.sin(orbitAngle);
    cy.batch(() => {
      cy.nodes().forEach((node) => {
        if (node.grabbed()) return;
        const anchor = motionAnchors.get(node.id());
        if (!anchor) return;
        const depth = Number(node.data("spatialDepth") || 0.3);
        const phase = Number(node.data("motionPhase") || 0);
        const amplitude = 0.5 + (depth * 1.35);
        const anchorX = anchor.x - motionCenter.x;
        const anchorY = anchor.y - motionCenter.y;
        const orbitX = motionCenter.x + (anchorX * orbitCosine) - (anchorY * orbitSine);
        const orbitY = motionCenter.y + (anchorX * orbitSine) + (anchorY * orbitCosine);
        node.position({
          x: orbitX + (Math.sin((seconds * 0.62) + phase) * amplitude),
          y: orbitY + (Math.cos((seconds * 0.54) + (phase * 1.17)) * amplitude * 0.68),
        });
      });
    });
  }

  function animateAmbientMotion(timestamp) {
    motionFrame = 0;
    if (!state.motionEnabled || document.hidden || !motionAnchors.size) return;
    updateGalaxyStats(timestamp, true);
    const simulationDue = (timestamp - lastMotionTick) >= 16;
    const viewportReady = draggedNodeId || (timestamp - lastViewportInteraction) >= 180;
    if (simulationDue && viewportReady) {
      const physicsActive = draggedNodeId || physicsWaves.length || timestamp < physicsActiveUntil || physicsStillMoving;
      physicsStillMoving = physicsActive ? Boolean(stepGraphPhysics(timestamp)) : false;
      if (!physicsStillMoving) {
        lastPhysicsTimestamp = 0;
        applyAmbientDrift(timestamp);
      }
      lastMotionTick = timestamp;
    }
    applyCameraCruise(timestamp);
    renderStarTrails(timestamp);
    startAmbientMotion();
  }

  function startAmbientMotion() {
    if (state.motionEnabled && !motionFrame) {
      motionFrame = window.requestAnimationFrame(animateAmbientMotion);
    }
  }

  function stopAmbientMotion(restoreAnchors = true) {
    if (motionFrame) window.cancelAnimationFrame(motionFrame);
    motionFrame = 0;
    lastPhysicsTimestamp = 0;
    physicsWaves.length = 0;
    physicsActiveUntil = 0;
    physicsStillMoving = false;
    draggedNodeId = "";
    motionVelocities.forEach((velocity) => {
      velocity.x = 0;
      velocity.y = 0;
    });
    if (!restoreAnchors) return;
    cy.batch(() => {
      cy.nodes().forEach((node) => {
        const anchor = motionAnchors.get(node.id());
        if (anchor && !node.grabbed()) node.position(anchor);
      });
    });
  }

  function updateMotionControl() {
    const button = byId("motion-toggle");
    button.setAttribute("aria-pressed", String(state.motionEnabled));
    button.textContent = state.motionEnabled ? "力场 开" : "力场 关";
  }

  function setMotionEnabled(enabled) {
    state.motionEnabled = enabled;
    updateMotionControl();
    if (enabled) {
      if (!motionAnchors.size) captureMotionAnchors();
      startAmbientMotion();
    } else {
      stopAmbientMotion(true);
    }
    updateGalaxyStats();
  }

  function updateZoomLevel() {
    byId("zoom-level").textContent = `${Math.round(cy.zoom() * 100)}%`;
  }

  function updateGalaxyStats(timestamp = performance.now(), sampleFrame = false) {
    if (sampleFrame) galaxyStatsFrames += 1;
    const elapsed = timestamp - galaxyStatsWindowStarted;
    if (sampleFrame && elapsed >= 700) {
      galaxyFps = Math.round((galaxyStatsFrames * 1000) / elapsed);
      galaxyStatsFrames = 0;
      galaxyStatsWindowStarted = timestamp;
    }
    const degrees = cy.nodes().map((node) => node.degree());
    const maxDegree = Math.max(0, ...degrees);
    const hubThreshold = Math.max(3, Math.ceil(maxDegree * 0.45));
    const hubCount = cy.nodes().filter((node) => node.degree() >= hubThreshold).length;
    byId("galaxy-fps").textContent = state.motionEnabled && galaxyFps ? String(galaxyFps) : "—";
    byId("galaxy-stat-nodes").textContent = String(cy.nodes().length);
    byId("galaxy-stat-links").textContent = String(cy.edges().length);
    byId("galaxy-stat-hubs").textContent = String(hubCount);
  }

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
    const explorationDepth = state.localFocus ? 1 : state.depth;
    let selected = seedIds.length
      ? collectNeighborhood(seedIds, explorationDepth, eligibleNodes, eligibleEdges)
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

  const clamp = (value, min, max) => Math.min(max, Math.max(min, value));
  const stableDepthNoise = (id) => {
    const hash = [...String(id)].reduce((total, character) => ((total * 31) + character.charCodeAt(0)) % 997, 17);
    return ((hash / 996) - 0.5) * 0.16;
  };
  const stableMotionPhase = (id) => {
    const hash = [...String(id)].reduce((total, character) => ((total * 37) + character.charCodeAt(0)) % 991, 23);
    return (hash / 990) * Math.PI * 2;
  };
  const stableGalaxyHash = (id) => [...String(id)]
    .reduce((total, character) => ((total * 41) + character.charCodeAt(0)) % 104729, 29);

  function quadraticCurvePoint(source, control, target, progress, output = {}) {
    const inverse = 1 - progress;
    output.x = (inverse * inverse * source.x) + (2 * inverse * progress * control.x) + (progress * progress * target.x);
    output.y = (inverse * inverse * source.y) + (2 * inverse * progress * control.y) + (progress * progress * target.y);
    return output;
  }

  function galaxyRgba(color, alpha) {
    const hex = String(color || "#8f989f").replace("#", "");
    const normalized = hex.length === 3 ? [...hex].map((value) => value + value).join("") : hex;
    const value = Number.parseInt(normalized, 16);
    if (!Number.isFinite(value)) return `rgba(143, 152, 159, ${alpha})`;
    return `rgba(${(value >> 16) & 255}, ${(value >> 8) & 255}, ${value & 255}, ${alpha})`;
  }

  function sizeStarTrailCanvas() {
    if (!starTrailCanvas || !starTrailContext) return false;
    const width = Math.max(1, Math.round(starTrailCanvas.clientWidth));
    const height = Math.max(1, Math.round(starTrailCanvas.clientHeight));
    const density = Math.min(window.devicePixelRatio || 1, 2);
    if (width !== starTrailWidth || height !== starTrailHeight || starTrailCanvas.width !== Math.round(width * density)) {
      starTrailWidth = width;
      starTrailHeight = height;
      starTrailCanvas.width = Math.round(width * density);
      starTrailCanvas.height = Math.round(height * density);
      starTrailContext.setTransform(density, 0, 0, density, 0, 0);
    }
    return true;
  }

  function rebuildStarTrailCache() {
    const settings = state.galaxySettings;
    starTrailEdges = cy.edges().slice(0, 140).map((edge) => ({
      edge,
      source: edge.source(),
      target: edge.target(),
      hash: stableGalaxyHash(edge.id()),
      curveDistance: Number(edge.data("galaxyCurveDistance") || 0) * 0.58,
      color: edge.data("galaxyColor") || "#8f989f",
      opacity: Number(edge.data("galaxyEdgeOpacity") || settings.edgeOpacity),
    }));
  }

  function renderStarTrails(timestamp) {
    if (!starTrailContext) return;
    if ((!starTrailWidth || !starTrailHeight) && !sizeStarTrailCanvas()) return;
    if ((timestamp - lastStarTrailFrame) < STAR_TRAIL_FRAME_MS) return;
    lastStarTrailFrame = timestamp;
    starTrailContext.clearRect(0, 0, starTrailWidth, starTrailHeight);
    const settings = state.galaxySettings;
    const configuredStrandCount = Math.round(settings.trailDensity);
    const interactionActive = draggedNodeId || (timestamp - lastViewportInteraction) < 240;
    const strandCount = interactionActive ? Math.min(2, configuredStrandCount) : configuredStrandCount;
    if (!strandCount || settings.preset === "minimal" || !starTrailEdges.length) return;

    starTrailContext.save();
    starTrailContext.globalCompositeOperation = "lighter";
    const zoom = cy.zoom();
    starTrailEdges.forEach((trailEdge) => {
      const edge = trailEdge.edge;
      const source = trailEdge.source.renderedPosition();
      const target = trailEdge.target.renderedPosition();
      const dx = target.x - source.x;
      const dy = target.y - source.y;
      const length = Math.max(1, Math.hypot(dx, dy));
      const normalX = -dy / length;
      const normalY = dx / length;
      const hash = trailEdge.hash;
      const baseCurve = trailEdge.curveDistance * zoom;
      const color = trailEdge.color;
      const interactionScale = edge.hasClass("faded") ? 0.08 : edge.hasClass("edge-active") ? 1.7 : 1;
      const opacity = trailEdge.opacity * interactionScale;
      let pulseControlX = 0;
      let pulseControlY = 0;

      for (let strand = 0; strand < strandCount; strand += 1) {
        const offset = (strand - ((strandCount - 1) / 2)) * (1.7 + ((hash % 7) * 0.15));
        const controlX = (source.x + target.x) / 2 + (normalX * (baseCurve + offset));
        const controlY = (source.y + target.y) / 2 + (normalY * (baseCurve + offset));
        if (strand === Math.floor(strandCount / 2)) {
          pulseControlX = controlX;
          pulseControlY = controlY;
        }
        starTrailContext.beginPath();
        starTrailContext.moveTo(source.x, source.y);
        starTrailContext.quadraticCurveTo(controlX, controlY, target.x, target.y);
        starTrailContext.strokeStyle = galaxyRgba(color, clamp(opacity * (0.16 + (strand * 0.045)), 0.025, 0.24));
        starTrailContext.lineWidth = 0.34 + (((hash + strand) % 5) * 0.08);
        starTrailContext.stroke();
      }

      if (!interactionActive && settings.preset === "atlas" && hash % 3 === 0) {
        const progress = ((timestamp * 0.000055) + ((hash % 1000) / 1000)) % 1;
        trailControlScratch.x = pulseControlX;
        trailControlScratch.y = pulseControlY;
        const point = quadraticCurvePoint(source, trailControlScratch, target, progress, trailPointScratch);
        const pulse = starTrailContext.createRadialGradient(point.x, point.y, 0, point.x, point.y, 4.5);
        pulse.addColorStop(0, galaxyRgba(color, 0.78));
        pulse.addColorStop(0.3, galaxyRgba(color, 0.36));
        pulse.addColorStop(1, galaxyRgba(color, 0));
        starTrailContext.fillStyle = pulse;
        starTrailContext.beginPath();
        starTrailContext.arc(point.x, point.y, 4.5, 0, Math.PI * 2);
        starTrailContext.fill();
      }
    });

    const selected = cy.nodes(":selected").toArray()[0] || cy.getElementById(state.focus).toArray()[0];
    if (selected) {
      const position = selected.renderedPosition();
      const color = selected.data("galaxyColor") || "#e5e0d6";
      const radius = 34 + (Math.sin(timestamp * 0.0024) * 5);
      const halo = starTrailContext.createRadialGradient(position.x, position.y, 0, position.x, position.y, radius);
      halo.addColorStop(0, galaxyRgba(color, 0.42));
      halo.addColorStop(0.16, galaxyRgba(color, 0.16));
      halo.addColorStop(1, galaxyRgba(color, 0));
      starTrailContext.fillStyle = halo;
      starTrailContext.beginPath();
      starTrailContext.arc(position.x, position.y, radius, 0, Math.PI * 2);
      starTrailContext.fill();
    }
    starTrailContext.restore();
  }

  function captureCruiseBaseline() {
    cruiseBaseline = { zoom: cy.zoom(), pan: { ...cy.pan() } };
    cruiseStartedAt = performance.now();
  }

  function applyCameraCruise(timestamp) {
    if (!state.galaxySettings.cameraCruise || prefersReducedMotion || draggedNodeId) return;
    if (timestamp < programmaticViewportUntil) return;
    if ((timestamp - lastViewportInteraction) < 1600) return;
    if ((timestamp - lastCameraCruiseFrame) < CAMERA_CRUISE_FRAME_MS) return;
    lastCameraCruiseFrame = timestamp;
    if (!cruiseBaseline) captureCruiseBaseline();
    const seconds = (timestamp - cruiseStartedAt) / 1000;
    const zoom = clamp(cruiseBaseline.zoom * (1 + (Math.sin(seconds * 0.2) * 0.035)), cy.minZoom(), cy.maxZoom());
    const pan = {
      x: cruiseBaseline.pan.x + (Math.sin(seconds * 0.17) * 10),
      y: cruiseBaseline.pan.y + (Math.cos(seconds * 0.13) * 7),
    };
    programmaticViewportUntil = timestamp + 80;
    cy.viewport({ zoom, pan });
  }

  function flyCameraToNode(node) {
    if (state.galaxySettings.preset !== "atlas" || prefersReducedMotion || !node?.length) return;
    const zoom = clamp(Math.max(cy.zoom(), 0.78) * 1.08, 0.62, 1.42);
    const position = node.position();
    const pan = { x: (cy.width() / 2) - (position.x * zoom), y: (cy.height() / 2) - (position.y * zoom) };
    programmaticViewportUntil = performance.now() + 760;
    cruiseBaseline = null;
    cy.animate({ pan, zoom, duration: 620, easing: "ease-in-out-cubic" });
    window.setTimeout(captureCruiseBaseline, 660);
  }

  function computeSpatialMetrics(view) {
    const degreeById = new Map(view.nodes.map((node) => [node.id, 0]));
    view.edges.forEach((edge) => {
      degreeById.set(edge.source, (degreeById.get(edge.source) || 0) + 1);
      degreeById.set(edge.target, (degreeById.get(edge.target) || 0) + 1);
    });
    const maxDegree = Math.max(1, ...degreeById.values());
    const nodes = new Map();
    view.nodes.forEach((node) => {
      const centrality = Math.sqrt((degreeById.get(node.id) || 0) / maxDegree);
      const depth = node.id === state.focus
        ? 1
        : clamp(0.24 + (centrality * 0.62) + stableDepthNoise(node.id), 0.22, 0.92);
      const baseSize = nodeBaseSizes[node.type] || 15;
      nodes.set(node.id, {
        spatialDepth: Number(depth.toFixed(3)),
        motionPhase: Number(stableMotionPhase(node.id).toFixed(4)),
        visualSize: Number((baseSize * (0.74 + (depth * 0.36))).toFixed(1)),
        depthOpacity: Number((0.43 + (depth * 0.57)).toFixed(2)),
        labelOpacity: Number((0.38 + (depth * 0.62)).toFixed(2)),
        depthOrder: Math.round(depth * 100),
        shadowBlur: Number((2 + (depth * 11)).toFixed(1)),
        shadowOpacity: Number((0.08 + (depth * 0.3)).toFixed(2)),
        shadowOffset: Number((1 + (depth * 4)).toFixed(1)),
      });
    });
    const edges = new Map();
    view.edges.forEach((edge) => {
      const sourceDepth = nodes.get(edge.source)?.spatialDepth || 0.3;
      const targetDepth = nodes.get(edge.target)?.spatialDepth || 0.3;
      const depth = (sourceDepth + targetDepth) / 2;
      edges.set(edge.id, {
        visualWidth: Number((0.48 + (depth * 0.72)).toFixed(2)),
        depthOpacity: Number((0.12 + (depth * 0.32)).toFixed(2)),
        depthOrder: Math.max(1, Math.round(depth * 50)),
      });
    });
    return { nodes, edges };
  }

  function computeGalaxyMetrics(view) {
    const settings = state.galaxySettings;
    const degreeById = new Map(view.nodes.map((node) => [node.id, 0]));
    view.edges.forEach((edge) => {
      degreeById.set(edge.source, (degreeById.get(edge.source) || 0) + 1);
      degreeById.set(edge.target, (degreeById.get(edge.target) || 0) + 1);
    });
    const maxDegree = Math.max(1, ...degreeById.values());
    const nodes = new Map();
    view.nodes.forEach((node) => {
      const degree = degreeById.get(node.id) || 0;
      const degreeCentrality = Math.sqrt(degree / maxDegree);
      const typeSize = nodeBaseSizes[node.type] || 15;
      const rawSize = settings.sizeMode === "uniform"
        ? 17
        : settings.sizeMode === "type"
          ? typeSize
          : 9 + (degreeCentrality * 39) + (node.id === state.focus ? 5 : 0);
      const galaxyNodeSize = clamp(rawSize * settings.nodeScale, 7, 62);
      const galaxyFontSize = clamp((6.2 + (degreeCentrality * 9.8)) * Math.sqrt(settings.nodeScale), 6, 18);
      const galaxyColor = GALAXY_TYPE_COLORS[node.type] || "#8f989f";
      nodes.set(node.id, {
        degree,
        degreeCentrality: Number(degreeCentrality.toFixed(4)),
        galaxyColor,
        galaxyBorderColor: galaxyColor,
        galaxyNodeSize: Number(galaxyNodeSize.toFixed(1)),
        galaxyFontSize: Number(galaxyFontSize.toFixed(1)),
        galaxyFontWeight: degreeCentrality > 0.58 ? 600 : 500,
        galaxyLabelOpacity: Number(clamp(0.38 + (degreeCentrality * 0.76), 0.38, 1).toFixed(2)),
        galaxyGlowBlur: Number((3 + (degreeCentrality * 20 * settings.glowStrength)).toFixed(1)),
        galaxyGlowOpacity: Number((settings.glowStrength * (0.1 + (degreeCentrality * 0.52))).toFixed(2)),
        galaxyBorderWidth: Number((0.7 + (degreeCentrality * 1.2)).toFixed(1)),
        galaxyTextOffset: Number((4 + (galaxyNodeSize * 0.18)).toFixed(1)),
      });
    });
    const edges = new Map();
    view.edges.forEach((edge) => {
      const source = nodes.get(edge.source);
      const target = nodes.get(edge.target);
      const centrality = ((source?.degreeCentrality || 0) + (target?.degreeCentrality || 0)) / 2;
      const hash = stableGalaxyHash(edge.id);
      const direction = hash % 2 ? 1 : -1;
      const curveMagnitude = (18 + (hash % 58)) * (0.36 + (settings.orbitStrength * 1.18));
      edges.set(edge.id, {
        galaxyColor: source?.galaxyColor || "#778087",
        galaxyCurveDistance: Number((direction * curveMagnitude).toFixed(1)),
        galaxyEdgeWidth: Number((0.34 + (centrality * 0.96)).toFixed(2)),
        galaxyEdgeOpacity: Number(clamp(settings.edgeOpacity * (0.56 + (centrality * 0.62)), 0.04, 0.92).toFixed(2)),
      });
    });
    return { nodes, edges };
  }

  function cytoscapeElements(view) {
    const spatialMetrics = computeSpatialMetrics(view);
    const galaxyMetrics = computeGalaxyMetrics(view);
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
          ...spatialMetrics.nodes.get(node.id),
          ...galaxyMetrics.nodes.get(node.id),
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
          relationKind: edge.relation_kind,
          causalStatus: edge.causal_status,
          polarity: edge.polarity,
          directness: edge.directness,
          evidenceLevel: edge.evidence_level,
          confidence: edge.confidence,
          rationale: edge.rationale,
          sourceUrls: edge.source_urls,
          linkMethods: edge.link_methods,
          evidenceIds: edge.evidence_ids,
          ...spatialMetrics.edges.get(edge.id),
          ...galaxyMetrics.edges.get(edge.id),
        },
      })),
    ];
  }

  function semanticPositions(preset) {
    const lanes = preset?.lanes || [];
    const width = Math.max(cy.width(), 640);
    const height = Math.max(cy.height(), 600);
    const maxRows = Math.max(5, Math.floor((height - 210) / 64));
    const horizontalPadding = 36;
    const laneWidth = (width - horizontalPadding * 2) / Math.max(lanes.length, 1);
    const top = 132;
    const bottom = 60;
    const positions = new Map();

    lanes.forEach((lane, laneIndex) => {
      const laneTypes = new Set(lane.node_types || []);
      const laneNodes = cy.nodes()
        .filter((node) => laneTypes.has(node.data("type")))
        .sort((left, right) => String(left.data("label")).localeCompare(String(right.data("label"))));
      const columnCount = Math.max(1, Math.ceil(laneNodes.length / maxRows));
      const innerWidth = Math.max(laneWidth - 20, 40);
      const columnWidth = innerWidth / columnCount;
      laneNodes.forEach((node, nodeIndex) => {
        const column = Math.floor(nodeIndex / maxRows);
        const row = nodeIndex % maxRows;
        const rowsInColumn = Math.min(maxRows, laneNodes.length - column * maxRows);
        const rowGap = Math.min(68, (height - top - bottom) / Math.max(rowsInColumn - 1, 1));
        const blockHeight = rowGap * Math.max(rowsInColumn - 1, 0);
        const y = top + (height - top - bottom - blockHeight) / 2 + row * rowGap;
        const x = horizontalPadding + laneIndex * laneWidth + 10 + columnWidth * (column + 0.5);
        positions.set(node.id(), { x, y });
      });
    });
    return (node) => positions.get(node.id()) || { x: width / 2, y: height / 2 };
  }

  function galaxyLayoutPositions() {
    const settings = state.galaxySettings;
    const width = Math.max(cy.width(), 720);
    const height = Math.max(cy.height(), 620);
    const center = { x: width / 2, y: height / 2 };
    const groups = new Map();
    cy.nodes().forEach((node) => {
      const group = GALAXY_GROUP_BY_TYPE.get(node.data("type")) ?? 5;
      if (!groups.has(group)) groups.set(group, []);
      groups.get(group).push(node);
    });
    const groupEntries = [...groups.entries()].sort(([left], [right]) => left - right);
    const positions = new Map();
    const clusterCount = Math.max(groupEntries.length, 1);
    const orbitRadiusX = Math.min(width * 0.31, 330) * settings.pressure;
    const orbitRadiusY = Math.min(height * 0.24, 220) * settings.pressure;

    groupEntries.forEach(([group, nodes], clusterIndex) => {
      const groupAngle = (-Math.PI / 2) + ((clusterIndex / clusterCount) * Math.PI * 2);
      let clusterRadiusScale = 1;
      if (settings.preset === "atlas") clusterRadiusScale = 0.72 + ((clusterIndex % 3) * 0.12);
      if (settings.preset === "spiral") clusterRadiusScale = 0.36 + ((clusterIndex + 1) / clusterCount) * 0.78;
      if (settings.preset === "nebula") clusterRadiusScale = 0.72 + ((stableGalaxyHash(group) % 24) / 100);
      const clusterTwist = settings.preset === "spiral" ? clusterIndex * 0.52 : 0;
      const clusterCenter = {
        x: center.x + (Math.cos(groupAngle + clusterTwist) * orbitRadiusX * clusterRadiusScale),
        y: center.y + (Math.sin(groupAngle + clusterTwist) * orbitRadiusY * clusterRadiusScale),
      };
      nodes.sort((left, right) => Number(right.data("degree")) - Number(left.data("degree")) || left.id().localeCompare(right.id()));
      nodes.forEach((node, nodeIndex) => {
        if (settings.preset === "atlas" && node.id() === state.focus) {
          positions.set(node.id(), center);
          return;
        }
        if (nodeIndex === 0) {
          positions.set(node.id(), clusterCenter);
          return;
        }
        const localAngle = (nodeIndex * GOLDEN_ANGLE) + groupAngle + (settings.orbitStrength * nodeIndex * 0.08);
        const localRadius = settings.linkDistance
          * Math.sqrt(nodeIndex)
          * (0.34 + (settings.pressure * 0.13))
          * (settings.preset === "nebula" ? 0.78 : 1);
        const flattening = settings.preset === "spiral" ? 0.58 : settings.preset === "nebula" ? 0.82 : 0.7;
        positions.set(node.id(), {
          x: clamp(clusterCenter.x + (Math.cos(localAngle) * localRadius), 54, width - 54),
          y: clamp(clusterCenter.y + (Math.sin(localAngle) * localRadius * flattening), 96, height - 48),
        });
      });
    });
    return (node) => positions.get(node.id()) || center;
  }

  function syncGalaxyControls() {
    const settings = state.galaxySettings;
    const values = {
      "galaxy-node-scale": settings.nodeScale,
      "galaxy-edge-opacity": settings.edgeOpacity,
      "galaxy-glow-strength": settings.glowStrength,
      "galaxy-trail-density": settings.trailDensity,
      "galaxy-link-distance": settings.linkDistance,
      "galaxy-pressure": settings.pressure,
      "galaxy-orbit-strength": settings.orbitStrength,
    };
    Object.entries(values).forEach(([id, value]) => {
      const input = byId(id);
      if (input) input.value = String(value);
    });
    byId("galaxy-size-mode").value = settings.sizeMode;
    byId("galaxy-starfield").checked = settings.starfield;
    byId("galaxy-twinkle").checked = settings.twinkle;
    byId("galaxy-auto-orbit").checked = settings.autoOrbit;
    byId("galaxy-camera-cruise").checked = settings.cameraCruise;
    byId("galaxy-node-scale-value").textContent = `${settings.nodeScale.toFixed(2)}×`;
    byId("galaxy-edge-opacity-value").textContent = `${Math.round(settings.edgeOpacity * 100)}%`;
    byId("galaxy-glow-strength-value").textContent = `${Math.round(settings.glowStrength * 100)}%`;
    byId("galaxy-trail-density-value").textContent = `${Math.round(settings.trailDensity)} 股`;
    byId("galaxy-link-distance-value").textContent = String(settings.linkDistance);
    byId("galaxy-pressure-value").textContent = `${settings.pressure.toFixed(2)}×`;
    byId("galaxy-orbit-strength-value").textContent = `${Math.round(settings.orbitStrength * 100)}%`;
    const presetLabels = { atlas: "Star Atlas", galaxy: "Galaxy", spiral: "Spiral", nebula: "Nebula", minimal: "Minimal" };
    byId("galaxy-preset-status").textContent = presetLabels[settings.preset] || "Custom";
    document.querySelectorAll("[data-galaxy-preset]").forEach((button) => {
      button.setAttribute("aria-pressed", String(button.dataset.galaxyPreset === settings.preset));
    });
  }

  function applyGalaxyAppearance() {
    const settings = state.galaxySettings;
    const panel = byId("main-content");
    const corridorMode = state.preset === "technology" && settings.preset === "minimal";
    panel.dataset.galaxyMode = settings.preset;
    panel.dataset.starfield = String(settings.starfield);
    panel.dataset.twinkle = String(settings.twinkle && !prefersReducedMotion);
    panel.dataset.trails = String(settings.trailDensity > 0);
    if (cy.nodes().length) {
      const view = {
        nodes: DATA.nodes.filter((node) => state.visibleNodeIds.has(node.id)),
        edges: DATA.edges.filter((edge) => state.visibleEdgeIds.has(edge.id)),
      };
      const metrics = computeGalaxyMetrics(view);
      cy.batch(() => {
        if (corridorMode) {
          cy.nodes().addClass("corridor-node");
          cy.edges().addClass("corridor-edge");
        } else {
          cy.nodes().removeClass("corridor-node");
          cy.edges().removeClass("corridor-edge");
        }
        cy.nodes().forEach((node) => {
          const values = metrics.nodes.get(node.id());
          if (values) node.data(values);
        });
        cy.edges().forEach((edge) => {
          const values = metrics.edges.get(edge.id());
          if (values) edge.data(values);
        });
      });
    }
    rebuildStarTrailCache();
    syncGalaxyControls();
    lastStarTrailFrame = 0;
    renderStarTrails(performance.now());
  }

  function applyGalaxyPreset(presetId) {
    const preset = GALAXY_PRESET_SETTINGS[presetId] || GALAXY_PRESET_SETTINGS.galaxy;
    state.galaxySettings = { ...preset };
    orbitStartedAt = performance.now();
    cruiseBaseline = null;
    applyGalaxyAppearance();
    renderTechnologyLanes({ nodes: DATA.nodes.filter((node) => state.visibleNodeIds.has(node.id)) });
    if (cy.nodes().length) runLayout();
  }

  function persistGalaxySettings() {
    const button = byId("galaxy-save");
    try {
      window.localStorage.setItem(GALAXY_STORAGE_KEY, JSON.stringify(state.galaxySettings));
      button.textContent = "已保存";
    } catch (_error) {
      button.textContent = "当前环境无法保存";
    }
    window.setTimeout(() => { button.textContent = "保存我的预设"; }, 1400);
  }

  function replayGalaxyEntrance() {
    if (!cy.nodes().length) return;
    if (prefersReducedMotion) {
      runLayout();
      return;
    }
    stopAmbientMotion(false);
    const center = { x: cy.width() / 2, y: cy.height() / 2 };
    const targets = new Map(cy.nodes().map((node) => [node.id(), { ...node.position() }]));
    cy.nodes().forEach((node) => {
      const phase = Number(node.data("motionPhase") || 0);
      node.position({ x: center.x + (Math.cos(phase) * 9), y: center.y + (Math.sin(phase) * 9) });
    });
    cy.nodes().sort((left, right) => Number(right.data("degree")) - Number(left.data("degree"))).forEach((node, index) => {
      window.setTimeout(() => {
        node.animate({ position: targets.get(node.id()), duration: 520, easing: "ease-out-cubic" });
      }, Math.min(index * 18, 620));
    });
    window.setTimeout(() => {
      captureMotionAnchors();
      startAmbientMotion();
    }, 1250);
  }

  function bindGalaxyControls() {
    const numericControls = {
      "galaxy-node-scale": ["nodeScale", false],
      "galaxy-edge-opacity": ["edgeOpacity", false],
      "galaxy-glow-strength": ["glowStrength", false],
      "galaxy-trail-density": ["trailDensity", false],
      "galaxy-link-distance": ["linkDistance", true],
      "galaxy-pressure": ["pressure", true],
      "galaxy-orbit-strength": ["orbitStrength", true],
    };
    Object.entries(numericControls).forEach(([id, [key, affectsLayout]]) => {
      const input = byId(id);
      input.addEventListener("input", () => {
        state.galaxySettings[key] = Number(input.value);
        applyGalaxyAppearance();
      });
      if (affectsLayout) input.addEventListener("change", () => runLayout());
    });
    byId("galaxy-size-mode").addEventListener("change", (event) => {
      state.galaxySettings.sizeMode = event.target.value;
      applyGalaxyAppearance();
    });
    [["galaxy-starfield", "starfield"], ["galaxy-twinkle", "twinkle"], ["galaxy-auto-orbit", "autoOrbit"], ["galaxy-camera-cruise", "cameraCruise"]].forEach(([id, key]) => {
      byId(id).addEventListener("change", (event) => {
        state.galaxySettings[key] = event.target.checked;
        if (key === "autoOrbit") orbitStartedAt = performance.now();
        if (key === "cameraCruise") cruiseBaseline = null;
        applyGalaxyAppearance();
        startAmbientMotion();
      });
    });
    document.querySelectorAll("[data-galaxy-preset]").forEach((button) => {
      button.addEventListener("click", () => applyGalaxyPreset(button.dataset.galaxyPreset));
    });
    byId("galaxy-save").addEventListener("click", persistGalaxySettings);
    byId("galaxy-reset").addEventListener("click", () => {
      state.galaxySettings = { ...DEFAULT_GALAXY_SETTINGS };
      try { window.localStorage.removeItem(GALAXY_STORAGE_KEY); } catch (_error) { /* File origins may disable storage. */ }
      orbitStartedAt = performance.now();
      cruiseBaseline = null;
      applyGalaxyAppearance();
      runLayout();
    });
    byId("galaxy-replay").addEventListener("click", replayGalaxyEntrance);
    syncGalaxyControls();
  }

  function runLayout() {
    stopAmbientMotion(false);
    const preset = presetById.get(state.preset);
    const name = state.galaxySettings.preset !== "minimal"
      ? "galaxy"
      : preset?.layout === "semantic"
      ? "semantic"
      : cy.nodes().length > 55 ? "cose" : (preset?.layout || "cose");
    const options = name === "galaxy"
      ? { name: "preset", positions: galaxyLayoutPositions(), fit: true, padding: 68, animate: false }
      : name === "semantic"
      ? { name: "preset", positions: semanticPositions(preset), fit: true, padding: 56, animate: false }
      : name === "breadthfirst"
        ? { name, directed: true, spacingFactor: 1.25, padding: 42, animate: false }
        : { name: "cose", idealEdgeLength: 82, nodeRepulsion: 5200, gravity: 0.16, padding: 42, animate: false, randomize: true };
    const layout = cy.layout(options);
    layout.one("layoutstop", () => {
      captureMotionAnchors();
      window.requestAnimationFrame(() => {
        captureCruiseBaseline();
        lastStarTrailFrame = 0;
        renderStarTrails(performance.now());
      });
      startAmbientMotion();
    });
    layout.run();
    if ((name === "semantic" || name === "galaxy") && cy.zoom() < 0.58) {
      cy.zoom(0.58);
      cy.center();
    }
    updateZoomLevel();
  }

  function renderTechnologyLanes(view) {
    const container = byId("technology-lanes");
    const preset = presetById.get(state.preset);
    const lanes = preset?.layout === "semantic" && state.galaxySettings.preset === "minimal" ? (preset.lanes || []) : [];
    container.hidden = !lanes.length;
    container.textContent = "";
    if (!lanes.length) return;
    lanes.forEach((lane, laneIndex) => {
      const laneTypes = new Set(lane.node_types || []);
      const count = view.nodes.filter((node) => laneTypes.has(node.type)).length;
      const item = document.createElement("span");
      const step = document.createElement("i");
      const label = document.createElement("b");
      const total = document.createElement("small");
      step.className = "lane-step";
      step.textContent = String(laneIndex + 1).padStart(2, "0");
      label.textContent = lane.label;
      total.textContent = `${count} 个节点`;
      item.append(step, label, total);
      container.append(item);
    });
    container.style.gridTemplateColumns = `repeat(${lanes.length}, minmax(0, 1fr))`;
  }

  function activateNodeEdges(node) {
    cy.edges().removeClass("edge-active incoming-active outgoing-active");
    if (!node.length) return;
    node.incomers("edge").addClass("edge-active incoming-active");
    node.outgoers("edge").addClass("edge-active outgoing-active");
  }

  function activateFocusEdges() {
    activateNodeEdges(cy.getElementById(state.focus));
  }

  function depthCandidatesAt(renderedPosition, tappedNode) {
    const candidates = cy.nodes().toArray().filter((node) => {
      const center = node.renderedPosition();
      const hitRadius = Math.max(DEPTH_TAP_RADIUS, (node.renderedOuterWidth() / 2) + 7);
      return Math.hypot(center.x - renderedPosition.x, center.y - renderedPosition.y) <= hitRadius;
    });
    if (!candidates.some((node) => node.id() === tappedNode.id())) candidates.push(tappedNode);
    return candidates.sort((left, right) => {
      const depthDifference = Number(right.data("depthOrder") || 0) - Number(left.data("depthOrder") || 0);
      if (depthDifference) return depthDifference;
      const leftPosition = left.renderedPosition();
      const rightPosition = right.renderedPosition();
      const leftDistance = Math.hypot(leftPosition.x - renderedPosition.x, leftPosition.y - renderedPosition.y);
      const rightDistance = Math.hypot(rightPosition.x - renderedPosition.x, rightPosition.y - renderedPosition.y);
      return leftDistance - rightDistance || left.id().localeCompare(right.id());
    });
  }

  function depthAwareTapTarget(event) {
    const renderedPosition = event.renderedPosition || event.target.renderedPosition();
    const candidates = depthCandidatesAt(renderedPosition, event.target);
    if (candidates.length <= 1) {
      depthTapCycle = null;
      return event.target;
    }
    const now = performance.now();
    const candidateKey = candidates.map((node) => node.id()).join("|");
    const repeatsPreviousTap = depthTapCycle
      && depthTapCycle.candidateKey === candidateKey
      && (now - depthTapCycle.time) <= DEPTH_TAP_WINDOW_MS
      && Math.hypot(depthTapCycle.x - renderedPosition.x, depthTapCycle.y - renderedPosition.y) <= DEPTH_TAP_RADIUS;
    const index = repeatsPreviousTap ? (depthTapCycle.index + 1) % candidates.length : 0;
    depthTapCycle = { candidateKey, index, time: now, x: renderedPosition.x, y: renderedPosition.y };
    return candidates[index];
  }

  function renderGraph() {
    const view = computeVisibleElements();
    depthTapCycle = null;
    state.visibleNodeIds = new Set(view.nodes.map((node) => node.id));
    state.visibleEdgeIds = new Set(view.edges.map((edge) => edge.id));
    stopAmbientMotion(false);
    motionAnchors.clear();
    cy.elements().remove();
    cy.add(cytoscapeElements(view));
    cy.nodes().addClass("editorial-node");
    cy.nodes().addClass("depth-aware");
    cy.nodes().addClass("galaxy-node");
    cy.edges().addClass("depth-aware");
    cy.edges().addClass("galaxy-edge");
    applyGalaxyAppearance();
    if (state.preset === "technology" && state.galaxySettings.preset === "minimal") {
      cy.nodes().addClass("corridor-node");
      cy.edges().addClass("corridor-edge");
    }
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
    byId("visible-count").textContent = `${state.localFocus ? "局部 · " : ""}${view.nodes.length} 节点 · ${view.edges.length} 关系`;
    byId("graph-status").textContent = `图谱已更新，显示 ${view.nodes.length} 个节点和 ${view.edges.length} 条关系。`;
    renderRelationTable(view.edges);
    renderInspector();
    updateGalaxyStats();
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
      research_object: "#d6d0c4", target: "#8f84b7", indication: "#b56f86",
      patent_family: "#6f8fb9", patent_document: "#5f9e92", claim: "#c49a5a",
      evidence: "#c97264", applicant: "#87909a", jurisdiction: "#668fa0",
      technology_theme: "#899f68", causal_concept: "#9bb2d0", source: "#6e7378",
    };
    byId("node-legend").innerHTML = DATA.legend.node_types
      .map((row) => `<div class="legend-row"><span class="legend-dot" style="background:${nodeColors[row.value] || "#64748b"}"></span>${escapeHtml(row.label)}</div>`)
      .join("");
    const edgeLegend = DATA.legend.relation_kinds || DATA.legend.assertions;
    byId("edge-legend").innerHTML = edgeLegend
      .map((row) => `<div class="legend-row"><span class="legend-line ${escapeHtml(row.line_style)}"></span>${escapeHtml(row.label)}</div>`)
      .join("");
  }

  function renderRelationTable(edges) {
    const body = byId("relation-table-body");
    if (!edges.length) {
      body.innerHTML = '<tr><td colspan="6" class="empty-copy">当前筛选下没有关系边。</td></tr>';
      return;
    }
    body.innerHTML = edges.slice(0, 200).map((edge) => {
      const source = nodesById.get(edge.source);
      const target = nodesById.get(edge.target);
      return `<tr>
        <td><button type="button" data-focus="${escapeHtml(edge.source)}">${escapeHtml(source?.label || edge.source)}</button></td>
        <td>${escapeHtml(edge.label || edge.type)}</td>
        <td><button type="button" data-focus="${escapeHtml(edge.target)}">${escapeHtml(target?.label || edge.target)}</button></td>
        <td><span class="relation-kind relation-kind-${escapeHtml(edge.relation_kind)}">${escapeHtml(edge.relation_kind || "structural")}</span><small class="relation-detail">${escapeHtml(edge.assertion || "structured")}</small></td>
        <td>${escapeHtml(edge.causal_status || "not_applicable")}<small class="relation-detail">${escapeHtml(edge.evidence_level || "not_applicable")} · ${escapeHtml(edge.confidence || "not_assessed")} · ${escapeHtml(edge.directness || "not_applicable")}</small></td>
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
      return `<button class="node-link" type="button" data-focus="${escapeHtml(otherId)}"><span class="node-link-copy"><b>${escapeHtml(edge.label)} · ${escapeHtml(other?.label || otherId)}</b><small>${escapeHtml(edge.relation_kind || "structural")} · ${escapeHtml(edge.causal_status || "not_applicable")} · ${escapeHtml(edge.evidence_level || "not_applicable")}</small></span><span class="node-link-arrow" aria-hidden="true">→</span></button>`;
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
    if (state.localFocus) next.set("local", "1");
    history.replaceState(null, "", `${window.location.pathname}?${next.toString()}${window.location.hash}`);
  }

  function selectNode(nodeId, options = {}) {
    const node = nodesById.get(nodeId);
    if (!node) return;
    const recordHistory = options.recordHistory ?? true;
    const openInspector = options.openInspector ?? true;
    if (recordHistory && state.focusHistory[state.focusIndex] !== nodeId) {
      state.focusHistory = state.focusHistory.slice(0, state.focusIndex + 1);
      state.focusHistory.push(nodeId);
      state.focusIndex = state.focusHistory.length - 1;
    }
    state.focus = nodeId;
    state.query = "";
    byId("graph-search").value = "";
    const graphNode = cy.getElementById(nodeId);
    const canFocusInPlace = options.preserveViewport && graphNode.length && !state.localFocus;
    if (canFocusInPlace) {
      cy.nodes().unselect();
      graphNode.select();
      activateFocusEdges();
      renderInspector();
      updateUrl();
      flyCameraToNode(graphNode);
    } else {
      if (!state.nodeTypes.has(node.type)) state.nodeTypes.add(node.type);
      incidentEdges(nodeId).forEach((edge) => state.relationTypes.add(edge.type));
      renderFilters();
      renderGraph();
    }
    updateFocusNavigation();
    if (openInspector) setPanelState("inspector", true);
  }

  function topHubNodes(limit = 12) {
    const visibleIds = state.visibleNodeIds.size
      ? state.visibleNodeIds
      : new Set(DATA.nodes.map((node) => node.id));
    const degreeById = new Map([...visibleIds].map((id) => [id, 0]));
    DATA.edges.forEach((edge) => {
      if (!visibleIds.has(edge.source) || !visibleIds.has(edge.target)) return;
      degreeById.set(edge.source, (degreeById.get(edge.source) || 0) + 1);
      degreeById.set(edge.target, (degreeById.get(edge.target) || 0) + 1);
    });
    return DATA.nodes
      .filter((node) => visibleIds.has(node.id))
      .map((node) => ({ ...node, graphDegree: degreeById.get(node.id) || 0 }))
      .sort((left, right) => right.graphDegree - left.graphDegree || left.label.localeCompare(right.label))
      .slice(0, limit);
  }

  function findBridgeNodes() {
    const nodeIds = new Set(state.visibleNodeIds);
    const adjacency = new Map([...nodeIds].map((id) => [id, new Set()]));
    DATA.edges.forEach((edge) => {
      if (!nodeIds.has(edge.source) || !nodeIds.has(edge.target)) return;
      adjacency.get(edge.source).add(edge.target);
      adjacency.get(edge.target).add(edge.source);
    });
    const discovery = new Map();
    const low = new Map();
    const parent = new Map();
    const bridges = new Set();
    let time = 0;
    function visit(nodeId) {
      time += 1;
      discovery.set(nodeId, time);
      low.set(nodeId, time);
      let children = 0;
      adjacency.get(nodeId).forEach((neighborId) => {
        if (!discovery.has(neighborId)) {
          children += 1;
          parent.set(neighborId, nodeId);
          visit(neighborId);
          low.set(nodeId, Math.min(low.get(nodeId), low.get(neighborId)));
          const isRootBridge = !parent.has(nodeId) && children > 1;
          const isInternalBridge = parent.has(nodeId) && low.get(neighborId) >= discovery.get(nodeId);
          if (isRootBridge || isInternalBridge) bridges.add(nodeId);
        } else if (neighborId !== parent.get(nodeId)) {
          low.set(nodeId, Math.min(low.get(nodeId), discovery.get(neighborId)));
        }
      });
    }
    nodeIds.forEach((nodeId) => { if (!discovery.has(nodeId)) visit(nodeId); });
    const hubRank = new Map(topHubNodes(DATA.nodes.length).map((node) => [node.id, node.graphDegree]));
    return [...bridges]
      .map((id) => ({ ...nodesById.get(id), graphDegree: hubRank.get(id) || 0 }))
      .sort((left, right) => right.graphDegree - left.graphDegree || left.label.localeCompare(right.label));
  }

  function renderNodeSearchResults(nodes, contextLabel) {
    const container = byId("search-results");
    container.innerHTML = nodes.length
      ? nodes.map((node) => `<button class="search-result" type="button" data-focus="${escapeHtml(node.id)}"><b>${escapeHtml(node.label)}</b><small>${escapeHtml(contextLabel)} · ${escapeHtml(nodeTypeLabels.get(node.type) || node.type)} · ${Number(node.graphDegree || 0)} 条连接</small></button>`).join("")
      : `<div class="search-result"><small>${escapeHtml(contextLabel)}：没有匹配节点</small></div>`;
    container.hidden = false;
  }

  function renderSearchResults() {
    const container = byId("search-results");
    const query = state.query.trim().toLowerCase();
    if (!query) {
      if (document.activeElement === byId("graph-search")) renderNodeSearchResults(topHubNodes(), "Top Hub");
      else {
        container.hidden = true;
        container.textContent = "";
      }
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
    state.focusHistory = [state.focus];
    state.focusIndex = 0;
    state.localFocus = false;
    byId("graph-search").value = "";
    byId("focus-neighborhood").setAttribute("aria-pressed", "false");
    configurePreset("technology", true);
    renderGraph();
    updateFocusNavigation();
    setPanelState("filter", false);
    setPanelState("inspector", false);
    setPanelState("ledger", false);
  }

  const depthSurface = byId("main-content");
  const graphCanvas = byId("graph-canvas");
  const reduceDepthMotion = prefersReducedMotion;
  let depthFrame = 0;
  let pendingDepth = { x: 0, y: 0 };
  function renderDepthParallax() {
    const { x, y } = pendingDepth;
    depthSurface.style.setProperty("--depth-x-far", `${(-x * 3).toFixed(2)}px`);
    depthSurface.style.setProperty("--depth-y-far", `${(-y * 2).toFixed(2)}px`);
    depthSurface.style.setProperty("--depth-x-mid", `${(-x * 8).toFixed(2)}px`);
    depthSurface.style.setProperty("--depth-y-mid", `${(-y * 5).toFixed(2)}px`);
    depthSurface.style.setProperty("--depth-x-near", `${(x * 5).toFixed(2)}px`);
    depthSurface.style.setProperty("--depth-y-near", `${(y * 3).toFixed(2)}px`);
    depthSurface.style.setProperty("--depth-light-x", `${(50 + (x * 8)).toFixed(2)}%`);
    depthSurface.style.setProperty("--depth-light-y", `${(46 + (y * 6)).toFixed(2)}%`);
    depthFrame = 0;
  }
  function queueDepthParallax(x, y) {
    if (reduceDepthMotion) return;
    pendingDepth = { x, y };
    if (!depthFrame) depthFrame = window.requestAnimationFrame(renderDepthParallax);
  }
  depthSurface.addEventListener("pointermove", (event) => {
    if (event.pointerType === "touch") return;
    const bounds = depthSurface.getBoundingClientRect();
    const x = clamp(((event.clientX - bounds.left) / Math.max(bounds.width, 1)) * 2 - 1, -1, 1);
    const y = clamp(((event.clientY - bounds.top) / Math.max(bounds.height, 1)) * 2 - 1, -1, 1);
    queueDepthParallax(x, y);
  }, { passive: true });
  depthSurface.addEventListener("pointerleave", () => queueDepthParallax(0, 0), { passive: true });
  graphCanvas.addEventListener("pointerdown", () => graphCanvas.classList.add("is-grabbing"), { passive: true });
  window.addEventListener("pointerup", () => graphCanvas.classList.remove("is-grabbing"), { passive: true });
  window.addEventListener("pointercancel", () => graphCanvas.classList.remove("is-grabbing"), { passive: true });

  let searchTimer;
  byId("graph-search").value = state.query;
  byId("graph-search").addEventListener("input", (event) => {
    state.query = event.target.value;
    renderSearchResults();
    window.clearTimeout(searchTimer);
    searchTimer = window.setTimeout(renderGraph, 180);
  });
  byId("graph-search").addEventListener("focus", renderSearchResults);
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
  byId("motion-toggle").addEventListener("click", () => setMotionEnabled(!state.motionEnabled));
  byId("reset-button").addEventListener("click", resetView);
  byId("export-button").addEventListener("click", exportVisible);
  byId("layer-toggle").addEventListener("click", () => {
    const open = !state.filterOpen;
    if (open) setPanelState("galaxy", false);
    setPanelState("filter", open);
  });
  byId("filter-close").addEventListener("click", () => setPanelState("filter", false));
  byId("galaxy-toggle").addEventListener("click", () => {
    const open = !state.galaxyOpen;
    if (open) setPanelState("filter", false);
    setPanelState("galaxy", open);
  });
  byId("galaxy-close").addEventListener("click", () => setPanelState("galaxy", false));
  byId("galaxy-top-hubs").addEventListener("click", (event) => {
    event.stopPropagation();
    state.query = "";
    byId("graph-search").value = "";
    byId("graph-search").focus();
    renderNodeSearchResults(topHubNodes(), "Top Hub");
  });
  byId("galaxy-bridge-nodes").addEventListener("click", (event) => {
    event.stopPropagation();
    state.query = "";
    byId("graph-search").value = "";
    byId("graph-search").focus();
    renderNodeSearchResults(findBridgeNodes(), "桥接节点");
  });
  byId("inspector-toggle").addEventListener("click", () => setPanelState("inspector", !state.inspectorOpen));
  byId("inspector-close").addEventListener("click", () => setPanelState("inspector", false));
  byId("ledger-toggle").addEventListener("click", () => setPanelState("ledger", !state.ledgerOpen));
  byId("ledger-close").addEventListener("click", () => setPanelState("ledger", false));
  byId("focus-back").addEventListener("click", () => navigateFocusHistory(-1));
  byId("focus-forward").addEventListener("click", () => navigateFocusHistory(1));
  byId("focus-neighborhood").setAttribute("aria-pressed", String(state.localFocus));
  byId("focus-neighborhood").addEventListener("click", (event) => {
    state.localFocus = !state.localFocus;
    event.currentTarget.setAttribute("aria-pressed", String(state.localFocus));
    renderGraph();
  });
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
  cy.on("tap", "node", (event) => {
    const target = depthAwareTapTarget(event);
    selectNode(target.id(), { preserveViewport: true });
  });
  cy.on("mouseover", "node", (event) => {
    const neighborhood = event.target.closedNeighborhood();
    cy.elements().addClass("faded");
    neighborhood.removeClass("faded");
    activateNodeEdges(event.target);
  });
  cy.on("mouseout", "node", () => {
    cy.elements().removeClass("faded");
    activateFocusEdges();
  });
  cy.on("mouseover", "edge", (event) => event.target.addClass("edge-active"));
  cy.on("mouseout", "edge", () => activateFocusEdges());
  cy.on("grab", "node", (event) => {
    const node = event.target;
    depthTapCycle = null;
    const position = node.position();
    if (state.motionEnabled) {
      draggedNodeId = node.id();
      lastDragSample = { position: { x: position.x, y: position.y }, time: performance.now(), velocity: { x: 0, y: 0 } };
      const velocity = velocityFor(node.id());
      velocity.x = 0;
      velocity.y = 0;
      physicsStillMoving = true;
      physicsActiveUntil = performance.now() + 2600;
    }
    graphCanvas.classList.add("is-grabbing");
    lastViewportInteraction = performance.now();
    activateNodeEdges(node);
    startAmbientMotion();
  });
  cy.on("drag", "node", (event) => {
    if (!state.motionEnabled) return;
    const now = performance.now();
    const node = event.target;
    const position = node.position();
    const elapsed = Math.max(0.008, (now - (lastDragSample?.time || now - 16)) / 1000);
    const previous = lastDragSample?.position || position;
    const dragVelocity = {
      x: (position.x - previous.x) / elapsed,
      y: (position.y - previous.y) / elapsed,
    };
    coupleNeighborVelocity(node, dragVelocity);
    motionAnchors.set(node.id(), { x: position.x, y: position.y });
    const velocity = velocityFor(node.id());
    velocity.x = 0;
    velocity.y = 0;
    lastDragSample = { position: { x: position.x, y: position.y }, time: now, velocity: dragVelocity };
    if ((now - lastWaveEmission) >= 42 && Math.hypot(dragVelocity.x, dragVelocity.y) > 12) {
      emitPhysicsWave(node, dragVelocity, 0.42);
      lastWaveEmission = now;
    }
    physicsStillMoving = true;
    physicsActiveUntil = now + 2600;
    startAmbientMotion();
  });
  cy.on("dragfree", "node", (event) => {
    const now = performance.now();
    const position = event.target.position();
    motionAnchors.set(event.target.id(), { x: position.x, y: position.y });
    if (state.motionEnabled) {
      const releaseVelocity = lastDragSample?.velocity || { x: 0, y: 0 };
      emitPhysicsWave(event.target, releaseVelocity, 0.7);
      const velocity = velocityFor(event.target.id());
      velocity.x = 0;
      velocity.y = 0;
      physicsStillMoving = true;
      physicsActiveUntil = now + 2800;
    }
    draggedNodeId = "";
    lastDragSample = null;
    graphCanvas.classList.remove("is-grabbing");
    startAmbientMotion();
  });
  cy.on("free", "node", () => {
    draggedNodeId = "";
    lastDragSample = null;
    graphCanvas.classList.remove("is-grabbing");
  });
  cy.on("zoom", (event) => {
    depthTapCycle = null;
    if (event.originalEvent || performance.now() > programmaticViewportUntil) {
      lastViewportInteraction = performance.now();
      captureCruiseBaseline();
    }
    updateZoomLevel();
  });
  cy.on("pan", (event) => {
    depthTapCycle = null;
    if (event.originalEvent || performance.now() > programmaticViewportUntil) {
      lastViewportInteraction = performance.now();
      captureCruiseBaseline();
    }
  });
  window.addEventListener("resize", () => {
    cy.resize();
    cruiseBaseline = null;
    sizeStarTrailCanvas();
    lastStarTrailFrame = 0;
    renderStarTrails(performance.now());
  });
  document.addEventListener("visibilitychange", () => {
    if (document.hidden) stopAmbientMotion(false);
    else startAmbientMotion();
  });
  window.addEventListener("keydown", (event) => {
    if ((event.ctrlKey || event.metaKey) && event.key.toLowerCase() === "k") {
      event.preventDefault();
      byId("graph-search").focus();
    }
    if (event.key === "Escape") {
      if (state.ledgerOpen) setPanelState("ledger", false);
      else if (state.inspectorOpen) setPanelState("inspector", false);
      else if (state.galaxyOpen) setPanelState("galaxy", false);
      else if (state.filterOpen) setPanelState("filter", false);
    }
  });

  DATA.presets.forEach((preset) => {
    const option = document.createElement("option");
    option.value = preset.id;
    option.textContent = preset.label;
    byId("view-preset").append(option);
  });
  bindGalaxyControls();
  configurePreset(initialPreset);
  renderQuality();
  renderLegend();
  renderSearchResults();
  updateMotionControl();
  renderGraph();
  updateZoomLevel();
  updateFocusNavigation();
})();
