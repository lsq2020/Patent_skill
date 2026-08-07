import csv
import json
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from build_case_output import build_case_output  # noqa: E402
from validate_output_schema import validate  # noqa: E402


class CaseOutputContractTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.project = Path(self.temp.name) / "sample-case"
        self.project.mkdir()
        (self.project / "research_scope.json").write_text(
            json.dumps(
                {
                    "research_object": {
                        "molecule": "Example molecule",
                        "target": "Target A",
                        "indication": "Example indication",
                    },
                    "jurisdictions": ["US"],
                    "related_jurisdictions": ["WO"],
                    "as_of": "2026-08-07",
                    "depth": "standard_analysis",
                    "focus": ["compound"],
                }
            ),
            encoding="utf-8",
        )
        (self.project / "identity.json").write_text("{}", encoding="utf-8")
        self._write_csv(
            "sample-patent-families.csv",
            [
                {
                    "family_id": "FAM-001",
                    "family_definition": "DOCDB simple family",
                    "representative_document": "US100B2",
                    "representative_application": "US10/001",
                    "grants": "US100B2",
                    "members": "US100A1;WO100A1",
                    "priority_set": "US-P-001",
                    "parent_family_id": "",
                    "continuity_relation": "",
                    "related_family_ids": "",
                    "earliest_priority": "2020-01-01",
                    "applicant_or_assignee": "Example Bio",
                    "jurisdictions": "US;WO",
                    "claim_theme": "Composition",
                    "claim_categories": "composition",
                    "source_url": "https://example.test/patent/US100B2",
                },
                {
                    "family_id": "FAM-002",
                    "family_definition": "DOCDB simple family",
                    "representative_document": "US200A1",
                    "representative_application": "US20/002",
                    "grants": "",
                    "members": "US200A1",
                    "priority_set": "US-P-001",
                    "parent_family_id": "FAM-001",
                    "continuity_relation": "DIVISIONAL_OF",
                    "related_family_ids": "",
                    "earliest_priority": "2021-01-01",
                    "applicant_or_assignee": "Example Bio",
                    "jurisdictions": "US",
                    "claim_theme": "Use",
                    "claim_categories": "use",
                    "source_url": "https://example.test/patent/US200A1",
                },
            ],
        )
        self.claims = [
            {
                "family_id": "FAM-001",
                "document": "US100B2",
                "claim_category": "composition",
                "element": "Sequence-defined antibody",
                "coverage": "explicit",
                "claim_location": "claim 1",
                "evidence_url": "https://example.test/patent/US100B2",
                "confidence": "high",
            },
            {
                "family_id": "FAM-002",
                "document": "US200A1",
                "claim_category": "use",
                "element": "Treatment of an indicated patient group",
                "coverage": "possible",
                "claim_location": "claim 12",
                "evidence_url": "https://example.test/patent/US200A1",
                "confidence": "medium",
            },
        ]
        self._write_csv("sample-claim-elements.csv", self.claims)
        self._write_csv(
            "sample-evidence.csv",
            [
                {
                    "finding_id": "FIND-001",
                    "conclusion_or_fact": "The granted document contains claim 1.",
                    "evidence_type": "patent_text",
                    "source_url": "https://example.test/patent/US100B2",
                    "document_no": "US100B2",
                    "claim_or_event_location": "claim 1",
                    "captured_at": "2026-08-07",
                    "direct_fact_or_inference": "direct_fact",
                    "confidence": "high",
                    "reviewer_action": "Verify register status",
                }
            ],
        )

    def tearDown(self):
        self.temp.cleanup()

    def _write_csv(self, name, rows):
        path = self.project / name
        with path.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
            writer.writeheader()
            writer.writerows(rows)

    def test_builds_stable_ids_and_first_class_relations(self):
        output = build_case_output(self.project)

        self.assertEqual("1.1", output["schema_version"])
        self.assertEqual([], validate(output))
        claim_ids = [row["claim_id"] for row in output["records"]["claims"]]
        self.assertEqual(2, len(set(claim_ids)))
        self.assertTrue(all(value.startswith("CLM-") for value in claim_ids))

        evidence = output["records"]["evidence"][0]
        self.assertEqual(["FAM-001"], evidence["family_ids"])
        self.assertEqual([claim_ids[0]], evidence["claim_ids"])

        relation_keys = {
            (row["source_id"], row["relation_type"], row["target_id"])
            for row in output["records"]["relations"]
        }
        self.assertIn(("family:FAM-001", "HAS_CLAIM", f"claim:{claim_ids[0]}"), relation_keys)
        self.assertIn(("family:FAM-001", "SUPPORTED_BY", "finding:FIND-001"), relation_keys)
        self.assertIn((f"claim:{claim_ids[0]}", "SUPPORTED_BY", "finding:FIND-001"), relation_keys)
        self.assertIn(("family:FAM-002", "DIVISIONAL_OF", "family:FAM-001"), relation_keys)
        self.assertIn(("family:FAM-001", "HAS_MEMBER", "document:US100A1"), relation_keys)

    def test_generated_claim_ids_do_not_depend_on_csv_row_order(self):
        first = build_case_output(self.project)
        first_by_element = {
            row["element"]: row["claim_id"] for row in first["records"]["claims"]
        }
        self._write_csv("sample-claim-elements.csv", list(reversed(self.claims)))

        second = build_case_output(self.project)
        second_by_element = {
            row["element"]: row["claim_id"] for row in second["records"]["claims"]
        }
        self.assertEqual(first_by_element, second_by_element)

    def test_validator_rejects_dangling_relation(self):
        output = build_case_output(self.project)
        output["records"]["relations"][0]["target_id"] = "claim:missing"
        errors = validate(output)
        self.assertTrue(any("dangling target_id" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
