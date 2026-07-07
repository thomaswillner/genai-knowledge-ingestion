# Scope Classifier (Deterministic Baseline)

This pack mandates a deterministic scope classifier (classifier_v1) defined in:
- spec/genai-knowledge-ingestion.meta-prompt.txt => SCOPE CLASSIFIER (NORMATIVE; DETERMINISTIC)
- scope policy preset: spec/policies/presets/scope.CYBERSEC_TECH_ONLY_V1.json => classifier_v1 params

Conformance is mandatory:
- tests/fixtures/scope_*.txt
- harness must assert IN_SCOPE / OUT_OF_SCOPE / BLOCKED behavior matches classifier_v1


v19 correction
- OUT_OF_SCOPE decisions (deny_threshold_met) are not overridden by the confidence threshold; confidence threshold applies only to IN_SCOPE.
