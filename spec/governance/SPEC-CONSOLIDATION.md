# Spec Maintenance and Consolidation (Operational Governance)

Status
- Consolidation has been completed.
- Canonical specification is:
  - /spec/genai-knowledge-ingestion.meta-prompt.txt (v1.0)
- Historical additive artifacts are preserved under:
  - /spec/history/patches/v0.x/

Change discipline (mandatory)
- All future changes must be applied to the canonical spec.
- If changes are developed as patches, they must be merged into the canonical spec before release.
- Maintain /spec/CHANGELOG.md with versioned, minimal deltas.

Non-goals
- This governance rule does not change runtime behavior. It changes maintenance discipline only.
