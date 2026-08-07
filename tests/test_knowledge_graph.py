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


if __name__ == "__main__":
    unittest.main()
