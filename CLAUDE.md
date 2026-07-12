# Entry Point

Use these files as entry points only. Do not inline large prompts here.

Authoritative build instruction:
- prompt-1-builder.txt

Authoritative product specification:
- spec/genai-knowledge-ingestion.meta-prompt.txt (Canonical Specification v1.0)

Hard rule:
- Do not re-print spec content in chat output. Reference by file path and section heading only.

## Agent skills

Per-repo config for the Matt Pocock engineering skills (`to-tickets`, `triage`, `to-spec`, `qa`, `improve-codebase-architecture`, `diagnosing-bugs`, `tdd`, …).

### Issue tracker

Issues/PRDs live as **GitHub issues** in `thomaswillner/genai-knowledge-ingestion` (via the `gh` CLI). External PRs are **not** a triage surface (solo-maintained). See `docs/agents/issue-tracker.md`.

### Triage labels

Default label vocabulary (`needs-triage`, `needs-info`, `ready-for-agent`, `ready-for-human`, `wontfix`). See `docs/agents/triage-labels.md`.

### Domain docs

Single-context layout — `CONTEXT.md` + `docs/adr/` at the repo root (created lazily by `/domain-modeling`). See `docs/agents/domain.md`.
