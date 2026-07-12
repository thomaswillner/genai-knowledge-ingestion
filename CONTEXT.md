# GenAI Knowledge Ingestion (GKI)

A fail-closed, deterministic pipeline that turns technical cybersecurity documents from controlled sources into schema-valid, auditable GenAI-ready knowledge artifacts — and refuses to publish anything it cannot prove is safe.

## Language

**Canonical Specification**:
The single versioned source of truth for product behavior; every normative requirement lives in it, and nowhere else.
_Avoid_: meta-prompt, spec pack, requirements doc

**Builder Prompt**:
The only live instruction given to a coding agent building the product; an entry point that binds the agent to the Canonical Specification instead of restating it.
_Avoid_: system prompt, build instructions

**Profile**:
A deployment tier (reference, standard, enterprise) that swaps detector and connector implementations while keeping schemas, gates, and reason codes identical.
_Avoid_: tier, edition, mode

**Gate**:
A fail-closed enforcement point in the pipeline; it either passes or halts with a Reason Code — there is no partial or silent success.
_Avoid_: check, validation step, filter

**Reason Code**:
The stable machine-readable identifier carried by every BLOCKED gate failure; ledgers, tests, and operators match on codes, not messages.
_Avoid_: error message, error code, exception type

**Preset**:
A versioned, identifiable policy artifact resolved by ID at run time; the unit in which policy changes ship.
_Avoid_: default config, policy template

**Policy Fingerprint**:
The cryptographic identity of the exact policy that shaped an output, carried in that output so every artifact produced under a since-changed policy remains findable.
_Avoid_: policy hash, checksum, policy version

**Detector**:
A sensitive-data engine (PII or secrets) with a versioned ruleset whose configuration identity is recorded in every output it cleared.
_Avoid_: scanner, filter

**Sensitive Pass**:
One of the three mandatory sensitive-data enforcement points (pre-persist, derived-fields, post-export); an unremediated finding at any pass blocks the run.
_Avoid_: PII scan, redaction step

**Chunk Record**:
The atomic published artifact: one strictly schema-valid record per chunk, carrying content, provenance, Policy Fingerprints, and gate outcomes so consumers never re-derive them.
_Avoid_: chunk metadata, embedding record, JSONL row

**Manifest**:
The document-level audit entry point: one per document, twinning the Chunk Record's provenance and fingerprints plus counts, scan summaries, and deletion-proof references.
_Avoid_: index entry, document summary

**Sentinel**:
An explicit, greppable value carried by a required field that does not apply in a given deployment; never blank and never an invented plausible value.
_Avoid_: placeholder, default value, N/A

**Deletion Proof**:
The auditable object attesting that a document's raw artifacts were destroyed; its reference exists in published outputs before serialization, the proof object itself only after deletion executes.
_Avoid_: deletion log, cleanup record

**Ledger**:
An append-only record of run outcomes — a success ledger for published objects and a failure ledger keyed by Reason Code; the primary artifact operators read.
_Avoid_: log, run history

**Conformance Suite**:
The set of fixture-driven tests that prove an implementation matches the Canonical Specification's normative algorithms; passing it is a condition of DONE, and its absence is itself a blocking failure.
_Avoid_: unit tests, regression tests, test coverage
