# Architecture

## Pipeline (spec execution contract, 16 steps)

```
                    ┌─ PRE-FLIGHT GATES ────────────────────────────┐
                    │ config nulls? tika up? legal basis? retention? │
                    └───────────────┬───────────────────────────────┘
                                    ▼
  sources ──► RETRIEVE ──► SNAPSHOT+HASH ──► EXTRACT ──► NORMALIZE
 (files,      (allowlist    (sha256 every     (Tika /     (whitespace,
  portals)     only)         byte ingested)    text)       segmentation)
                                    │
                                    ▼
              ┌──── SENSITIVE PASS 1: pre-persist scan ────┐  ✗→ BLOCKED + raw deleted
              ▼                                             │
         SCOPE GATE  ✗→ OUT_OF_SCOPE (deny is final) / BLOCKED (fail-closed)
              ▼
          LABELING  (deterministic rules + label_quality controls)
              ▼
              ┌──── SENSITIVE PASS 2: derived fields ──────┐  ✗→ BLOCKED
              ▼
        QUALITY GATE  ✗→ BLOCKED: data_quality_gate
              ▼
          CHUNKING  (cl100k_base, structure-aware, deterministic)
              ▼
         SERIALIZE  (strict schemas, additionalProperties: false)
              ▼
              ┌──── SENSITIVE PASS 3: post-export scan ────┐  ✗→ output destroyed, BLOCKED
              ▼
           PUBLISH  ──►  RAW DELETION + PROOF  ──►  LEDGERS + MANIFEST
```

Every ✗ path writes a failure-ledger entry with a normative reason code. No path exits silently.

## Reference implementation layout

```
reference/
├── gki_reference/
│   ├── blocked.py        Blocked exception — the only failure channel
│   ├── fingerprints.py   sha256 over canonical JSON; file/text hashing
│   ├── extract.py        text/markdown extraction + deterministic segmentation
│   ├── textscore.py      shared normalize / occurrence-count / weighted-score
│   ├── scope.py          classifier_v1 (spec Appendix A, incl. v18 deny-final fix)
│   ├── labeling.py       rule engine + label_quality (raw filter → weighted rank → cap → primary)
│   ├── quality.py        scoring_rubric_v1
│   ├── chunking.py       cl100k_base token chunking; blocks without tiktoken
│   ├── sensitive.py      3-pass regex detectors behind the spec's detector interface
│   ├── serialize.py      strict-schema validation + JSONL/JSON writers
│   ├── pipeline.py       execution-contract orchestration, ledgers, deletion proofs
│   └── cli.py            gki-reference CLI
└── tests/                conformance suites (see verify.sh)
```

## Design decisions

**Why one shared `textscore.py`?** The spec defines scope classification and labeling with *identical* segmentation, normalization, and counting semantics. One implementation means they cannot drift apart — a conformance bug in one would surface in both suites.

**Why does `Blocked` carry a code, not a message?** Codes are the API. Ledgers, tests, and operators all match on `reason_code`; the human-readable detail is auxiliary. This is what makes failure handling scriptable.

**Why regex detectors instead of a Presidio stub?** A stub that always returns "clean" would make the reference profile a lie. The regex rulesets are real detectors with real config hashes — weaker than Presidio, honest about it (distinct ruleset IDs: `REFERENCE_*`), and they demonstrably catch the planted fixtures.

**Why is the tokenizer non-negotiable?** Chunk boundaries define chunk hashes; chunk hashes define dedup and provenance. A fallback tokenizer would produce different-but-plausible chunks — the worst kind of nondeterminism. `BLOCKED: tokenizer_unavailable` is cheaper than a silent fork in history.

**Why are findings truncated to 8 chars?** The failure ledger is the most-read artifact in the system. If it quoted matches in full, the audit trail would itself become a secrets store.

**Trust boundaries.** Raw staging (`staging/`) is the only place unsanitized bytes rest, and its lifetime ends with either a deletion proof (success) or an immediate delete (any block). Nothing downstream of pass 3 has ever contained a detected finding.
