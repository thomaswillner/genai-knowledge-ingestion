"""Quality gate: deterministic scoring_rubric_v1 per spec Appendix A."""

from dataclasses import dataclass, field

from .blocked import Blocked


@dataclass
class QualityResult:
    quality_score: float
    quality_flags: list = field(default_factory=list)
    passed: bool = True


def score_document(
    extracted_text: str,
    token_count: int,
    title: "str | None",
    summary: "str | None",
    parse_warnings_present: bool,
    duplicate_ratio: float,
    missing_metadata_ratio: float,
    quality_policy: dict,
) -> QualityResult:
    rubric = quality_policy.get("scoring_rubric_v1")
    if not rubric:
        raise Blocked("quality_rubric_config_missing", "quality_policy.scoring_rubric_v1 is mandatory (v16+)")

    flags = []
    score = 1.0

    normalized_len = len(" ".join(extracted_text.split()))
    if normalized_len == 0:
        return QualityResult(0.0, ["EMPTY_TEXT"], passed=False)

    if token_count < rubric["min_tokens"]:
        score -= rubric["p_too_short"]
        flags.append("TOO_SHORT")
    if not title:
        score -= rubric["p_missing_title"]
        flags.append("MISSING_TITLE")
    if not summary:
        score -= rubric["p_missing_summary"]
        flags.append("MISSING_SUMMARY")
    if parse_warnings_present:
        score -= rubric["p_parse_warning"]
        flags.append("PARSE_WARNING")
    if duplicate_ratio > quality_policy["max_duplicate_ratio"]:
        score -= rubric["p_duplicate_ratio"]
        flags.append("DUPLICATE_RATIO_HIGH")
    if missing_metadata_ratio > quality_policy["max_missing_metadata_ratio"]:
        score -= rubric["p_missing_metadata_ratio"]
        flags.append("MISSING_METADATA_HIGH")

    score = min(1.0, max(0.0, score))
    passed = score >= quality_policy["min_quality_score"]
    return QualityResult(score, flags, passed)
