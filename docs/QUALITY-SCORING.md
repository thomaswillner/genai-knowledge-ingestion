# Quality Scoring (Deterministic Baseline)

This pack mandates deterministic quality scoring (scoring_rubric_v1) defined in:
- spec/genai-knowledge-ingestion.meta-prompt.txt => QUALITY SCORE (NORMATIVE; DETERMINISTIC)
- quality policy preset: spec/policies/presets/quality.QUALITY_MIN_V1.json => scoring_rubric_v1 params

Conformance is mandatory:
- tests/fixtures/quality_*.txt
- harness must assert EMPTY_TEXT hard fail and good-text pass above min_quality_score
