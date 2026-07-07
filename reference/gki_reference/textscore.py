"""Shared deterministic text scoring primitives (spec Appendix A).

Used by both the scope classifier and the labeling engine, which the
spec defines with identical segmentation, normalization, and
occurrence-counting semantics.
"""


def normalize(text: str) -> str:
    """Lowercase + collapse all whitespace runs to single spaces (spec A.2)."""
    return " ".join(text.lower().split())


def count_occurrences(term: str, section_text_normalized: str) -> int:
    """Non-overlapping substring occurrences of a normalized term (spec A.3)."""
    term = normalize(term)
    if not term:
        return 0
    return section_text_normalized.count(term)


def sections(title_text: str, headings_text: str, body_text: str) -> dict:
    return {
        "title": normalize(title_text or ""),
        "headings": normalize(headings_text or ""),
        "body": normalize(body_text or ""),
    }


def weighted_score(term_list, secs: dict, weights: dict) -> tuple:
    """Return (weighted_score, raw_total_occurrences) for a term list."""
    weighted = 0
    raw = 0
    for term in term_list:
        for name, text in secs.items():
            occ = count_occurrences(term, text)
            raw += occ
            weighted += occ * int(weights.get(name, 1))
    return weighted, raw
