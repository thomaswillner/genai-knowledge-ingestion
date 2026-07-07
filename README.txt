GENAI Knowledge Ingestion — Prompt Pack v1.0

Delta vs v1.0 (per Claude findings):
1) taxonomy_version schema gap fixed
- taxonomy_version added to strict chunk schema (required string).
- labeling preset already includes taxonomy_version; now output can emit it top-level without schema failure.

2) No-match labeling behavior defined
- LABELING_MIN_V1 now defines no_match_action="empty_labels".
- confidence_mode="rule_binary": matched labels => label_confidence=1.0; no match => labels=[], label_confidence=null.

3) Label confidence threshold semantics clarified
- label_confidence_threshold set to 0.5 (safe for future model_probability mode; no impact for rule_binary where confidence=1.0 on matches).

4) Deletion proof reservation HMAC ordering note added
- If using HMAC-derived deletion_proof_ref reservation IDs, identifier_policy.hmac_key_reference must be configured before reservation step.

Schemas remain strict (additionalProperties=false; extensions required).

Governance:
- Post-first-run spec consolidation rule: spec/governance/SPEC-CONSOLIDATION.md

Package documentation:
- Package overview: docs/PACKAGE-OVERVIEW.md

Accelerators:
- Dependency bootstrap: infra/docker-compose.dependencies.yml (see docs/DEPENDENCY-BOOTSTRAP.md)
- Test fixtures: tests/fixtures/
- Labeling noise control: docs/LABELING-QUALITY.md (preset LABELING_MIN_V2)

Verification:
- Labeling algorithm conformance requirement: docs/VERIFICATION-NOTE-LABELING.md

Conformance:
- Scope conformance fixtures: tests/fixtures/scope_*.txt
- Quality conformance fixtures: tests/fixtures/quality_*.txt
- Labeling suite extension fixtures: tests/fixtures/label_*.txt

Docs:
- Scope classifier: docs/SCOPE-CLASSIFIER.md
- Quality scoring: docs/QUALITY-SCORING.md


Pack version: v21
Canonical spec: spec/genai-knowledge-ingestion.meta-prompt.txt (v1.0.2)

---

## License

Licensed under the [PolyForm Noncommercial License 1.0.0](LICENSE.md) — personal and noncommercial use only. Commercial use is not permitted.
