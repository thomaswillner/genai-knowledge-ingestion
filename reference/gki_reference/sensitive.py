"""Sensitive data verification: 3-pass, fail-closed.

Reference profile detectors are deterministic regex rulesets that stand in
for Presidio (PII) and Gitleaks (secrets) behind the same detector
interface the spec defines. Enterprise deployments swap in the real
services (see docs/PROFILES.md); the enforcement points and fail-closed
semantics are identical.

Detector config hashes are computed over the ruleset definition so chunk
records and manifests can prove exactly which rules scanned them.
"""

import re
from dataclasses import dataclass, field

from .fingerprints import fingerprint

# --- Reference rulesets -----------------------------------------------------

PII_RULESET_ID = "REFERENCE_EU_PII_V1"
PII_RULES = {
    "EMAIL": r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}",
    "PHONE_INTL": r"\+\d{2}[\s\d]{8,15}\d",
    "IBAN": r"\b[A-Z]{2}\d{2}[A-Z0-9]{11,30}\b",
}

SECRETS_RULESET_ID = "REFERENCE_SECRETS_V1"
SECRETS_RULES = {
    "AWS_ACCESS_KEY_ID": r"\bAKIA[0-9A-Z]{16}\b",
    "AWS_SECRET_ACCESS_KEY": r"(?i)aws.{0,30}(secret|key).{0,10}[:=]\s*[A-Za-z0-9/+=]{30,}",
    "PRIVATE_KEY_BLOCK": r"-----BEGIN [A-Z ]*PRIVATE KEY-----",
    "GENERIC_TOKEN_ASSIGNMENT": r"(?i)\b(api[_-]?key|token|secret|password)\b\s*[:=]\s*['\"]?[A-Za-z0-9_\-/+=]{16,}",
}

PII_CONFIG_HASH = fingerprint({"id": PII_RULESET_ID, "rules": PII_RULES})
SECRETS_CONFIG_HASH = fingerprint({"id": SECRETS_RULESET_ID, "rules": SECRETS_RULES})


@dataclass
class Finding:
    detector: str
    rule: str
    match_preview: str  # first 8 chars only — findings must never leak the secret


@dataclass
class ScanResult:
    findings: list = field(default_factory=list)

    @property
    def clean(self) -> bool:
        return not self.findings


def _scan(text: str, ruleset: dict, detector: str) -> list:
    findings = []
    for rule, pattern in sorted(ruleset.items()):
        for m in re.finditer(pattern, text):
            findings.append(Finding(detector, rule, m.group(0)[:8]))
    return findings


def scan_text(text: str) -> ScanResult:
    """One scan invocation = PII ruleset + secrets ruleset over the text."""
    result = ScanResult()
    result.findings.extend(_scan(text, PII_RULES, PII_RULESET_ID))
    result.findings.extend(_scan(text, SECRETS_RULES, SECRETS_RULESET_ID))
    return result


def scan_summary(results: dict) -> dict:
    """results: pass_name -> ScanResult. Summarize without leaking content."""
    return {
        pass_name: {
            "finding_count": len(r.findings),
            "rules_hit": sorted({f"{f.detector}/{f.rule}" for f in r.findings}),
        }
        for pass_name, r in results.items()
    }
