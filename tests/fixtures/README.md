# Gate fixtures

The fixtures are repository-local synthetic tests only:

- `T1_PASS`: all required source, authority, approval, hash, postcondition, and history inputs are valid.
- `T2_HOLD`: a required source is unreachable.
- `T3_BLOCKED`: a changed path is outside explicit authority.
- `T4_STALE_APPROVAL`: the approved HEAD no longer matches the target HEAD.
- `T5_HASH_MISMATCH`: the manifest does not match the artifact.
- `T6_PASS_AFTER_CORRECTION`: a prior `HOLD` and corrective transition remain visible while the current result is `PASS`.
- `T7_EMPTY_SOURCE_REFS`: an empty required-source list is `HOLD`.
- `T8_UNBOUND_HUMAN_GATE`: an approval without a non-empty target binding is `HOLD`.
- `T9_WRONG_HUMAN_GATE_RECORD`: an approval record absent from the referenced file is `HOLD`.
- `T10_EMPTY_ARTIFACT_REFS`: an empty artifact list and failed integrity precondition are `HOLD`.
- `T11_FAILED_ARTIFACT_PRECONDITION`: a manifest mismatch is `HOLD`.
- `T12_MANIFEST_UNSPECIFIED`: an omitted manifest is `HOLD`.

The fixture input is separate from the published canonical exemplar. It does not rewrite or replace any exemplar file.

Human Gate binding values are stored in `common/HUMAN_GATE.yaml` (or the named fixture Human Gate file). Case JSON may identify the Human Gate path and record, but its `approval_target` is never an approval source.
