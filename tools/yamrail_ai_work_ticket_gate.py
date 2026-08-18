#!/usr/bin/env python3
"""Small, dependency-free validation gate for the Yamrail/EEA PoC.

The gate evaluates an explicit JSON input against files already present in a
repository or fixture workspace. It never performs a repository mutation or
an external publication. A receipt is written only when the caller asks for
one.
"""

from __future__ import annotations

import argparse
import fnmatch
import hashlib
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


DECISIONS = {"PASS", "HOLD", "BLOCKED", "UNKNOWN"}
CANONICAL_EXEMPLAR_ROOT = Path("appendix/evidence_canonical_exemplar/20260816")


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _resolve(root: Path, relative: str) -> Path | None:
    """Resolve a repository-relative path without allowing traversal."""

    candidate = Path(relative)
    if candidate.is_absolute() or ".." in candidate.parts:
        return None
    resolved_root = root.resolve()
    resolved = (root / candidate).resolve()
    try:
        resolved.relative_to(resolved_root)
    except ValueError:
        return None
    return resolved


def _read_text(root: Path, relative: str) -> str | None:
    path = _resolve(root, relative)
    if path is None or not path.is_file():
        return None
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return None


def _parse_manifest_members(root: Path, manifest_path: str) -> list[dict[str, Any]]:
    """Parse the small `members` subset used by the canonical YAML manifest.

    This intentionally avoids a runtime YAML dependency. The parser accepts
    the repository's existing manifest form and the same subset in fixtures.
    """

    text = _read_text(root, manifest_path)
    if text is None:
        return []
    entries: list[dict[str, Any]] = []
    manifest_dir = Path(manifest_path).parent
    current: dict[str, Any] | None = None
    in_members = False
    for line in text.splitlines():
        if line.strip() == "members:":
            in_members = True
            continue
        if not in_members:
            continue
        member_match = re.match(r"^\s*-\s+path:\s+(.+?)\s*$", line)
        if member_match:
            if current:
                entries.append(current)
            member_path = member_match.group(1).strip().strip("'\"")
            normalized_path = str(manifest_dir / member_path).replace("\\", "/")
            current = {"path": normalized_path}
            continue
        if re.match(r"^\S", line) and not line.startswith("members:"):
            break
        if current is None:
            continue
        sha_match = re.match(r"^\s+sha256:\s+([0-9a-fA-F]{64})\s*$", line)
        if sha_match:
            current["sha256"] = sha_match.group(1).lower()
            continue
        bytes_match = re.match(r"^\s+bytes:\s+(\d+)\s*$", line)
        if bytes_match:
            current["bytes"] = int(bytes_match.group(1))
    if current:
        entries.append(current)
    return entries


def _ok(condition: bool, detail: str) -> dict[str, Any]:
    return {"status": "PASS" if condition else "FAIL", "detail": detail}


def _metric(passed: int, total: int) -> dict[str, Any]:
    rate = None if total == 0 else round(passed / total, 6)
    return {"count": passed, "total": total, "rate": rate}


def _all_refs_reachable(root: Path, refs: list[dict[str, Any]]) -> tuple[bool, list[dict[str, Any]], list[str]]:
    results: list[dict[str, Any]] = []
    holds: list[str] = []
    for ref in refs:
        relative = str(ref.get("path", ""))
        path = _resolve(root, relative)
        exists = path is not None and path.is_file()
        record_id = ref.get("record_id")
        content = None if not exists or path is None else path.read_text(encoding="utf-8", errors="replace")
        record_reachable = not record_id or (content is not None and str(record_id) in content)
        expected_sha = ref.get("sha256")
        actual_sha = _sha256(path) if exists and path is not None else None
        hash_ok = not expected_sha or actual_sha == str(expected_sha).lower()
        passed = exists and record_reachable and hash_ok
        results.append(
            {
                "record_id": record_id,
                "path": relative,
                "exists": exists,
                "record_reachable": record_reachable,
                "expected_sha256": expected_sha,
                "actual_sha256": actual_sha,
                "status": "PASS" if passed else "HOLD",
            }
        )
        if not passed:
            holds.append(f"SOURCE_UNREACHABLE:{relative}")
    return not holds, results, holds


