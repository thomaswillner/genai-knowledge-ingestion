"""LABELING CONFORMANCE TEST GATE + EXTENSION (spec Appendix A, mandatory)."""

from conftest import load_fixture_doc

from gki_reference.labeling import label


def _label(name, labeling_policy):
    doc = load_fixture_doc(name)
    return _label_doc(doc, labeling_policy)


def _label_doc(doc, labeling_policy):
    return label(doc.title or "", " ".join(doc.headings), doc.extracted_text, labeling_policy)


def test_base_case_synthetic_iam_runbook(labeling_policy):
    """Minimum required conformance case from spec Appendix A."""
    result = _label("synthetic_iam_runbook.txt", labeling_policy)
    assert "IAM" in result.labels
    assert result.extensions["labeling"]["primary_labels"]["domain_tags"] == "IAM"
    assert result.label_confidence == 1.0  # rule_binary, labels non-empty


def test_no_match_path(labeling_policy):
    result = _label("label_no_match.txt", labeling_policy)
    assert result.labels == []
    assert result.label_confidence is None  # no_match_action=empty_labels


def test_cap_path_many_domains(labeling_policy):
    result = _label("label_cap_many_domains.txt", labeling_policy)
    domain_scores = result.extensions["labeling"]["label_scores"]["domain_tags"]
    max_per_type = labeling_policy["label_quality"]["max_labels_per_type"]
    assert len(domain_scores) == max_per_type
    # deterministic primary emitted
    assert "domain_tags" in result.extensions["labeling"]["primary_labels"]


def test_tie_break_lexicographic(labeling_policy):
    result = _label("label_tie_break.txt", labeling_policy)
    scores = result.extensions["labeling"]["label_scores"]["domain_tags"]
    assert scores.get("IAM") == scores.get("PAM"), "fixture must produce a tie"
    assert result.extensions["labeling"]["primary_labels"]["domain_tags"] == "IAM"


def test_min_occurrences_raw_filter(labeling_policy):
    """Raw (unweighted) filter: a single title-only hit scores high weighted
    but must be dropped when raw occurrences < min_occurrences."""
    from gki_reference.extract import extract_text_document
    doc = extract_text_document("TITLE: SIEM\n\nNothing else relevant here.")
    result = _label_doc(doc, labeling_policy)
    assert "SIEM" not in result.labels  # raw=1 < min_occurrences=2 despite weighted score 5
