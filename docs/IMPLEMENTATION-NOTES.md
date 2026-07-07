# Implementation Notes

Clarifications surfaced by actually building the reference implementation against the canonical spec. A spec that has never been executed hides ambiguities; these are the ones building it exposed. None change the spec's intent — they pin down under-specified corners so any two implementations agree.

## 1. Short documents yield one chunk

Spec §9 step 5 says each chunk's token length must be between `min_chunk_tokens` and `max_chunk_tokens_hard_cap`. Read naively, a 12-token document would violate `min_chunk_tokens=100` and have no legal output. Resolution: **the minimum governs split points, not whole documents.** A document shorter than `min_chunk_tokens` produces exactly one chunk containing all its tokens. Enforced by `test_short_document_single_chunk`.

## 2. Deterministic segmentation needs a concrete title/heading rule

Spec Appendix A references `title_text`, `headings_text`, `body_text` but leaves extraction of them to the (format-specific) parser. For the reference profile's text inputs this must be pinned or scope/labeling scores drift between implementations. Chosen rule: `TITLE:` prefix on line 1 → title; markdown `#`-prefixed lines → headings; remainder → body. Documented in `extract.py`; standard/enterprise profiles get title/headings from Tika metadata but MUST feed the same three-section model downstream.

## 3. `label_quality` raw filter precedes weighted scoring

Spec Appendix A specifies both a `min_occurrences` raw (unweighted) filter and `section_weighting` scoring, but order matters: a single title hit with weight 5 scores well above a `min_occurrences=2` threshold if you filter on the weighted score. The spec's intent (confirmed by the fixture design) is **raw-count filter first, then weighted ranking of survivors**. `test_min_occurrences_raw_filter` locks this: `TITLE: SIEM` with one occurrence is dropped despite weighted score 5.

## 4. Deny-final ordering must precede confidence in code, not just prose

Spec §6 fixes the v18 defect ("OUT_OF_SCOPE by deny_threshold MUST NOT be overridden by confidence"). In code this means the deny check must be the *first* branch of the decision, before any confidence comparison. `scope.py` orders it that way; `test_out_of_scope_marketing_deny_final` asserts a denied doc stays denied regardless of its allow-score confidence.

## 5. Deletion-proof ref is reserved, not just referenced

Spec §11's reservation model is subtle: `deletion_proof_ref` must appear in chunk records that are serialized *before* the raw is deleted. The implementation computes the ref deterministically (`proofs/<run_id>/<doc_id>.deletion-proof.json`) and writes it into every record, then materializes the proof file only after deletion. This guarantees no serialized record can point to a proof that was never reserved.

## 6. Findings truncation is a spec-completing safety rule

The spec mandates scanning and ledgering but doesn't explicitly bound what a finding record may contain. Building it made the hazard obvious: a finding that quotes the match turns the failure ledger into a secrets store. The reference impl truncates every finding preview to 8 characters. Recommended for all profiles; encoded in `sensitive.py`.

## 7. Detector identity = ruleset ID + config hash, both

Recording only "Presidio" is insufficient for reproducibility — rules change. Both chunk records and manifests carry `*_ruleset_id` **and** `*_config_hash`. The reference regex detectors compute their config hash over the ruleset dict itself, so a rule edit changes the hash and makes pre-edit records distinguishable. Enterprise profiles must hash the actual Presidio/Gitleaks config files (spec §5.1 already requires this).

## Open items for standard/enterprise builders

- **Chunking `section_path`**: the reference impl emits `/` (flat) since text inputs lack reliable structure. Tika-based profiles should populate real section paths and add chunking conformance tests proving boundary determinism per §9.
- **Redaction mode**: the reference profile only supports `removal_mode: drop` (block on finding). Presidio-based profiles implementing `redact` must run pass-2/pass-3 on the *redacted* text and prove no finding survives.
- **ACL propagation**: reference uses a single sentinel; enterprise must carry real ACL refs from source through to chunk records without widening access.
