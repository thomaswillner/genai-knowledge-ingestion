# Why This Is Different

Every RAG tutorial ships the same ingestion script: read files, split into chunks, embed, index. It works in the demo. Then it meets reality: a PDF with an employee's IBAN in a footer, an AWS key pasted into a runbook, a marketing deck that poisons retrieval quality, a re-index six months later that nobody can reproduce because the chunking code changed and nothing recorded which version made which chunk.

GKI is built on one conviction: **knowledge ingestion is a compliance problem wearing a data-engineering costume.** Treat it that way and everything else follows.

## The four properties

### 1. Fail-closed, not best-effort

Every step is a gate; every gate that cannot meet its contract stops the pipeline with a **named reason code** — `BLOCKED: sensitive_data_violation`, `BLOCKED: scope_gate_low_confidence`, `BLOCKED: tokenizer_unavailable`. There is no partial silent success, no "skipped 3 files (see logs)". A document either becomes a fully-proven artifact or it becomes a failure-ledger entry with an exact machine-readable cause.

The subtle rule most systems get wrong: **deny always beats allow.** An out-of-scope decision triggered by the denylist can never be overridden by a confidence score. Confidence thresholds apply only to letting things *in*, never to letting things *past* a rejection.

### 2. Deterministic to the token

Same input + same policy = byte-identical output, forever. No probabilistic classifier decides what enters your knowledge base — the scope gate and labeling engine are rule-based, with tie-breaks specified down to lexicographic order. Even the tokenizer is pinned (cl100k_base) and its absence blocks rather than falling back. This is what makes an ingest **reproducible in an audit** and **diffable across time**: re-run last year's ingest and get last year's chunks, exactly.

### 3. Provenance you can cryptographically verify

Every chunk record carries the SHA-256 fingerprint of *each policy that shaped it* — scope, labeling, quality, chunking, and both detector configs — plus the source object hash and a deletion-proof reference. A chunk is never just text: it's text plus a complete, hash-verified account of how it came to exist and why it was allowed to. When a policy changes, you can identify every artifact produced under the old policy with one query.

### 4. Sensitive data is hunted three times, then the raw is destroyed with proof

PII and secrets scanning runs at three enforcement points: before anything persists, again on derived fields (titles, summaries, labels — where sensitive data loves to reappear), and once more on the final serialized output. Only after the sanitized artifact passes all three does the pipeline delete the raw staging copy — and it materializes a **deletion proof** (path, hash, timestamp) under a reference that was reserved *before* serialization, so the proof chain has no gap. Findings themselves are truncated to 8 characters: the audit trail can never become the leak.

## The proof discipline

A spec that has never been executed is a hypothesis. This repo ships:

- a **reference implementation** (steps 5–12 + deletion proofs + ledgers) that runs with zero infrastructure,
- **conformance fixtures with expected outcomes for every gate** — including engineered ties, cap overflows, no-match paths, and an intentionally ambiguous document that must fail closed,
- a **one-command harness** (`./verify.sh`) that proves implementation and spec agree — 24 tests.

The fixtures don't test the code; they test **any** implementation. Build the enterprise tier in Java behind Tika and Presidio, run the same fixtures, and you know it conforms. That's the difference between "documentation" and a **specification with teeth**.

## Compared to the alternatives

| | Naive RAG scripts | Enterprise ETL/governance suites | **GKI** |
|---|---|---|---|
| Failure mode | Silent skip/leak | Config-buried, vendor-locked | Named BLOCKED code, fail-closed |
| Reproducibility | None (code drifts) | Partial | Deterministic to the token |
| Provenance | File path, maybe | Lineage UI | Per-artifact policy fingerprints |
| PII/secrets | Afterthought | Separate product | 3-pass, fail-closed, in-pipeline |
| Proof it works | Demo | Sales deck | Runnable conformance suite in-repo |
| Infra floor | None | Massive | **Zero** (reference profile) → scales up |

## What this is not

- Not an agent-memory wiki: GKI produces *retrieval artifacts* (chunk records) for RAG/index workloads, not a curated knowledge graph. The two compose — GKI-grade gates make excellent front doors for any knowledge store.
- Not a crawler: retrieval is allowlist-only and deterministic by design. If you want "ingest the whole internet," this is the wrong tool on purpose.
