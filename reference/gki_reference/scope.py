"""Scope gate: deterministic classifier_v1, exactly per spec Appendix A.

Decision semantics (v18 defect fix, normative):
- deny_total >= deny_threshold  => OUT_OF_SCOPE, final, never overridden.
- confidence threshold applies ONLY to IN_SCOPE decisions.
"""

from dataclasses import dataclass, field

from .blocked import Blocked
from .textscore import sections, weighted_score


@dataclass
class ScopeResult:
    decision: str  # IN_SCOPE | OUT_OF_SCOPE | BLOCKED
    scope_class: "str | None"
    scope_confidence: float
    audit: dict = field(default_factory=dict)


def classify(title_text: str, headings_text: str, body_text: str, scope_policy: dict) -> ScopeResult:
    clf = scope_policy.get("classifier_v1")
    if not clf:
        raise Blocked("scope_classifier_config_missing", "scope_policy.classifier_v1 is mandatory (v16+)")

    weights = clf["section_weighting"]
    secs = sections(title_text, headings_text, body_text)

    allow_scores = {
        cls: weighted_score(terms, secs, weights)[0]
        for cls, terms in clf["allow_terms"].items()
    }
    deny_scores = {
        cls: weighted_score(terms, secs, weights)[0]
        for cls, terms in clf["deny_terms"].items()
    }

    allow_total = max(allow_scores.values(), default=0)
    deny_total = max(deny_scores.values(), default=0)

    # argmax with deterministic tie-break: score desc, class lexicographic asc
    scope_class = None
    if allow_scores:
        scope_class = sorted(allow_scores.items(), key=lambda kv: (-kv[1], kv[0]))[0][0]
    deny_top_class = None
    if deny_scores and deny_total > 0:
        deny_top_class = sorted(deny_scores.items(), key=lambda kv: (-kv[1], kv[0]))[0][0]

    confidence = min(1.0, max(0.0, (allow_total - deny_total) / clf["confidence_divisor"]))

    audit = {
        "allow_top_class": scope_class,
        "allow_top_score": allow_total,
        "deny_top_class": deny_top_class,
        "deny_top_score": deny_total,
        "classifier_version": "classifier_v1",
    }

    if deny_total >= clf["deny_threshold"]:
        audit["decision"] = "OUT_OF_SCOPE"
        return ScopeResult("OUT_OF_SCOPE", None, confidence, audit)

    if allow_total >= clf["allow_threshold"] and (allow_total - deny_total) >= clf["allow_margin"]:
        if confidence < scope_policy["scope_confidence_threshold"]:
            audit["decision"] = "BLOCKED"
            return ScopeResult("BLOCKED", scope_class, confidence, audit)
        audit["decision"] = "IN_SCOPE"
        return ScopeResult("IN_SCOPE", scope_class, confidence, audit)

    audit["decision"] = "BLOCKED"
    return ScopeResult("BLOCKED", scope_class, confidence, audit)
