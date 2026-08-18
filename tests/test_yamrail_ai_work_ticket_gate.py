import json
import hashlib
import tempfile
import unittest
from pathlib import Path

from tools.yamrail_ai_work_ticket_gate import _parse_manifest_members, run_fixtures, write_receipt


PROJECT_ROOT = Path(__file__).resolve().parents[1]


class YamrailAiWorkTicketGateTests(unittest.TestCase):
    def test_six_required_fixture_decisions(self):
        results = run_fixtures(PROJECT_ROOT, None)
        self.assertEqual(
            [(result["case_id"], result["decision"]) for result in results],
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

