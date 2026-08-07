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

        self.assertEqual("1.1", graph["schema_version"])
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
                "causal_concept",
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
            {"family", "technology", "evidence", "applicant", "causal"},
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
            any(gap["code"] == "family_relations_partial" for gap in quality["gaps"])
        )

        filed_by_labels = {
            next(node["label"] for node in graph["nodes"] if node["id"] == edge["target"])
            for edge in graph["edges"]
            if edge["source"] == "family:DVL-FAM-002" and edge["type"] == "FILED_BY"
        }
        self.assertEqual(
            {"C/o Definiens AG", "Definiens AG", "MedImmune LLC"},
            filed_by_labels,
        )
        family_007 = next(
            node for node in graph["nodes"] if node["id"] == "family:DVL-FAM-007"
        )
        self.assertIn("ceased", family_007["properties"]["official_status"].lower())
        self.assertTrue(
            any(
                edge["source"] == "document:CN120936347A"
                and edge["type"] == "NATIONAL_PHASE_OF"
                and edge["target"] == "document:WO2024213696A1"
                for edge in graph["edges"]
            )
        )
        self.assertEqual(5, quality["metrics"]["member_relation_edge_count"])

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

    def test_causal_preset_exposes_patent_context_without_promoting_it_to_causality(self):
        graph, quality = build_graph_data(
            self.case_dir,
            output_path=self.output_dir / "graph-data.json",
            quality_path=self.output_dir / "graph-quality.json",
        )

        causal_preset = next(row for row in graph["presets"] if row["id"] == "causal")
        self.assertTrue(
            {
                "research_object",
                "target",
                "indication",
                "patent_family",
                "claim",
                "technology_theme",
                "causal_concept",
                "evidence",
                "source",
            }.issubset(causal_preset["node_types"])
        )
        self.assertTrue(
            {"IN_SCOPE", "PROTECTS", "HAS_CLAIM", "SUPPORTED_BY", "HAS_SOURCE"}.issubset(
                causal_preset["relation_types"]
            )
        )

        research_id = "research:durvalumab-pdl1-nsclc"
        concept_ids = {
            node["id"] for node in graph["nodes"] if node["type"] == "causal_concept"
        }
        context_edges = [
            edge
            for edge in graph["edges"]
            if edge["source"] == research_id
            and edge["target"] in concept_ids
            and edge["type"] == "IN_SCOPE"
        ]
        self.assertEqual(concept_ids, {edge["target"] for edge in context_edges})
        self.assertTrue(
            all(
                edge["relation_kind"] == "structural"
                and edge["causal_status"] == "not_applicable"
                for edge in context_edges
            )
        )

        eligible_nodes = {
            node["id"]
            for node in graph["nodes"]
            if node["type"] in causal_preset["node_types"]
        }
        eligible_edges = [
            edge
            for edge in graph["edges"]
            if edge["type"] in causal_preset["relation_types"]
            and edge["source"] in eligible_nodes
            and edge["target"] in eligible_nodes
        ]
        visible = {"concept:C-DURVALUMAB"}
        frontier = set(visible)
        for _ in range(causal_preset["default_depth"]):
            next_frontier = {
                endpoint
                for edge in eligible_edges
                for endpoint in (edge["source"], edge["target"])
                if (edge["source"] in frontier or edge["target"] in frontier)
            }
            visible.update(next_frontier)
            frontier = next_frontier

        visible_types = {
            node["type"] for node in graph["nodes"] if node["id"] in visible
        }
        self.assertGreaterEqual(len(visible), 40)
        self.assertTrue(
            {"patent_family", "claim", "technology_theme"}.issubset(visible_types)
        )
        self.assertEqual(1.0, quality["metrics"]["causal_context_coverage_rate"])
        self.assertTrue(quality["checks"]["all_causal_concepts_in_scope"])

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

    def test_builds_auditable_causal_nodes_edges_and_preset(self):
        source = json.loads((self.case_dir / "case-output.json").read_text(encoding="utf-8"))
        source["schema_version"] = "1.2"
        source["records"]["evidence"] = [
            row for row in source["records"]["evidence"] if not row.get("concept_ids")
        ]
        source["records"]["relations"] = [
            row
            for row in source["records"]["relations"]
            if not row["source_id"].startswith("concept:")
            and not row["target_id"].startswith("concept:")
        ]
        source["records"]["concepts"] = [
            {
                "concept_id": "C-DRUG",
                "concept_type": "intervention",
                "label": "Durvalumab after chemoradiotherapy",
                "description": "Defined intervention.",
                "source_urls": ["https://example.test/trial"],
            },
            {
                "concept_id": "C-OUTCOME",
                "concept_type": "clinical_outcome",
                "label": "Progression or death",
                "description": "Randomized trial endpoint.",
                "source_urls": ["https://example.test/trial"],
            },
        ]
        source["records"]["evidence"].append(
            {
                "finding_id": "CAUSE-001",
                "conclusion_or_fact": "Randomization supports a treatment effect.",
                "evidence_type": "randomized_trial",
                "source_url": "https://example.test/trial",
                "family_ids": [],
                "claim_ids": [],
                "concept_ids": ["C-DRUG", "C-OUTCOME"],
                "link_methods": ["explicit_concept_id"],
                "confidence": "high",
            }
        )
        source["records"]["relations"].append(
            {
                "relation_id": "REL-CAUSAL",
                "source_id": "concept:C-DRUG",
                "relation_type": "REDUCES_RISK_OF",
                "target_id": "concept:C-OUTCOME",
                "assertion": "direct_fact",
                "link_methods": ["curated_causal_relation"],
                "evidence_ids": ["CAUSE-001"],
                "properties": {"population": "Trial population"},
                "relation_kind": "causal",
                "causal_status": "established",
                "polarity": "negative",
                "directness": "total_effect",
                "evidence_level": "randomized_trial",
                "confidence": "high",
                "rationale": "Randomized placebo comparison.",
                "source_urls": ["https://example.test/trial"],
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

        self.assertEqual("1.1", graph["schema_version"])
        self.assertEqual([], validate(graph))
        concept = next(node for node in graph["nodes"] if node["id"] == "concept:C-DRUG")
        self.assertEqual("causal_concept", concept["type"])
        self.assertEqual("intervention", concept["facets"]["concept_type"][0])
        edge = next(row for row in graph["edges"] if row["id"] == "REL-CAUSAL")
        self.assertEqual("causal", edge["relation_kind"])
        self.assertEqual("established", edge["causal_status"])
        self.assertEqual("randomized_trial", edge["evidence_level"])
        causal_preset = next(row for row in graph["presets"] if row["id"] == "causal")
        self.assertIn("causal_concept", causal_preset["node_types"])
        self.assertIn("REDUCES_RISK_OF", causal_preset["relation_types"])
        self.assertEqual(1, quality["metrics"]["causal_relation_count"])

    def test_validator_rejects_causal_graph_edges_without_provenance(self):
        graph, _ = build_graph_data(
            self.case_dir,
            output_path=self.output_dir / "graph-data.json",
            quality_path=self.output_dir / "graph-quality.json",
        )
        broken = copy.deepcopy(graph)
        broken["schema_version"] = "1.1"
        broken["edges"][0].update(
            {
                "relation_kind": "causal",
                "causal_status": "established",
                "evidence_ids": [],
                "source_urls": [],
                "rationale": "",
            }
        )

        errors = validate(broken)

        self.assertTrue(any("causal edge requires evidence_ids" in error for error in errors))
        self.assertTrue(any("causal edge requires source_urls" in error for error in errors))
        self.assertTrue(any("causal edge requires rationale" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
