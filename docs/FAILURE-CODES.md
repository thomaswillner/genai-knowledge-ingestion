# BLOCKED Reason Codes — Complete Reference

Every gate failure carries exactly one of these codes. Codes are stable API: ledgers, tests, and automation match on them.

## Pre-flight (spec §2)

| Code | Gate | Meaning | Operator action |
|---|---|---|---|
| `config_invalid` | CONFIG_VALIDATION_GATE | Required config key null/missing | Fill the key; nulls never default |
| `tika_unavailable` | TIKA_HEALTH_GATE | Parsing layer down (standard/enterprise) | Restore Tika or ingest text via reference path |
| `legal_basis_missing` | LEGAL_BASIS_GATE | Portal domain lacks legal-basis record | Record legal basis before retrieval |
| `retention_exception_missing` | RETENTION_EXCEPTION_GATE | EU + raw retention >0 without exception record | Provide exception record or set retention 0 |

## Retrieval (spec §3, enterprise)

| Code | Meaning |
|---|---|
| `domain_not_allowed` | URL outside `domain_allowlist` — no wild crawling, ever |
| `portal_rate_limited` | 403/429 hit; URL in cooldown |
| `mfa_handoff_timeout` | Operator did not complete headed-mode MFA in time |
| `archive_policy_violation` | Archive exceeds zip/rar policy bounds |

## Extraction & tokenization

| Code | Meaning |
|---|---|
| `tokenizer_unavailable` | cl100k_base (tiktoken) missing — deliberately no fallback |

## Sensitive data (spec §5 — 3 enforcement points)

| Code | Meaning |
|---|---|
| `sensitive_data_violation` | Unremediated PII/secret at pass 1 (pre-persist), 2 (derived fields), or 3 (post-export). Raw/output destroyed; findings ledgered with 8-char previews |
| `presidio_endpoint_missing` | Presidio configured but endpoint null (enterprise) |
| `gitleaks_path_missing` / `gitleaks_image_missing` | Gitleaks exec mode configured without binary/image |

## Scope gate (spec §6)

| Code | Meaning |
|---|---|
| `scope_out_of_scope` | Deny threshold met. **Final — never overridden by confidence** |
| `scope_gate_low_confidence` | Neither confidently in scope nor denied → fail closed |
| `scope_classifier_config_missing` | `scope_policy.classifier_v1` absent (mandatory v16+) |
| `scope_conformance_test_failed` | Harness cannot prove classifier_v1 semantics |

## Labeling (spec §7)

| Code | Meaning |
|---|---|
| `labeling_no_match_undefined` | Policy lacks `no_match_action` |
| `labeling_confidence_mode_missing` | Policy lacks (or impl doesn't support) `confidence_mode` |
| `labeling_conformance_test_failed` | Base conformance case fails |
| `labeling_conformance_suite_incomplete` | No-match / cap / tie-break cases missing |

## Quality (spec §8)

| Code | Meaning |
|---|---|
| `data_quality_gate` | `quality_score < min_quality_score` (flags in detail) |
| `quality_rubric_config_missing` | `quality_policy.scoring_rubric_v1` absent |
| `quality_conformance_test_failed` | Conformance cases fail |

## Serialization (spec §10)

| Code | Meaning |
|---|---|
| `schema_missing_required_field` | Record missing a required field |
| `schema_unknown_field` | Field outside schema and outside `extensions` |
| `schema_validation_failed` | Any other schema violation |

## Deletion & completion (spec §11, §13)

| Code | Meaning |
|---|---|
| `deletion_proof_ref_not_reserved` | Proof ref not reserved before serialization |
| `done_gate_failed` | One-command harness missing a mandatory suite |
