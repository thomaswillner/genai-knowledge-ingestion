# Canonical spec lives as a versioned repo artifact, not in agent prompts

`CLAUDE.md` and `AGENTS.md` are deliberately near-empty entry points; the only live prompt is `prompt-1-builder.txt`, and all normative behavior lives in `spec/genai-knowledge-ingestion.meta-prompt.txt` (Canonical v1.0) plus versioned schemas and policies. This replaced the earlier additive "vN clauses remain" prompt chain (retired per `spec/governance/SPEC-CONSOLIDATION.md`, preserved under `spec/history/patches/v0.x/`), whose stacked deltas drifted from what agents actually executed and left no single authoritative copy to fingerprint or diff.

## Consequences

Re-printing spec content in chat or prompts is forbidden (reference by file path + heading only); all future changes go to the canonical spec with deltas in `spec/CHANGELOG.md`. Do not "fix" the thin `CLAUDE.md`/`AGENTS.md` by inlining instructions — the emptiness is the mechanism that keeps exactly one authoritative copy.
