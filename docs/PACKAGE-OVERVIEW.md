## What this package builds and what it’s used for

This package is a **build pack** (prompts + spec + strict schemas + policies + starter config) that guides a coding agent (Claude Code / OpenAI Codex / Cursor) to build a production-grade tool named:

**GENAI Knowledge Ingestion**

**Purpose:** deterministically ingest **technical cybersecurity knowledge** (architecture docs, runbooks, code, processes, best practices) from controlled sources (vendor partner portals, SharePoint/Drives, manual file imports), transform it into **GenAI-ready artifacts** (chunked JSONL + manifest), enforce **GDPR/PII + secrets removal**, preserve **ACLs**, produce **auditable ledgers**, and **delete raw artifacts** with **deletion proof**.

It is intended for enterprise use cases like:
- building a governed internal RAG/knowledge base for IAM / PAM / Zero Trust / SIEM delivery patterns
- indexing vendor portal documentation into a compliant GenAI knowledge store
- creating a repeatable ingestion pipeline for cybersecurity reference architectures and runbooks

This package **does not contain the final product code**. It contains the operational instructions and compliance gates that enable an agent/human team to build it correctly.

---

## What’s inside the package (logical structure)

- **Prompt 1 (Builder Prompt):** the agent execution contract (phases, block conditions, “strict schema gate”, artifact-first output discipline).
- **Prompt 2 (Spec Pack):** the product specification (deterministic pipeline, portal/MFA strategy, compliance gates, deletion-proof model).
- **Strict JSON Schemas:** enforce compliance as a hard gate (`additionalProperties=false`, `extensions` required).
- **Policies + Presets:** EU baseline policies, labeling baseline, detector configuration (Presidio + Gitleaks).
- **Starter config:** a complete config skeleton with `null` for environment-specific values (so missing inputs are explicit and BLOCK when required).
- **MCP + Skills (optional):** tooling integration files for Codex/Claude/Cursor workflows.

---

## Who can build this and what skills are required

Minimum roles/skills:
1. **Senior Backend/Platform Engineer**
   - ingestion pipeline architecture, idempotency, checkpoints, hashing, schema enforcement, logging/ledgers
2. **Security/Privacy Engineer**
   - GDPR/retention, PII + secrets gates, ACL enforcement, auditability, threat modeling
3. **Automation Engineer (Portals)**
   - Playwright automation, deterministic discovery, throttling/retry, snapshotting, MFA handoff workflow
4. **DevOps/SRE**
   - containerization/K8s, secrets management, CI/CD, observability, hardened deployment

Optional:
- **Frontend engineer** (if you want a polished UI for config editing + progress + resume dashboards)

---

## How you use this package (build flow)

1) **Unpack into a repo**  
2) **Pick the build agent**
- Claude Code → uses `CLAUDE.md`
- OpenAI Codex → uses `AGENTS.md`
- Cursor → use `prompt-1-builder.txt` as project rule(s)

3) **Fill the starter configuration**
- `config/starter-config.json` contains required keys and deliberately leaves environment fields as `null`
- you must set the hard-blocker inputs (storage targets, portal URLs/legal basis, detector endpoints, secret refs)

4) **Run the agent**
- agent follows Prompt 1, reads Prompt 2 + schemas/policies, scaffolds and implements the tool, generates tests/runbook

5) **VERIFY gate**
- strict schema validation (chunks/manifests), preflight gates, detectors, resume/dedupe, deletion proof, ledgers

---

## What the built tool does at runtime (runtime flow)

1) **Preflight gates**
- Tika health, config validation, legal basis for portals, retention exception gate (EU + raw retention > 0)

2) **Deterministic retrieval**
- Playwright-only portal retrieval (allowlist gated), snapshot hashing, offline extraction

3) **Parsing**
- primary: Apache Tika Server (minimal parsing stack)

4) **Sensitive-data gates (PII + secrets)**
- Presidio (PII) + Gitleaks (secrets)
- enforced pre-persist, derived-fields, post-export

5) **Scope gate**
- persist only technical cybersecurity content classes

6) **Mandatory labeling**
- deterministic rule-based baseline; no-match behavior defined; emits `taxonomy_version`

7) **Chunking + output packaging**
- GenAI-ready **JSONL chunks + manifest**, validated by strict schemas

8) **Publish**
- write sanitized outputs to destinations + index

9) **Raw deletion + deletion proof**
- deletion proof ref is reserved early; proof materialized after deletion

10) **Ledgers + catalog**
- success/failure ledgers, catalog entries, audit metadata

---

## Required software / systems / dependencies

### Core dependencies (product runtime)
- **Apache Tika Server** (mandatory parsing service)
- **Playwright + Chromium runtime** (vendor portal retrieval)
- **Presidio services** (Analyzer + Anonymizer) for PII detection/redaction
- **Gitleaks** (CLI or container) for secrets detection
- **Storage targets** for:
  - job state / checkpoints
  - sanitized artifact store (JSONL + manifest)
  - audit logs + success/failure ledgers
  - catalog + quality reports
- **Index / vector store** (your choice, but required by the spec as a target)

### Operational requirements (enterprise)
- secrets management (to supply `hmac_key_reference`, portal creds, API tokens by reference)
- network controls (domain allowlists, egress controls)
- centralized logging/monitoring (PII-free logs)

### Optional tooling integrations
- **MCP config**: `.mcp.json` and optional `.mcp.optional.gkiDevTools.json`
- **Codex MCP config**: `.codex/config.toml`
- **Codex Skill**: `.agents/skills/.../SKILL.md`

---

## What must be configured (or it will BLOCK)
- storage targets (object store, state store, ledgers, audit, catalog, quality reports)
- vendor portal profiles (login/base URLs, allowlists, legal basis record IDs)
- MFA handoff storage (session artifact store + TTL + encryption required)
- Presidio endpoints (analyzer/anonymizer URLs)
- Gitleaks execution (native path or docker image)
- `identifier_policy.hmac_key_reference` if HMAC-based IDs are used (e.g., for deletion-proof ref reservation)

---

## Output you get from the built tool
- schema-valid **JSONL chunk records** + **manifest** per document
- policy fingerprints + detector config hashes embedded for auditability
- success/failure ledgers (with destinations + reasons)
- deletion proof objects (post-delete)
- crash-resumable runs with deterministic checkpoints


---

## Accelerator assets included
- Dependency bootstrap: docs/DEPENDENCY-BOOTSTRAP.md + infra/docker-compose.dependencies.yml
- Test fixtures: tests/fixtures/
- Labeling noise control: docs/LABELING-QUALITY.md + labeling.LABELING_MIN_V2.json


---

## Additional conformance gates (v16)
- Scope classifier deterministic algorithm + conformance fixtures (tests/fixtures/scope_*.txt)
- Quality scoring deterministic rubric + conformance fixtures (tests/fixtures/quality_*.txt)
- Labeling suite extension fixtures (tests/fixtures/label_*.txt)


Pack version: v21
