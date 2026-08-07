import copy
import json
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from build_graph_data import build_graph_data  # noqa: E402
from validate_graph_data import validate  # noqa: E402


class GraphDataTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.output_dir = Path(self.temp.name)
        self.case_dir = ROOT / "durvalumab-pdl1-nsclc"

    def tearDown(self):
        self.temp.cleanup()

    def test_builds_connected_graph_and_facets_from_case_output(self):
        graph, quality = build_graph_data(
            self.case_dir,
            output_path=self.output_dir / "graph-data.json",
            quality_path=self.output_dir / "graph-quality.json",
        )

        self.assertEqual("1.0", graph["schema_version"])
        self.assertEqual([], validate(graph))
        node_ids = {row["id"] for row in graph["nodes"]}
        node_types = {row["type"] for row in graph["nodes"]}
        self.assertTrue(
            {
                "research_object",
                "target",
                "indication",
                "patent_family",
                "patent_document",
                "claim",
                "evidence",
                "applicant",
                "jurisdiction",
                "technology_theme",
                "source",
            }.issubset(node_types)
        )
        self.assertTrue(
            all(edge["source"] in node_ids and edge["target"] in node_ids for edge in graph["edges"])
        )
        self.assertTrue(
            any(
                edge["source"].startswith("family:")
                and edge["type"] == "SUPPORTED_BY"
                and edge["target"].startswith("finding:")
                for edge in graph["edges"]
            )
        )
        self.assertEqual(
            {"family", "technology", "evidence", "applicant"},
            {preset["id"] for preset in graph["presets"]},
        )
        technology = next(preset for preset in graph["presets"] if preset["id"] == "technology")
        self.assertEqual(2, technology["default_depth"])
        self.assertEqual("semantic", technology["layout"])
        self.assertEqual(
            ["research", "scope", "families", "themes", "claims"],
            [lane["id"] for lane in technology["lanes"]],
        )
        self.assertEqual(["patent_family"], technology["lanes"][2]["node_types"])
        self.assertEqual(len(graph["nodes"]), graph["meta"]["node_count"])
        self.assertEqual(len(graph["edges"]), graph["meta"]["edge_count"])
        self.assertEqual("warning", quality["status"])
        self.assertTrue(
            any(gap["code"] == "family_relations_missing" for gap in quality["gaps"])
        )

    def test_family_relation_edges_survive_without_inference(self):
        source = json.loads((self.case_dir / "case-output.json").read_text(encoding="utf-8"))
        source["records"]["relations"].append(
            {
                "relation_id": "REL-EXPLICIT",
                "source_id": "family:DVL-FAM-002",
                "relation_type": "DIVISIONAL_OF",
                "target_id": "family:DVL-FAM-001",
                "assertion": "direct_fact",
                "link_methods": ["family.family_relations"],
                "evidence_ids": [],
                "properties": {},
            }
        )
        case_output_path = self.output_dir / "case-output.json"
        case_output_path.write_text(json.dumps(source), encoding="utf-8")

        graph, quality = build_graph_data(
            self.output_dir,
            case_output_path=case_output_path,
            output_path=self.output_dir / "graph-data.json",
            quality_path=self.output_dir / "graph-quality.json",
        )
        edge = next(row for row in graph["edges"] if row["id"] == "REL-EXPLICIT")
        self.assertEqual("DIVISIONAL_OF", edge["type"])
        self.assertEqual("direct_fact", edge["assertion"])
        self.assertEqual(1, quality["metrics"]["family_relation_edge_count"])

    def test_validator_rejects_dangling_graph_edge(self):
        graph, _ = build_graph_data(
            self.case_dir,
            output_path=self.output_dir / "graph-data.json",
            quality_path=self.output_dir / "graph-quality.json",
        )
        broken = copy.deepcopy(graph)
        broken["edges"][0]["target"] = "missing:node"
        errors = validate(broken)
        self.assertTrue(any("dangling target" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
