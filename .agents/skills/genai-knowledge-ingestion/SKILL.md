---
name: genai-knowledge-ingestion
description: >
  v21: fixes labeling determinism (no_match_action + confidence_mode), aligns taxonomy_version with strict chunk schema, and documents HMAC key ordering for deletion proof reservation.
---

# Skill: GENAI Knowledge Ingestion (v21)
- Always emit extensions:{}.
- Labeling is mandatory and deterministic:
  - no_match_action defined (default empty_labels)
  - confidence_mode defined (default rule_binary -> confidence=1.0 for matches)
- taxonomy_version is required in chunk records; output it from labeling policy taxonomy_version.
- If using HMAC-derived deletion_proof_ref reservation IDs: configure identifier_policy.hmac_key_reference before run.
