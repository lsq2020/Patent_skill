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


if __name__ == "__main__":
    unittest.main()
