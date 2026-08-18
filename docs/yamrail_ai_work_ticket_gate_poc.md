# Yamrail AI work-ticket gate PoC

This repository-local PoC connects the published evidence canonical exemplar to one small GitHub Actions status check named `yamrail-ai-work-ticket-gate`.

It validates only explicit fixture input. The validator does not mutate Git refs, merge branches, publish releases, change repository settings, or perform external publication.

## What the check evaluates

- source and evidence reachability by exact path and record identifier;
- repository, branch, changed-path, and operation authority boundaries;
- Human Gate approval freshness against the target HEAD, diff hash, and artifact hash;
- SHA-256 and byte-count integrity from a manifest;
- machine-readable precondition and postcondition results;
- preservation of `HOLD`, failure, `UNKNOWN`, corrective transition, and history references; and
- exact evidence reachability for material determinations.

The six synthetic fixtures cover PASS, missing-source HOLD, unauthorized-scope BLOCKED, stale approval HOLD, hash-mismatch HOLD, and PASS after correction with prior state retained.

## Boundary of the comparison

Ordinary GitHub review, branch rules, and status checks remain ordinary GitHub mechanisms. The PoC adds explicit work-order authority, source reachability, artifact verification, stale-approval detection, history preservation, and an acceptance receipt. The overlap is recorded in the receipt; replacement conditions are intentionally `NOT_DEFINED_BY_THIS_POC`.

This PoC does not claim superiority over GitHub, OPA, SLSA, ITSM, or any certification/compliance framework.

## Receipt

The workflow generates `yamrail-ai-work-ticket-gate.receipt.json` and retains it as a workflow artifact. All fields other than `generated_at` are derived from the fixture and evaluation target, so repeated evaluations can be compared without relying on a timestamp.

