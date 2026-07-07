# Operations

Running, troubleshooting, and degrade paths. For the reference profile this is a laptop; for standard/enterprise, substitute your service topology but keep the same gate discipline.

## Running

```bash
# full conformance suite (spec §13 verification gates)
./verify.sh

# ingest one or more files
cd reference
python3 -m gki_reference.cli --config ../config/reference-config.json --input FILE [FILE...]
```

Exit codes: `0` all published · `1` at least one input blocked · `2` config/dependency failure (pipeline never started).

## Reading the output

```
reference-output/
├── sanitized/    <doc_id>.chunks.jsonl     published chunk records (schema-valid)
│                 <doc_id>.manifest.json    per-document manifest
├── proofs/       <run_id>/<doc_id>.deletion-proof.json
├── ledgers/      success.jsonl             one line per published doc
│                 failure.jsonl             one line per block, with reason_code
└── staging/      (transient — empty between runs; holds raw only mid-pipeline)
```

**Operate from the ledgers.** `success.jsonl` and `failure.jsonl` are the source of truth for what happened. `jq -r .reason_code failure.jsonl | sort | uniq -c` tells you your block distribution at a glance.

## Troubleshooting by reason code

Look up any code in [FAILURE-CODES.md](FAILURE-CODES.md). Common ones:

| Symptom | Code | Fix |
|---|---|---|
| Pipeline won't start | `config_invalid` | A required key is null. Message names it. Fill it — don't blank it |
| Every doc blocks pre-scan | `sensitive_data_violation` | Working as designed if inputs contain PII/secrets. Check `failure.jsonl` scan summary (rules hit, counts — never the values) |
| Legit doc rejected | `scope_out_of_scope` | Denylist matched. Inspect `extensions.scope` audit in the ledger detail; tune deny terms in the scope policy if a term is over-broad |
| Legit doc blocked, not denied | `scope_gate_low_confidence` | Neither allow-threshold nor margin met. The doc is genuinely ambiguous — add signal or accept the fail-closed |
| Can't run at all | `tokenizer_unavailable` | `pip install tiktoken`. There is no fallback by design |

## Degrade paths (explicit, never silent)

The system never silently skips. When a capability is unavailable, it degrades to a **narrower but still-safe** behavior and says so:

- **Tika down (standard/enterprise)** → `tika_unavailable` for binary formats. Text/markdown still ingests via the reference path. You do not silently skip PDFs — you get a blocked entry per PDF.
- **Portal broken (enterprise)** → deterministic discovery fails loudly (`domain_not_allowed` / `portal_rate_limited`). Sanctioned fallback: export the docs manually and ingest as local files (reference behavior). Portal fragility never becomes silent data loss.
- **Presidio down (enterprise)** → `presidio_endpoint_missing`. You may NOT fall back to a weaker detector silently; either fix Presidio or explicitly switch the profile to regex detectors (which changes the recorded `primary_detector_ruleset_id`, so the downgrade is auditable in every record).

## Source connectors (standard/enterprise)

The reference profile's source is "local files you point `--input` at". Higher profiles add connectors, all bound by the same rules:

1. **Allowlist-only.** Retrieval touches only domains in `web_portal_policy.domain_allowlist`. No connector may crawl.
2. **Snapshot-hash everything** on retrieval (URL, HTTP status, timestamp, sha256) into the audit ledger before extraction.
3. **Offline extraction.** Parse the downloaded artifact, never live browser DOM.
4. **Legal basis + retention gates** fire before a single byte is retrieved from a vendor portal in EU jurisdiction.

## Re-ingest / reproducibility

Because the pipeline is deterministic and every artifact carries its config+policy fingerprints, re-running the same inputs with the same config produces byte-identical chunk records. To reproduce a historical dataset: check out the config version named in its manifest's `run_stamps.config_version`, re-run, compare `content_hash` lists. Divergence means something non-deterministic crept in — that's a bug, and the hashes will find it.
