"""Labeling engine: rule-based baseline + label_quality controls.

Implements LABELING QUALITY CONTROLS from spec Appendix A exactly:
raw-occurrence filter (unweighted) -> weighted scoring -> selection with
deterministic tie-break (score desc, label lexicographic asc) -> primary
label per type -> optional emission to extensions.<key>.
"""

from dataclasses import dataclass, field

from .blocked import Blocked
from .textscore import sections, weighted_score


@dataclass
class LabelingResult:
    labels: list
    label_confidence: "float | None"
    taxonomy_version: str
    extensions: dict = field(default_factory=dict)


def label(title_text: str, headings_text: str, body_text: str, labeling_policy: dict) -> LabelingResult:
    if "no_match_action" not in labeling_policy:
        raise Blocked("labeling_no_match_undefined")
    if "confidence_mode" not in labeling_policy:
        raise Blocked("labeling_confidence_mode_missing")

    lq = labeling_policy.get("label_quality", {})
    weights = lq.get("section_weighting", {"title": 1, "headings": 1, "body": 1})
    min_occ = int(lq.get("min_occurrences", 1))
    max_per_type = lq.get("max_labels_per_type")
    dedupe = bool(lq.get("dedupe", False))

    secs = sections(title_text, headings_text, body_text)

    emitted = []
    primary_labels = {}
    label_scores = {}

    for label_type, rules in labeling_policy.get("rules", {}).items():
        candidates = {}  # label -> (score, raw)
        for rule in rules:
            score, raw = weighted_score(rule["match_any"], secs, weights)
            lbl = rule["label"]
            if lbl in candidates:
                prev_score, prev_raw = candidates[lbl]
                candidates[lbl] = (prev_score + score, prev_raw + raw)
            else:
                candidates[lbl] = (score, raw)

        # Raw occurrence filter (mandatory, unweighted) before weighted ranking
        passed = {l: s for l, (s, raw) in candidates.items() if raw >= min_occ}
        ranked = sorted(passed.items(), key=lambda kv: (-kv[1], kv[0]))
        if max_per_type is not None:
            ranked = ranked[: int(max_per_type)]

        if ranked:
            primary_labels[label_type] = ranked[0][0]
            label_scores[label_type] = {l: s for l, s in ranked}
            for l, _ in ranked:
                if not dedupe or l not in emitted:
                    emitted.append(l)

    confidence_mode = labeling_policy["confidence_mode"]
    if confidence_mode == "rule_binary":
        label_confidence = 1.0 if emitted else None
    else:
        raise Blocked("labeling_confidence_mode_missing",
                      f"unsupported confidence_mode for reference profile: {confidence_mode}")

    extensions = {}
    if lq.get("emit_primary_labels_to_extensions") and primary_labels:
        key = lq.get("extensions_key", "labeling")
        extensions[key] = {"primary_labels": primary_labels, "label_scores": label_scores}

    return LabelingResult(
        labels=emitted,
        label_confidence=label_confidence,
        taxonomy_version=str(labeling_policy.get("taxonomy_version", "")),
        extensions=extensions,
    )
