"""QUALITY CONFORMANCE TEST GATE (spec Appendix A, mandatory)."""

from conftest import load_fixture_doc

from gki_reference.chunking import token_count
from gki_reference.extract import derive_summary
from gki_reference.quality import score_document


def _score(name, quality_policy):
    doc = load_fixture_doc(name)
    tokens = token_count(doc.extracted_text) if doc.extracted_text else 0
    return score_document(
        doc.extracted_text, tokens, doc.title, derive_summary(doc),
        bool(doc.parse_warnings), duplicate_ratio=0.0, missing_metadata_ratio=0.0,
        quality_policy=quality_policy,
    )


def test_quality_good(quality_policy):
    result = _score("quality_good.txt", quality_policy)
    assert result.quality_score >= quality_policy["min_quality_score"]
    assert "EMPTY_TEXT" not in result.quality_flags
    assert result.passed


def test_quality_empty_hard_fail(quality_policy):
    result = _score("quality_empty.txt", quality_policy)
    assert result.quality_score == 0.0
    assert "EMPTY_TEXT" in result.quality_flags
    assert not result.passed
