import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from build_modular_reports import build_reports  # noqa: E402


class ReportingIntegrationTests(unittest.TestCase):
    def test_modular_report_build_includes_knowledge_graph(self):
        with tempfile.TemporaryDirectory() as temp:
            project = Path(temp) / "case"
            shutil.copytree(ROOT / "cases" / "durvalumab-pdl1-nsclc", project)
            for name in (
                "case-output.json",
                "graph-data.json",
                "graph-quality.json",
                "knowledge-graph.html",
            ):
                path = project / name
                if path.exists():
                    path.unlink()

            build_reports(project)

            self.assertTrue((project / "case-output.json").exists())
            self.assertTrue((project / "graph-data.json").exists())
            self.assertTrue((project / "graph-quality.json").exists())
            self.assertTrue((project / "knowledge-graph.html").exists())
            self.assertIn("knowledge-graph.html", (project / "report-index.md").read_text(encoding="utf-8"))
            report_index = (project / "report-index.html").read_text(encoding="utf-8")
            self.assertIn("knowledge-graph.html", report_index)
            self.assertIn('class="graph-embed"', report_index)
            self.assertIn('<iframe', report_index)
            self.assertIn('src="knowledge-graph.html?view=technology&amp;depth=2"', report_index)
            self.assertIn('title="Durvalumab 专利证据双链图"', report_index)
            self.assertIn("allowfullscreen", report_index)
            state = json.loads((project / "state.json").read_text(encoding="utf-8"))
            self.assertEqual("complete", state["reports"]["knowledge_graph"])
            self.assertEqual("warning", state["graph_quality"])


if __name__ == "__main__":
    unittest.main()
