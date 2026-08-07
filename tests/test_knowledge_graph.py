import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from build_knowledge_graph import build_knowledge_graph, script_json  # noqa: E402


class KnowledgeGraphPageTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.output = Path(self.temp.name) / "knowledge-graph.html"
        self.case_dir = ROOT / "cases" / "durvalumab-pdl1-nsclc"

    def tearDown(self):
        self.temp.cleanup()

    def test_builds_an_offline_accessible_cytoscape_view(self):
        result = build_knowledge_graph(self.case_dir, output_path=self.output)
        html = self.output.read_text(encoding="utf-8")

        self.assertEqual(self.output, result)
        self.assertIn('data-cytoscape-version="3.34.0"', html)
        self.assertIn("cytoscape({", html)
        self.assertIn("window.PATENT_GRAPH_DATA", html)
        self.assertNotIn("<script src=", html)
        self.assertNotIn("<link rel=\"stylesheet\" href=", html)
        self.assertIn('id="graph-canvas"', html)
        self.assertIn('aria-label="专利证据关系图"', html)
        self.assertIn('id="graph-search"', html)
        self.assertIn('id="view-preset"', html)
        self.assertIn('id="depth-control"', html)
        self.assertIn('id="case-context"', html)
        self.assertIn('id="context-focus-label"', html)
        self.assertIn('id="context-view-description"', html)
        self.assertIn('id="node-type-filters"', html)
        self.assertIn('id="node-filter-summary"', html)
        self.assertIn('id="quality-banner"', html)
        self.assertIn('id="inspector-tabs"', html)
        self.assertIn('id="inspector-outgoing-count"', html)
        self.assertIn('id="canvas-focus-label"', html)
        self.assertIn('id="technology-lanes"', html)
        self.assertIn('data-tab="backlinks"', html)
        self.assertIn('id="relation-table-body"', html)
        self.assertIn("history.replaceState", html)
        self.assertIn("collectNeighborhood", html)
        self.assertIn("semanticPositions", html)
        self.assertIn('preset?.layout === "semantic"', html)
        self.assertIn("edge-active", html)
        self.assertNotIn('"font-weight": 650', html)
        self.assertNotIn('"font-weight": 680', html)

    def test_embedded_json_cannot_terminate_its_script_tag(self):
        payload = {"label": "</script><script>alert(1)</script>"}
        encoded = script_json(payload)
        self.assertNotIn("</script", encoded.lower())
        self.assertIn("<\\/script>", encoded)

    def test_builds_a_canvas_first_patent_atlas_shell(self):
        build_knowledge_graph(self.case_dir, output_path=self.output)
        html = self.output.read_text(encoding="utf-8")

        self.assertIn('class="graph-rail"', html)
        self.assertIn('id="layer-toggle"', html)
        self.assertIn('aria-controls="filter-panel"', html)
        self.assertIn('id="filter-panel"', html)
        self.assertIn('id="inspector-close"', html)
        self.assertIn('id="ledger-toggle"', html)
        self.assertIn('aria-controls="relation-ledger"', html)
        self.assertIn('id="focus-back"', html)
        self.assertIn('id="focus-forward"', html)
        self.assertIn('id="focus-neighborhood"', html)
        self.assertIn('class="workspace-shell"', html)
        self.assertIn('class="relation-ledger" id="relation-ledger"', html)

        self.assertIn("focusHistory", html)
        self.assertIn("navigateFocusHistory", html)
        self.assertIn("setPanelState", html)
        self.assertIn("incoming-active", html)
        self.assertIn("outgoing-active", html)
        self.assertIn("corridor-edge", html)
        self.assertIn("workspace.is-filter-open", html)
        self.assertIn("workspace.is-inspector-open", html)
        self.assertIn("relation-ledger.is-open", html)

    def test_visualizes_technology_as_a_numbered_evidence_corridor(self):
        build_knowledge_graph(self.case_dir, output_path=self.output)
        html = self.output.read_text(encoding="utf-8")

        self.assertIn('class="path-legend"', html)
        self.assertIn('data-path="incoming"', html)
        self.assertIn('data-path="outgoing"', html)
        self.assertIn('className = "lane-step"', html)
        self.assertIn('addClass("corridor-node")', html)
        self.assertIn('node.corridor-node[type = "claim"]', html)
        self.assertIn(".technology-lanes::before", html)

    def test_uses_a_dark_editorial_constellation_palette(self):
        build_knowledge_graph(self.case_dir, output_path=self.output)
        html = self.output.read_text(encoding="utf-8")

        self.assertIn('data-theme="dark"', html)
        self.assertIn('<meta name="color-scheme" content="dark">', html)
        self.assertIn("--graph-bg: #1a1c1e;", html)
        self.assertIn("--entity-family: #6f8fb9;", html)
        self.assertIn("--entity-document: #5f9e92;", html)
        self.assertIn("--entity-claim: #c49a5a;", html)
        self.assertIn("--entity-evidence: #c97264;", html)
        self.assertIn('addClass("editorial-node")', html)
        self.assertIn('node.editorial-node[type = "patent_family"]', html)
        self.assertIn('"target-arrow-shape": "none"', html)
        self.assertIn("html[data-theme=\"dark\"] .graph-panel", html)

    def test_uses_obsidian_system_type_and_compact_label_spacing(self):
        build_knowledge_graph(self.case_dir, output_path=self.output)
        html = self.output.read_text(encoding="utf-8")

        self.assertIn('--font-obsidian: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Inter, "Noto Sans SC", "PingFang SC", "Microsoft YaHei", sans-serif;', html)
        self.assertIn("font-family: var(--font-obsidian);", html)
        self.assertIn("letter-spacing: -0.01em;", html)
        self.assertIn('"font-family": "-apple-system, BlinkMacSystemFont, \'Segoe UI\', Roboto, Inter, \'Noto Sans SC\', \'PingFang SC\', \'Microsoft YaHei\', sans-serif"', html)
        self.assertIn('"line-height": 1.22,', html)
        self.assertIn('"text-margin-y": 7,', html)
        self.assertNotIn("--font-editorial", html)

    def test_compacts_canvas_annotations_without_discarding_full_node_labels(self):
        build_knowledge_graph(self.case_dir, output_path=self.output)
        html = self.output.read_text(encoding="utf-8")

        self.assertIn("const compactOrganizationLabel = (value) =>", html)
        self.assertIn('if (node.type === "patent_family") {', html)
        self.assertIn('return [node.label, document].filter(Boolean).join("\\n");', html)
        self.assertIn('if (node.type === "claim") return compactLabel(properties.claim_category || node.label.split(" · ")[0], 18);', html)
        self.assertIn('if (node.type === "applicant") return compactOrganizationLabel(node.label);', html)
        self.assertIn('if (node.type === "causal_concept") return compactLabel(node.label, 28);', html)
        self.assertIn('if (node.type === "source") return compactLabel(node.label, 24);', html)
        self.assertIn("label: node.label,", html)
        self.assertIn("displayLabel: nodeDisplayLabel(node),", html)
        self.assertNotIn("const priorityYear =", html)

    def test_builds_a_galaxy_visual_lab_with_editorial_presets(self):
        build_knowledge_graph(self.case_dir, output_path=self.output)
        html = self.output.read_text(encoding="utf-8")

        self.assertIn('id="galaxy-toggle"', html)
        self.assertIn('aria-controls="galaxy-panel"', html)
        self.assertIn('id="galaxy-panel"', html)
        self.assertIn('data-galaxy-preset="galaxy"', html)
        self.assertIn('data-galaxy-preset="spiral"', html)
        self.assertIn('data-galaxy-preset="nebula"', html)
        self.assertIn('data-galaxy-preset="minimal"', html)
        self.assertIn("const DEFAULT_GALAXY_SETTINGS", html)
        self.assertIn("function applyGalaxyAppearance()", html)
        self.assertIn("function galaxyLayoutPositions()", html)
        self.assertIn("const GOLDEN_ANGLE", html)
        self.assertIn('addClass("galaxy-node")', html)
        self.assertIn('addClass("galaxy-edge")', html)
        self.assertIn('selector: "node.galaxy-node"', html)
        self.assertIn('selector: "edge.galaxy-edge"', html)
        self.assertIn('"curve-style": "unbundled-bezier"', html)
        self.assertIn("workspace.is-galaxy-open", html)
        self.assertIn("data-galaxy-mode", html)

    def test_scales_galaxy_hubs_and_exposes_readability_controls(self):
        build_knowledge_graph(self.case_dir, output_path=self.output)
        html = self.output.read_text(encoding="utf-8")

        self.assertIn('id="galaxy-node-scale"', html)
        self.assertIn('id="galaxy-edge-opacity"', html)
        self.assertIn('id="galaxy-glow-strength"', html)
        self.assertIn('id="galaxy-link-distance"', html)
        self.assertIn('id="galaxy-pressure"', html)
        self.assertIn('id="galaxy-orbit-strength"', html)
        self.assertIn('id="galaxy-size-mode"', html)
        self.assertIn("function computeGalaxyMetrics(view)", html)
        self.assertIn("galaxyNodeSize", html)
        self.assertIn("galaxyFontSize", html)
        self.assertIn("galaxyCurveDistance", html)
        self.assertIn("degreeCentrality", html)

    def test_surfaces_galaxy_hubs_bridge_nodes_and_runtime_statistics(self):
        build_knowledge_graph(self.case_dir, output_path=self.output)
        html = self.output.read_text(encoding="utf-8")

        self.assertIn('id="galaxy-stats"', html)
        self.assertIn('id="galaxy-fps"', html)
        self.assertIn('id="galaxy-stat-nodes"', html)
        self.assertIn('id="galaxy-stat-links"', html)
        self.assertIn('id="galaxy-stat-hubs"', html)
        self.assertIn('id="galaxy-top-hubs"', html)
        self.assertIn('id="galaxy-bridge-nodes"', html)
        self.assertIn("function topHubNodes", html)
        self.assertIn("function findBridgeNodes", html)
        self.assertIn("function updateGalaxyStats", html)
        self.assertIn("function renderNodeSearchResults", html)
        self.assertIn('addEventListener("focus", renderSearchResults)', html)
        self.assertIn("function persistGalaxySettings()", html)
        self.assertIn("function replayGalaxyEntrance()", html)
        self.assertIn("window.localStorage.setItem", html)
        self.assertIn("state.galaxySettings.autoOrbit", html)

    def test_adds_a_cinematic_star_atlas_with_real_edge_trails_and_camera_cruise(self):
        build_knowledge_graph(self.case_dir, output_path=self.output)
        html = self.output.read_text(encoding="utf-8")

        self.assertIn('data-galaxy-preset="atlas"', html)
        self.assertIn('id="galaxy-trail-density"', html)
        self.assertIn('id="galaxy-camera-cruise"', html)
        self.assertIn('id="star-trail-canvas"', html)
        self.assertIn("trailDensity", html)
        self.assertIn("cameraCruise", html)
        self.assertIn("function quadraticCurvePoint", html)
        self.assertIn("function renderStarTrails(timestamp)", html)
        self.assertIn("function applyCameraCruise(timestamp)", html)
        self.assertIn("if (timestamp < programmaticViewportUntil) return;", html)
        self.assertIn("event.originalEvent || performance.now() > programmaticViewportUntil", html)
        self.assertIn('selector: "node.galaxy-node:selected"', html)
        self.assertIn(".star-trail-canvas", html)
        self.assertIn("mix-blend-mode: screen", html)
        self.assertIn("pointer-events: none", html)

    def test_adds_depth_cues_without_transforming_the_interactive_canvas(self):
        build_knowledge_graph(self.case_dir, output_path=self.output)
        html = self.output.read_text(encoding="utf-8")

        self.assertIn('class="graph-depth-field"', html)
        self.assertEqual(3, html.count('class="depth-plane '))
        self.assertIn("perspective: 900px", html)
        self.assertIn("translate3d(var(--depth-x-far)", html)
        self.assertIn("function computeSpatialMetrics(view)", html)
        self.assertIn('addClass("depth-aware")', html)
        self.assertIn("node.depth-aware", html)
        self.assertIn("edge.depth-aware", html)
        self.assertIn('addEventListener("pointermove"', html)
        self.assertIn("requestAnimationFrame", html)
        self.assertNotIn("graph-canvas { transform:", html)

    def test_supports_draggable_floating_nodes_and_trackpad_zoom(self):
        build_knowledge_graph(self.case_dir, output_path=self.output)
        html = self.output.read_text(encoding="utf-8")

        self.assertIn('id="motion-toggle"', html)
        self.assertIn('id="zoom-level"', html)
        self.assertIn("userZoomingEnabled: true", html)
        self.assertIn("userPanningEnabled: true", html)
        self.assertIn("autoungrabify: false", html)
        self.assertIn("wheelSensitivity: 5", html)
        self.assertIn("function startAmbientMotion()", html)
        self.assertIn('cy.on("grab", "node"', html)
        self.assertIn('cy.on("dragfree", "node"', html)
        self.assertIn('cy.on("zoom"', html)
        self.assertIn("motionAnchors.set", html)
        self.assertIn(".graph-canvas { cursor: grab;", html)

    def test_keeps_node_font_ratio_stable_then_hides_labels_at_distant_zoom_levels(self):
        build_knowledge_graph(self.case_dir, output_path=self.output)
        html = self.output.read_text(encoding="utf-8")

        self.assertIn("const GRAPH_LABEL_HIDE_ZOOM = 0.68;", html)
        self.assertIn("const GRAPH_LABEL_DETAIL_ZOOM = 0.92;", html)
        self.assertIn('selector: "node.semantic-label-hidden"', html)
        self.assertIn('selector: "edge.semantic-label-hidden"', html)
        self.assertIn("function applySemanticZoom()", html)
        self.assertIn("zoom < GRAPH_LABEL_HIDE_ZOOM", html)
        self.assertIn("zoom < GRAPH_LABEL_DETAIL_ZOOM", html)
        self.assertIn("const galaxyFontSize = clamp(4.4 + (galaxyNodeSize * 0.17), 6.5, 14);", html)
        self.assertIn("const galaxyTextOffset = clamp(3.5 + (galaxyNodeSize * 0.12), 4.5, 11);", html)
        self.assertIn("window.requestAnimationFrame(applySemanticZoom)", html)
        self.assertNotIn("GRAPH_LABEL_MIN_RENDERED_SIZE", html)
        self.assertNotIn("semanticNodeSize", html)
        self.assertNotIn("semanticFontSize", html)
        self.assertNotIn('selector: "node.semantic-zoom"', html)

    def test_keeps_zoom_and_cinematic_motion_responsive_under_load(self):
        build_knowledge_graph(self.case_dir, output_path=self.output)
        html = self.output.read_text(encoding="utf-8")

        self.assertIn("const STAR_TRAIL_FRAME_MS = 24;", html)
        self.assertIn("const CAMERA_CRUISE_FRAME_MS = 24;", html)
        self.assertIn("function rebuildStarTrailCache()", html)
        self.assertIn("const interactionActive = draggedNodeId || (timestamp - lastViewportInteraction) < 240;", html)
        self.assertIn("if ((timestamp - lastCameraCruiseFrame) < CAMERA_CRUISE_FRAME_MS) return;", html)

    def test_propagates_drag_motion_with_springs_damping_and_waves(self):
        build_knowledge_graph(self.case_dir, output_path=self.output)
        html = self.output.read_text(encoding="utf-8")

        self.assertIn("const SPRING_STIFFNESS", html)
        self.assertIn("const DAMPING_COEFFICIENT", html)
        self.assertIn("const COULOMB_STRENGTH", html)
        self.assertIn("const WAVE_SPEED", html)
        self.assertIn("function captureSpringRestLengths()", html)
        self.assertIn("function stepGraphPhysics(timestamp)", html)
        self.assertIn("extension = distance - restLength", html)
        self.assertIn("springForce = SPRING_STIFFNESS * extension", html)
        self.assertIn("Math.exp(-DAMPING_COEFFICIENT * deltaTime)", html)
        self.assertIn("Math.exp(-WAVE_DECAY * localTime)", html)
        self.assertIn("physicsWaves.push", html)
        self.assertIn('cy.on("drag", "node"', html)

    def test_uses_faster_but_bounded_motion_tuning(self):
        build_knowledge_graph(self.case_dir, output_path=self.output)
        html = self.output.read_text(encoding="utf-8")

        self.assertIn("const SPRING_STIFFNESS = 13.2;", html)
        self.assertIn("const DAMPING_COEFFICIENT = 5.1;", html)
        self.assertIn("const WAVE_SPEED = 760;", html)
        self.assertIn("const MAX_PHYSICS_SPEED = 390;", html)
        self.assertIn("const DRAG_NEIGHBOR_COUPLING = 0.28;", html)
        self.assertIn("function coupleNeighborVelocity(node, dragVelocity)", html)
        self.assertIn("coupleNeighborVelocity(node, dragVelocity);", html)
        self.assertIn("(seconds * 0.62)", html)
        self.assertIn("(seconds * 0.54)", html)
        self.assertIn("(timestamp - lastMotionTick) >= 16", html)
        self.assertIn("(now - lastWaveEmission) >= 42", html)

    def test_cycles_through_overlapping_depth_nodes_without_relayout(self):
        build_knowledge_graph(self.case_dir, output_path=self.output)
        html = self.output.read_text(encoding="utf-8")

        self.assertIn("const DEPTH_TAP_RADIUS = 14;", html)
        self.assertIn("function depthCandidatesAt(renderedPosition, tappedNode)", html)
        self.assertIn("function depthAwareTapTarget(event)", html)
        self.assertIn("depthTapCycle.index + 1", html)
        self.assertIn('cy.on("tap", "node", (event) => {', html)
        self.assertIn("selectNode(target.id(), { preserveViewport: true });", html)
        self.assertIn("const canFocusInPlace = options.preserveViewport", html)
        self.assertIn("graphNode.select();", html)
        self.assertIn("点击重叠节点逐层选择", html)

    def test_distinguishes_causal_mechanistic_and_noncausal_edges(self):
        build_knowledge_graph(self.case_dir, output_path=self.output)
        html = self.output.read_text(encoding="utf-8")

        self.assertIn('node[type = "causal_concept"]', html)
        self.assertIn('edge[relationKind = "causal"]', html)
        self.assertIn('edge[relationKind = "mechanistic"]', html)
        self.assertIn('edge[relationKind = "associative"]', html)
        self.assertIn("relationKind: edge.relation_kind", html)
        self.assertIn("causalStatus: edge.causal_status", html)
        self.assertIn("evidenceLevel: edge.evidence_level", html)
        self.assertIn('class="relation-kind relation-kind-${escapeHtml(edge.relation_kind)}"', html)
        self.assertIn("因果状态 / 证据等级", html)


if __name__ == "__main__":
    unittest.main()
