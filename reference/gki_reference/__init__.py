"""GKI Reference Implementation.

Minimal, dependency-light implementation of the canonical specification
(spec/genai-knowledge-ingestion.meta-prompt.txt) covering pipeline steps
5-12 plus raw deletion proofs and ledgers, in the "reference" profile
(local files, regex detectors, no Tika/Presidio/Playwright).

Purpose: prove the spec is buildable, executable, and that its
conformance fixtures pass. See docs/PROFILES.md for what this profile
does and does not enforce.
"""

__version__ = "0.1.0"
SCHEMA_VERSION = "gki-1.0"
