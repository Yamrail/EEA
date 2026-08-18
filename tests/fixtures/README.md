# Gate fixtures

The six fixtures are repository-local synthetic tests only:

- `T1_PASS`: all required source, authority, approval, hash, postcondition, and history inputs are valid.
- `T2_HOLD`: a required source is unreachable.
- `T3_BLOCKED`: a changed path is outside explicit authority.
- `T4_STALE_APPROVAL`: the approved HEAD no longer matches the target HEAD.
- `T5_HASH_MISMATCH`: the manifest does not match the artifact.
- `T6_PASS_AFTER_CORRECTION`: a prior `HOLD` and corrective transition remain visible while the current result is `PASS`.

The fixture input is separate from the published canonical exemplar. It does not rewrite or replace any exemplar file.