def evaluate_case(case: dict[str, Any], root: Path) -> dict[str, Any]:
    """Evaluate one explicit gate case and return a receipt-shaped result."""

    work_order = case.get("work_order", {})
    authority = work_order.get("authority", {})
    target = case.get("target", {})
    changed_paths = [str(item) for item in case.get("changed_paths", [])]
    holds: list[str] = []
    blocked: list[str] = []

    source_refs = case.get("source_refs", [])
    source_pass, source_results, source_holds = _all_refs_reachable(root, source_refs)
    holds.extend(source_holds)

    allowed_repository = authority.get("repository")
    repository_ok = allowed_repository == case.get("repository")
    allowed_branch = authority.get("branch")
    branch_ok = allowed_branch == case.get("branch")
    allowed_operations = authority.get("operations", [])
    operation_ok = case.get("operation") in allowed_operations
    allowed_paths = authority.get("paths", [])
    path_results = {
        path: any(fnmatch.fnmatch(path, pattern) for pattern in allowed_paths)
        for path in changed_paths
    }
    paths_ok = all(path_results.values())
    authority_pass = repository_ok and branch_ok and operation_ok and paths_ok
    if not authority_pass:
        blocked.append("AUTHORITY_OUTSIDE_EXPLICIT_SCOPE")

    human_gate = case.get("human_gate", {})
    gate_ref = human_gate.get("path", "")
    gate_path = _resolve(root, gate_ref)
    gate_reachable = gate_path is not None and gate_path.is_file()
    approval_target = human_gate.get("approval_target", {})
    target_fields = ("head", "diff_sha256", "artifact_hash")
    freshness_matches = all(approval_target.get(field) == target.get(field) for field in target_fields)
    approval_fresh = human_gate.get("decision") == "APPROVE" and freshness_matches
    if not gate_reachable:
        holds.append(f"HUMAN_GATE_UNREACHABLE:{gate_ref}")
    elif human_gate.get("decision") != "APPROVE":
        holds.append("HUMAN_GATE_NOT_APPROVED")
    elif not freshness_matches:
        holds.append("HUMAN_GATE_STALE")

    manifest_path = str(case.get("manifest_path", ""))
    manifest_entries = _parse_manifest_members(root, manifest_path)
    manifest_by_path = {str(entry.get("path")): entry for entry in manifest_entries}
    artifact_results: list[dict[str, Any]] = []
    for artifact in case.get("artifact_refs", []):
        relative = str(artifact.get("path", ""))
        path = _resolve(root, relative)
        exists = path is not None and path.is_file()
        actual_sha = _sha256(path) if exists and path is not None else None
        manifest_entry = manifest_by_path.get(relative)
        expected_sha = None if manifest_entry is None else manifest_entry.get("sha256")
        hash_ok = exists and expected_sha is not None and actual_sha == expected_sha
        size_ok = exists and manifest_entry is not None and path.stat().st_size == manifest_entry.get("bytes")
        passed = hash_ok and size_ok
        artifact_results.append(
            {
                "path": relative,
                "manifest_expected_sha256": expected_sha,
                "actual_sha256": actual_sha,
                "manifest_expected_bytes": None if manifest_entry is None else manifest_entry.get("bytes"),
                "actual_bytes": None if not exists or path is None else path.stat().st_size,
                "status": "PASS" if passed else "HOLD",
            }
        )
        if not passed:
            holds.append(f"ARTIFACT_HASH_MISMATCH:{relative}")
    artifact_pass = bool(artifact_results) and all(item["status"] == "PASS" for item in artifact_results)

    postcondition = case.get("postcondition", {})
    required_postcondition_fields = ("precondition", "operation_scope", "postcondition", "artifact_hash_state")
    postcondition_complete = all(postcondition.get(field) for field in required_postcondition_fields)
    postcondition_pass = postcondition_complete and postcondition.get("verified") is True
    if not postcondition_pass:
        holds.append("POSTCONDITION_UNVERIFIED")

    history_results: list[dict[str, Any]] = []
    history_pass = True
    for history in case.get("history_refs", []):
        relative = str(history.get("path", ""))
        content = _read_text(root, relative)
        required_states = [str(state) for state in history.get("required_states", [])]
        states_present = all(state in (content or "") for state in required_states)
        passed = content is not None and states_present
        history_results.append({"path": relative, "required_states": required_states, "status": "PASS" if passed else "HOLD"})
        history_pass = history_pass and passed
        if not passed:
            holds.append(f"HISTORY_NOT_PRESERVED:{relative}")

    determinations = case.get("determinations", [])
    reachability_results: list[dict[str, Any]] = []
    reachability_pass = True
    for determination in determinations:
        relative = str(determination.get("path", ""))
        record_id = str(determination.get("record_id", ""))
        content = _read_text(root, relative)
        passed = bool(content is not None and record_id and record_id in content)
        reachability_results.append(
            {"statement": determination.get("statement"), "record_id": record_id, "path": relative, "status": "PASS" if passed else "HOLD"}
        )
        reachability_pass = reachability_pass and passed
        if not passed:
            holds.append(f"EVIDENCE_NOT_REACHABLE:{record_id}:{relative}")

    decision = "BLOCKED" if blocked else "HOLD" if holds else "PASS"
    if decision not in DECISIONS:
        decision = "UNKNOWN"

    metric_totals = {
        "unsupported_acceptance_count/rate": _metric(1 if decision != "PASS" else 0, 1),
        "evidence_reachability_count/rate": _metric(sum(item["status"] == "PASS" for item in reachability_results), len(reachability_results)),
        "unauthorized_action_block_count/rate": _metric(1 if blocked else 0, 1),
        "stale_approval_detection_count/rate": _metric(1 if human_gate.get("decision") == "APPROVE" and not freshness_matches else 0, 1),
        "postcondition_mismatch_detection_count/rate": _metric(1 if not postcondition_pass else 0, 1),
        "false_hold_count/rate": None,
        "history_preservation_count/rate": _metric(sum(item["status"] == "PASS" for item in history_results), len(history_results)),
    }

    return {
        "case_id": case.get("case_id"),
        "gate_schema_version": "YAMRAIL_AI_WORK_TICKET_GATE_V1",
        "work_order_id": work_order.get("work_order_id"),
        "repository": case.get("repository"),
        "evaluated_head": target.get("head"),
        "decision": decision,
        "evidence_refs": source_results + reachability_results,
        "authority_refs": {
            "repository": {"expected": allowed_repository, "actual": case.get("repository"), "status": "PASS" if repository_ok else "BLOCKED"},
            "branch": {"expected": allowed_branch, "actual": case.get("branch"), "status": "PASS" if branch_ok else "BLOCKED"},
            "operation": {"allowed": allowed_operations, "actual": case.get("operation"), "status": "PASS" if operation_ok else "BLOCKED"},
            "paths": {"allowed": allowed_paths, "changed": path_results, "status": "PASS" if paths_ok else "BLOCKED"},
        },
        "human_gate_ref": gate_ref,
        "approval_target": approval_target,
        "approval_freshness": "FRESH" if approval_fresh else "STALE" if gate_reachable and human_gate.get("decision") == "APPROVE" else "UNKNOWN",
        "artifact_hash_results": artifact_results,
        "changed_paths": changed_paths,
        "precondition_results": {
            "source_reachability": _ok(source_pass, "all required source refs are reachable and exact"),
            "authority_boundary": _ok(authority_pass, "repository, branch, path, and operation remain in explicit scope"),
            "human_gate": _ok(gate_reachable and human_gate.get("decision") == "APPROVE", "Human Gate ref is reachable and approved"),
            "artifact_integrity": _ok(artifact_pass, "manifest SHA-256 and byte counts match"),
        },
        "postcondition_results": {
            "complete": postcondition_complete,
            "verified": postcondition.get("verified") is True,
            "operation_scope": postcondition.get("operation_scope"),
            "artifact_hash_state": postcondition.get("artifact_hash_state"),
        },
        "history_refs": history_results,
        "holds": sorted(set(holds)),
        "blocked": sorted(set(blocked)),
        "evidence_reachability": reachability_results,
        "metrics": metric_totals,
        "baseline_comparison": {
            "ordinary_github_mechanisms": ["GitHub review", "branch rules", "status checks"],
            "poc_additions": [
                "artifact hash verification",
                "explicit work-order authority",
                "source reachability",
                "stale approval detection",
                "HOLD/UNKNOWN preservation",
                "acceptance receipt",
            ],
            "overlap": ["status checks", "human review remains external to this script"],
            "replacement_conditions": ["NOT_DEFINED_BY_THIS_POC"],
            "claim_boundary": "No superiority or certification claim is made.",
        },
    }


