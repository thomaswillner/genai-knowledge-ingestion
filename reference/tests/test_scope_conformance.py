"""SCOPE CONFORMANCE TEST GATE (spec Appendix A, mandatory for VERIFY/DONE)."""

from conftest import load_fixture_doc

from gki_reference.scope import classify


def _classify(name, scope_policy):
    doc = load_fixture_doc(name)
    return classify(doc.title or "", " ".join(doc.headings), doc.extracted_text, scope_policy)


def test_in_scope_iam(scope_policy):
    result = _classify("scope_in_scope_iam.txt", scope_policy)
    assert result.decision == "IN_SCOPE"
    assert result.scope_class in scope_policy["allowlist_taxonomy"]
    assert result.scope_confidence >= scope_policy["scope_confidence_threshold"]
    assert result.audit["classifier_version"] == "classifier_v1"


def test_out_of_scope_marketing_deny_final(scope_policy):
    result = _classify("scope_out_of_scope_marketing.txt", scope_policy)
    assert result.decision == "OUT_OF_SCOPE"
    assert result.audit["decision"] == "OUT_OF_SCOPE"
    # v18 defect fix: deny decisions are final regardless of confidence
    assert result.audit["deny_top_score"] >= scope_policy["classifier_v1"]["deny_threshold"]


def test_ambiguous_mixed_fails_closed(scope_policy):
    result = _classify("scope_ambiguous_mixed.txt", scope_policy)
    assert result.decision == "BLOCKED"
