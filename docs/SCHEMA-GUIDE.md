# Schema Guide

The chunk record demands ~35 required fields with `additionalProperties: false`. That is correct for governance and high-friction in practice — this guide tells you **what each field is, why it's required, and what to put when it doesn't apply to your deployment**.

Rule: a field never applies "sometimes as blank". If it doesn't apply, it carries an explicit **sentinel** (a visible, greppable value) — never `""` and never an invented plausible value. Fields that are genuinely optional are typed `["string","null"]` in the schema; everything else is mandatory by design.

## Chunk record ([`spec/schemas/gki.chunk-record.schema.json`](../spec/schemas/gki.chunk-record.schema.json))

### Identity & dataset
| Field | Why required | When N/A |
|---|---|---|
| `schema_version` | Pin the schema that validated this record | never N/A — `gki-1.0` |
| `doc_id` | Groups chunks of one document | never N/A |
| `dataset_id` / `dataset_version` | Which dataset+version this belongs to; enables reproducible re-index | set per config |
| `index_version` | Which index generation | `"1"` if unindexed |
| `chunk_index` / `chunk_id` | Ordinal + unique id within doc | never N/A |

### Provenance (the point of the system)
| Field | Why required | When N/A |
|---|---|---|
| `source_id` | Logical source (portal, drive, manual) | `local-manual-import` |
| `source_object_ref_hash` | sha256 of the exact source bytes | never N/A |
| `object_version` | Source-system version if any | `null` (optional field) |
| `provenance_ref` | Pointer to full provenance record | always emit a ref |
| `content_hash` | sha256 of chunk text — dedup + integrity | never N/A |

### Policy fingerprints (audit)
`scope_policy_fingerprint`, `labeling_policy_fingerprint`, `data_quality_policy_fingerprint`, `chunking_policy_fingerprint` — sha256 of each policy that shaped the record. **Never N/A**: even a permissive policy has a fingerprint. This is what lets you find every artifact made under a since-changed policy.

### Access control
| Field | Why required | When N/A |
|---|---|---|
| `acl_ref` | Who may see this chunk | single-user: sentinel `acl://reference/local-single-user`. **Not blank** — an empty ACL is indistinguishable from "world-readable", which is the exact failure this field prevents |

### Scope / labeling / quality outcomes
`scope_class`, `scope_confidence`, `labels`, `label_confidence` (nullable), `taxonomy_version`, `quality_score`, `quality_flags` — the gate results, carried so a consumer never re-derives them.

### Sensitive-data attestation
| Field | Why required | When N/A |
|---|---|---|
| `sensitive_data_status` | enum pass/blocked/redacted/quarantined/not_run | published records are always `pass` |
| `sensitive_data_scan_summary_ref` | Pointer to (content-free) scan summary | always a ref |
| `primary_detector_ruleset_id` + `_config_hash` | Which PII detector+config scanned this | reference profile: `REFERENCE_EU_PII_V1` |
| `secondary_detector_ruleset_id` + `_config_hash` | Which secrets detector+config | reference profile: `REFERENCE_SECRETS_V1` |

The detector **config hash** matters more than the ID: it proves not just "Presidio scanned this" but "Presidio *with these exact rules* scanned this". Change a rule, change the hash, and old records are distinguishable.

### Destinations & deletion
| Field | Why required | When N/A |
|---|---|---|
| `deletion_proof_ref` | Where the raw-deletion proof lives; reserved before serialization | never N/A |
| `sanitized_destination_uri` | Where the sanitized artifact went | local: `file://…/sanitized/` |
| `index_destination` | Where it was indexed | unindexed: sentinel `reference://not-indexed` |

### `extensions`
The only place `additionalProperties: true` is allowed. Anything not in the core schema lives here — scope audit block, primary labels, future fields. **Requiring `extensions` to exist** (even as `{}`) means "unknown data has exactly one legal home", which is what makes `additionalProperties: false` on everything else enforceable.

## Manifest ([`spec/schemas/gki.manifest.schema.json`](../spec/schemas/gki.manifest.schema.json))

Document-level twin of the chunk record: same provenance + fingerprints, plus `counts`, `hashes`, `run_stamps` (run_id, extraction timestamp, config version+hash), `scan_summaries`, `deletion_proofs_summary`, and refs to catalog/quality reports. One manifest per document; it's the audit entry point for that doc.

## Why `additionalProperties: false` is worth the friction

An open schema lets a well-meaning change add `customer_name` to a chunk record, and six months later that field is in your vector store, unredacted, because no gate knew to look at it. A closed schema makes every new field a deliberate decision that either goes through schema review or lands in `extensions` (which pass-2 sensitive scanning covers). The friction is the feature.