def write_receipt(result: dict[str, Any], destination: Path, generated_at: str | None = None) -> None:
    receipt = dict(result)
    receipt["generated_at"] = generated_at or datetime.now(timezone.utc).isoformat(timespec="seconds")
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(receipt, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def load_case(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _deep_merge(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    merged = dict(base)
    for key, value in override.items():
        if isinstance(value, dict) and isinstance(merged.get(key), dict):
            merged[key] = _deep_merge(merged[key], value)
        else:
            merged[key] = value
    return merged


def run_fixtures(project_root: Path, receipt: Path | None) -> list[dict[str, Any]]:
    fixture_root = project_root / "tests" / "fixtures"
    base_case = load_case(fixture_root / "base_case.json")
    results: list[dict[str, Any]] = []
    for case_path in sorted(fixture_root.glob("T*/case.json")):
        case = _deep_merge(base_case, load_case(case_path))
        workspace = fixture_root / str(case["workspace"])
        result = evaluate_case(case, workspace)
        expected = case.get("expected_decision")
        if result["decision"] != expected:
            raise AssertionError(f"{case['case_id']}: expected {expected}, got {result['decision']}")
        results.append(result)
    if len(results) != 6:
        raise AssertionError(f"expected 6 fixtures, found {len(results)}")
    if receipt is not None:
        pass_result = next(item for item in results if item["case_id"] == "T1_PASS")
        write_receipt(pass_result, receipt)
    return results


def validate_published_exemplar(project_root: Path) -> dict[str, Any]:
    """Validate the published exemplar without changing its canonical state."""

    root = project_root.resolve()
    manifest = CANONICAL_EXEMPLAR_ROOT / "MANIFEST.yaml"
    members = _parse_manifest_members(root, str(manifest))
    member_results: list[dict[str, Any]] = []
    for member in members:
        relative = str(member["path"])
        path = _resolve(root, relative)
        exists = path is not None and path.is_file()
        actual_sha = _sha256(path) if exists and path is not None else None
        actual_bytes = path.stat().st_size if exists and path is not None else None
        member_results.append(
            {
                "path": relative,
                "exists": exists,
                "sha256_match": exists and actual_sha == member.get("sha256"),
                "bytes_match": exists and actual_bytes == member.get("bytes"),
                "status": "PASS" if exists and actual_sha == member.get("sha256") and actual_bytes == member.get("bytes") else "HOLD",
            }
        )
    required_paths = [
        "01_ORDER/WORK_ORDER.yaml",
        "02_EVIDENCE/FIELD_RECORD.yaml",
        "03_INSPECTION/INSPECTION_RESULT.yaml",
        "04_HOLD/HOLD_REGISTER.yaml",
        "05_CANONICAL/CANONICAL_POINTER.yaml",
        "06_HISTORY/CHANGE_HISTORY.yaml",
        "HUMAN_GATE.yaml",
    ]
    reachability = {}
    for relative in required_paths:
        candidate = str(CANONICAL_EXEMPLAR_ROOT / relative).replace("\\", "/")
        resolved = _resolve(root, candidate)
        reachability[candidate] = resolved is not None and resolved.is_file()
    human_gate_text = _read_text(root, str(CANONICAL_EXEMPLAR_ROOT / "HUMAN_GATE.yaml")) or ""
    canonical_change_hold = bool(re.search(r"canonical_change:\s*\n\s+state:\s+HOLD", human_gate_text))
    passed = bool(members) and all(item["status"] == "PASS" for item in member_results) and all(reachability.values()) and canonical_change_hold
    return {
        "canonical_exemplar_root": str(CANONICAL_EXEMPLAR_ROOT).replace("\\", "/"),
        "manifest": str(manifest).replace("\\", "/"),
        "member_count": len(member_results),
        "member_results": member_results,
        "required_paths": reachability,
        "existing_canonical_change_human_gate": "HOLD" if canonical_change_hold else "UNKNOWN",
        "status": "PASS" if passed else "HOLD",
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-fixtures", action="store_true")
    parser.add_argument("--validate-exemplar", action="store_true")
    parser.add_argument("--project-root", type=Path, default=Path.cwd())
    parser.add_argument("--receipt", type=Path)
    args = parser.parse_args(argv)
    if not args.run_fixtures and not args.validate_exemplar:
        parser.error("select --run-fixtures and/or --validate-exemplar")
    if args.validate_exemplar:
        exemplar = validate_published_exemplar(args.project_root.resolve())
        print(f"published exemplar: {exemplar['status']} ({exemplar['member_count']} manifest members)")
        if exemplar["status"] != "PASS":
            return 1
    if args.run_fixtures:
        results = run_fixtures(args.project_root.resolve(), args.receipt.resolve() if args.receipt else None)
        for result in results:
            print(f"{result['case_id']}: {result['decision']}")
    if args.receipt:
        print(f"receipt: {args.receipt}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

