import json
import hashlib
import tempfile
import unittest
from pathlib import Path

from tools.yamrail_ai_work_ticket_gate import evaluate_case, _parse_manifest_members, load_case, run_fixtures, write_receipt


PROJECT_ROOT = Path(__file__).resolve().parents[1]


class YamrailAiWorkTicketGateTests(unittest.TestCase):
    def test_six_required_fixture_decisions(self):
        results = run_fixtures(PROJECT_ROOT, None)
        self.assertEqual(
            [(result["case_id"], result["decision"]) for result in results[:6]],
            [
                ("T1_PASS", "PASS"),
                ("T2_HOLD", "HOLD"),
                ("T3_BLOCKED", "BLOCKED"),
                ("T4_STALE_APPROVAL", "HOLD"),
                ("T5_HASH_MISMATCH", "HOLD"),
                ("T6_PASS_AFTER_CORRECTION", "PASS"),
            ],
        )

    def test_receipt_has_required_fields_and_deterministic_body(self):
        with tempfile.TemporaryDirectory() as directory:
            first = Path(directory) / "first.json"
            second = Path(directory) / "second.json"
            result = next(item for item in run_fixtures(PROJECT_ROOT, None) if item["case_id"] == "T1_PASS")
            write_receipt(result, first, generated_at="2026-08-18T00:00:00+00:00")
            write_receipt(result, second, generated_at="2026-08-18T00:00:00+00:00")
            self.assertEqual(first.read_bytes(), second.read_bytes())
            receipt = json.loads(first.read_text(encoding="utf-8"))
            required = {
                "gate_schema_version",
                "work_order_id",
                "repository",
                "evaluated_head",
                "decision",
                "evidence_refs",
                "authority_refs",
                "human_gate_ref",
                "approval_target",
                "approval_freshness",
                "artifact_hash_results",
                "changed_paths",
                "precondition_results",
                "postcondition_results",
                "history_refs",
                "holds",
                "generated_at",
            }
            self.assertTrue(required.issubset(receipt))
            self.assertEqual(receipt["decision"], "PASS")
            self.assertEqual(receipt["approval_freshness"], "FRESH")
            self.assertEqual(receipt["holds"], [])

    def test_rework_negative_fixtures_hold_for_missing_bindings_and_artifacts(self):
        results = {result["case_id"]: result for result in run_fixtures(PROJECT_ROOT, None)}
        for case_id in (
            "T7_EMPTY_SOURCE_REFS",
            "T8_UNBOUND_HUMAN_GATE",
            "T9_WRONG_HUMAN_GATE_RECORD",
            "T10_EMPTY_ARTIFACT_REFS",
            "T11_FAILED_ARTIFACT_PRECONDITION",
            "T12_MANIFEST_UNSPECIFIED",
        ):
            self.assertEqual(results[case_id]["decision"], "HOLD")
        self.assertIn("SOURCE_REFS_REQUIRED", results["T7_EMPTY_SOURCE_REFS"]["holds"])
        self.assertIn("HUMAN_GATE_UNBOUND", results["T8_UNBOUND_HUMAN_GATE"]["holds"])
        self.assertIn(
            "HUMAN_GATE_RECORD_UNREACHABLE:HG-MISSING-001",
            results["T9_WRONG_HUMAN_GATE_RECORD"]["holds"],
        )
        self.assertIn("ARTIFACT_REFS_REQUIRED", results["T10_EMPTY_ARTIFACT_REFS"]["holds"])
        self.assertIn("ARTIFACT_INTEGRITY_FAILED", results["T10_EMPTY_ARTIFACT_REFS"]["holds"])
        self.assertEqual(results["T11_FAILED_ARTIFACT_PRECONDITION"]["precondition_results"]["artifact_integrity"]["status"], "FAIL")
        self.assertIn("MANIFEST_UNSPECIFIED", results["T12_MANIFEST_UNSPECIFIED"]["holds"])

    def test_pass_requires_all_required_preconditions(self):
        results = {result["case_id"]: result for result in run_fixtures(PROJECT_ROOT, None)}
        for case_id in ("T1_PASS", "T6_PASS_AFTER_CORRECTION"):
            self.assertEqual(results[case_id]["decision"], "PASS")
            self.assertTrue(
                all(
                    item["status"] == "PASS"
                    for item in results[case_id]["precondition_results"].values()
                )
            )

    def test_human_gate_binding_comes_from_evidence_file(self):
        base_case = load_case(PROJECT_ROOT / "tests" / "fixtures" / "base_case.json")
        base_case["human_gate"]["approval_target"] = {
            "head": "case-side-forbidden-value",
            "diff_sha256": "case-side-forbidden-value",
            "artifact_hash": "case-side-forbidden-value",
        }
        result = evaluate_case(base_case, PROJECT_ROOT / "tests" / "fixtures" / "common")
        self.assertEqual(result["decision"], "PASS")
        self.assertEqual(result["approval_target_source"], "HUMAN_GATE.yaml")
        self.assertEqual(result["approval_target"]["head"], "fixture-head")

        stale = next(
            item for item in run_fixtures(PROJECT_ROOT, None) if item["case_id"] == "T4_STALE_APPROVAL"
        )
        self.assertEqual(stale["decision"], "HOLD")
        self.assertEqual(stale["approval_target"]["head"], "fixture-head")
        self.assertIn("HUMAN_GATE_STALE", stale["holds"])

    def test_unsupported_acceptance_does_not_count_holds_or_blocked(self):
        results = run_fixtures(PROJECT_ROOT, None)
        self.assertTrue(
            all(
                result["metrics"]["unsupported_acceptance_count/rate"]["count"] == 0
                for result in results
            )
        )

    def test_manifest_member_paths_are_relative_to_manifest_directory(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            nested = root / "appendix" / "exemplar"
            nested.mkdir(parents=True)
            artifact = nested / "artifact.txt"
            artifact.write_text("nested artifact\n", encoding="utf-8")
            digest = hashlib.sha256(artifact.read_bytes()).hexdigest()
            (nested / "MANIFEST.yaml").write_text(
                "members:\n- path: artifact.txt\n  sha256: " + digest + "\n  bytes: 16\n",
                encoding="utf-8",
            )
            members = _parse_manifest_members(root, "appendix/exemplar/MANIFEST.yaml")
            self.assertEqual(members[0]["path"], "appendix/exemplar/artifact.txt")
            self.assertEqual(members[0]["sha256"], digest)


if __name__ == "__main__":
    unittest.main()
