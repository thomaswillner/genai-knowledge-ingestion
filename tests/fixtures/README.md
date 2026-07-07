# Test Fixtures

Contents
- synthetic_iam_runbook.txt
  - synthetic-only input containing PII + secrets patterns to validate gating.
- schema_valid_chunk.json / schema_valid_manifest.json
  - strict-schema valid examples to validate JSON schema enforcement.

Intended usage
- The build agent must create a one-command test harness which:
  - validates these JSON files against the strict schemas under /spec/schemas/
  - uses synthetic_iam_runbook.txt as a dry-run pipeline input

Note
- The JSON schema fixtures validate schema structure only, not value correctness (e.g., hashes). Value correctness must be verified by the one-command test harness dry-run.

Conformance requirement
- In addition to schema validation, the harness must run labeling algorithm conformance tests (see docs/VERIFICATION-NOTE-LABELING.md).

Additional fixtures (v16)
- scope_*: scope classifier conformance cases
- quality_*: quality scoring conformance cases
- label_*: labeling conformance suite extension cases
