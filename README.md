# GENAI Knowledge Ingestion (GKI)

**A fail-closed, deterministic, fully auditable pipeline that turns raw technical documents into GenAI-ready markdown/JSONL knowledge — and refuses to produce anything it cannot prove is safe.**

Spec pack + runnable reference implementation. 24 conformance tests, one command.

```bash
./verify.sh                     # run the full conformance suite (24 tests)
```

```bash
cd reference && python3 -m gki_reference.cli \
  --config ../config/reference-config.json \
  --input  ../tests/fixtures/quality_good.txt
# → {"status": "published", "doc_id": "...", "chunks": 1, ...}
```

## Why this exists

Most knowledge-ingestion setups for RAG are optimistic scripts: they parse what they can, index what they parsed, and silently drop or leak the rest. GKI inverts that posture — **every step is a gate, every gate fails closed, and every output carries cryptographic proof of exactly which policies produced it.** See [docs/WHY-THIS-IS-DIFFERENT.md](docs/WHY-THIS-IS-DIFFERENT.md) for the full argument.

## What's in the box

| Layer | Where | What |
|---|---|---|
| Canonical spec | [`spec/genai-knowledge-ingestion.meta-prompt.txt`](spec/genai-knowledge-ingestion.meta-prompt.txt) | Normative pipeline contract, 16 steps, fail-closed gates, deterministic algorithms |
| Strict schemas | [`spec/schemas/`](spec/schemas/) | Chunk record + manifest, `additionalProperties: false` |
| Policy presets | [`spec/policies/`](spec/policies/) | Scope classifier, labeling, quality rubric, chunking, EU GDPR baselines, detector configs |
| **Reference implementation** | [`reference/`](reference/) | Runnable Python implementation of pipeline steps 5–12 + deletion proofs + ledgers |
| Conformance fixtures | [`tests/fixtures/`](tests/fixtures/) | Synthetic inputs with expected outcomes for every gate |
| One-command harness | [`verify.sh`](verify.sh) | Proves the implementation matches the spec |

## Quick start

See [docs/QUICKSTART.md](docs/QUICKSTART.md). TL;DR:

```bash
python3 -m pip install -r reference/requirements.txt   # jsonschema, tiktoken, pytest
./verify.sh
```

## Deployment profiles

The spec is enterprise-grade; you don't need the enterprise to use it. Three profiles ([docs/PROFILES.md](docs/PROFILES.md)):

- **reference** — zero infrastructure. Local text files, regex detectors, runs on a laptop. This repo ships it working.
- **standard** — adds Apache Tika (binary formats) and Gitleaks (real secrets engine).
- **enterprise** — adds Presidio PII services, portal retrieval with legal-basis gates, ACL propagation, GDPR retention machinery.

Same schemas, same gates, same failure codes in all three — only the detector/connector implementations change.

## Documentation

| Doc | Purpose |
|---|---|
| [WHY-THIS-IS-DIFFERENT.md](docs/WHY-THIS-IS-DIFFERENT.md) | What makes this approach special — the positioning argument |
| [QUICKSTART.md](docs/QUICKSTART.md) | Running in 5 minutes |
| [ARCHITECTURE.md](docs/ARCHITECTURE.md) | Pipeline stages, data flow, design decisions |
| [PROFILES.md](docs/PROFILES.md) | reference / standard / enterprise deployment tiers |
| [SCHEMA-GUIDE.md](docs/SCHEMA-GUIDE.md) | Every required field: what, why, what to put when N/A |
| [FAILURE-CODES.md](docs/FAILURE-CODES.md) | Complete BLOCKED reason-code reference |
| [OPERATIONS.md](docs/OPERATIONS.md) | Running, troubleshooting, source connectors, degrade paths |
| [IMPLEMENTATION-NOTES.md](docs/IMPLEMENTATION-NOTES.md) | Spec clarifications surfaced by building the reference impl |
| [PACKAGE-OVERVIEW.md](docs/PACKAGE-OVERVIEW.md) | Original pack overview (build-agent usage) |

## Building the full product

This repo also works as an agent build pack: point Claude Code at [`CLAUDE.md`](CLAUDE.md) or Codex at [`AGENTS.md`](AGENTS.md), fill [`config/starter-config.json`](config/starter-config.json) (nulls block deliberately — see SCHEMA-GUIDE), and the agent builds the standard/enterprise tiers against the same conformance suite that already proves the reference tier.

## License

[PolyForm Noncommercial License 1.0.0](LICENSE.md) — personal and noncommercial use only. Commercial use is not permitted.
