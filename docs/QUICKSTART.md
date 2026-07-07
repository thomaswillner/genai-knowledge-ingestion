# Quickstart (5 minutes, zero infrastructure)

## 1. Install dependencies

```bash
python3 -m pip install -r reference/requirements.txt
```

Three packages: `jsonschema` (strict schema gates), `tiktoken` (the spec-mandated cl100k_base tokenizer), `pytest` (harness).

## 2. Prove the implementation conforms to the spec

```bash
./verify.sh
# 24 passed
```

This runs every mandatory verification gate from spec §13: schema validation, scope/labeling/quality conformance suites, sensitive-data gates, chunking determinism, and a full end-to-end run.

## 3. Ingest your first document

```bash
cd reference
python3 -m gki_reference.cli \
  --config ../config/reference-config.json \
  --input  ../tests/fixtures/quality_good.txt
```

Expected output:

```json
{"status": "published", "doc_id": "doc-…", "chunks": 1,
 "chunks_path": "reference-output/sanitized/doc-….chunks.jsonl",
 "manifest_path": "reference-output/sanitized/doc-….manifest.json"}
```

Look inside `reference-output/`:

```
sanitized/   doc-….chunks.jsonl      # schema-valid chunk records
             doc-….manifest.json     # document manifest, all fingerprints
proofs/      run-…/doc-….deletion-proof.json   # raw deletion proof
ledgers/     success.jsonl           # what published, when, with what score
             failure.jsonl           # what blocked, and the exact reason code
```

## 4. Watch it fail closed (the point of the whole system)

```bash
python3 -m gki_reference.cli \
  --config ../config/reference-config.json \
  --input  ../tests/fixtures/synthetic_iam_runbook.txt \
           ../tests/fixtures/scope_out_of_scope_marketing.txt
```

```json
{"status": "blocked", "input": "…synthetic_iam_runbook.txt", "reason_code": "sensitive_data_violation"}
{"status": "blocked", "input": "…scope_out_of_scope_marketing.txt", "reason_code": "scope_out_of_scope"}
```

The first fixture contains synthetic PII + AWS keys — caught at pass 1, raw copy deleted, findings ledgered with 8-char previews only. The second is a marketing brochure — denylisted, final, not overridable. Look up any code in [FAILURE-CODES.md](FAILURE-CODES.md).

## 5. Ingest your own files

Point `--input` at any UTF-8 text/markdown file. The reference profile handles text only (that's the deal that buys zero infrastructure); for PDF/DOCX you need the standard profile with Tika — see [PROFILES.md](PROFILES.md).

To change dataset identity, ACL sentinel, or policies, copy `config/reference-config.json` and edit — every key is documented in [SCHEMA-GUIDE.md](SCHEMA-GUIDE.md). Any required key set to `null` blocks with `config_invalid` instead of guessing. That's by design.
