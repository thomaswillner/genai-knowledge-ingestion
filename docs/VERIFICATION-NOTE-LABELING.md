# Verification Note: Spec-Conformance Tests (Labeling)

Why this exists
- The spec defines a deterministic labeling algorithm (label_quality scoring, min_occurrences filter, section_weighting, primary label selection).
- Schemas and fixtures prove *structure* and provide *inputs*, but they do not prove an implementation matches the algorithm.

What is required (mandatory for VERIFY/DONE)
- The one-command test harness must include **algorithm conformance tests** ("golden tests") for labeling:
  - Run the labeling module against `tests/fixtures/synthetic_iam_runbook.txt`
  - Use labeling policy `LABELING_MIN_V2`
  - Assert deterministic outputs:
    - `labels` contains `"IAM"`
    - `extensions.labeling.primary_labels.domain_tags == "IAM"`
    - `label_confidence == 1.0` when labels are non-empty (rule_binary mode)

Scope
- This is a harness requirement, not a schema requirement.
- This is knowable and deterministic; it must be verified in CI to prevent drift between spec and implementation.

Rationale
- Without an executable conformance test, a correct-looking implementation can silently diverge (thresholding semantics, weighting, tie-breakers).


Cap fixture expectation
- For tests/fixtures/label_cap_many_domains.txt under LABELING_MIN_V2, tie-breaking is lexicographic when scores are equal.
- Expected: extensions.labeling.primary_labels.domain_tags == "CloudSec" (C < I).
