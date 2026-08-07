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

  const state = {
    preset: initialPreset,
    depth: initialDepth,
    focus: initialFocus,
    query: params.get("q") || "",
    tab: "overview",
    focusHistory: [initialFocus],
    focusIndex: 0,
    filterOpen: false,
    inspectorOpen: false,
    ledgerOpen: false,
    localFocus: params.get("local") === "1",
    motionEnabled: !prefersReducedMotion,
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
        const coulombForce = COULOMB_STRENGTH / ((distance * distance) + 144);
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
    cy.batch(() => {
      cy.nodes().forEach((node) => {
        if (node.grabbed()) return;
        const anchor = motionAnchors.get(node.id());
        if (!anchor) return;
        const depth = Number(node.data("spatialDepth") || 0.3);
        const phase = Number(node.data("motionPhase") || 0);
        const amplitude = 0.5 + (depth * 1.35);
        node.position({
          x: anchor.x + (Math.sin((seconds * 0.62) + phase) * amplitude),
          y: anchor.y + (Math.cos((seconds * 0.54) + (phase * 1.17)) * amplitude * 0.68),
        });
      });
    });
  }

  function animateAmbientMotion(timestamp) {
    motionFrame = 0;
    if (!state.motionEnabled || document.hidden || !motionAnchors.size) return;
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
  }

  function updateZoomLevel() {
    byId("zoom-level").textContent = `${Math.round(cy.zoom() * 100)}%`;
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

  function cytoscapeElements(view) {
    const spatialMetrics = computeSpatialMetrics(view);
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

  function runLayout() {
    stopAmbientMotion(false);
    const preset = presetById.get(state.preset);
    const name = preset?.layout === "semantic"
      ? "semantic"
      : cy.nodes().length > 55 ? "cose" : (preset?.layout || "cose");
    const options = name === "semantic"
      ? { name: "preset", positions: semanticPositions(preset), fit: true, padding: 56, animate: false }
      : name === "breadthfirst"
        ? { name, directed: true, spacingFactor: 1.25, padding: 42, animate: false }
        : { name: "cose", idealEdgeLength: 82, nodeRepulsion: 5200, gravity: 0.16, padding: 42, animate: false, randomize: true };
    const layout = cy.layout(options);
    layout.one("layoutstop", () => {
      captureMotionAnchors();
      startAmbientMotion();
    });
    layout.run();
    if (name === "semantic" && cy.zoom() < 0.58) {
      cy.zoom(0.58);
      cy.center();
    }
    updateZoomLevel();
  }

  function renderTechnologyLanes(view) {
    const container = byId("technology-lanes");
    const preset = presetById.get(state.preset);
    const lanes = preset?.layout === "semantic" ? (preset.lanes || []) : [];
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
    cy.edges().addClass("depth-aware");
    if (state.preset === "technology") {
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
    } else {
      if (!state.nodeTypes.has(node.type)) state.nodeTypes.add(node.type);
      incidentEdges(nodeId).forEach((edge) => state.relationTypes.add(edge.type));
      renderFilters();
      renderGraph();
    }
    updateFocusNavigation();
    if (openInspector) setPanelState("inspector", true);
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
  byId("layer-toggle").addEventListener("click", () => setPanelState("filter", !state.filterOpen));
  byId("filter-close").addEventListener("click", () => setPanelState("filter", false));
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
  cy.on("zoom", () => {
    depthTapCycle = null;
    lastViewportInteraction = performance.now();
    updateZoomLevel();
  });
  cy.on("pan", () => {
    depthTapCycle = null;
    lastViewportInteraction = performance.now();
  });
  window.addEventListener("resize", () => cy.resize());
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
      else if (state.filterOpen) setPanelState("filter", false);
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
  updateMotionControl();
  renderGraph();
  updateZoomLevel();
  updateFocusNavigation();
})();
