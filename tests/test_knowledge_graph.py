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
        self.case_dir = ROOT / "durvalumab-pdl1-nsclc"

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
        self.assertIn("wheelSensitivity: 0.48", html)
        self.assertIn("function startAmbientMotion()", html)
        self.assertIn('cy.on("grab", "node"', html)
        self.assertIn('cy.on("dragfree", "node"', html)
        self.assertIn('cy.on("zoom"', html)
        self.assertIn("motionAnchors.set", html)
        self.assertIn(".graph-canvas { cursor: grab;", html)

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
