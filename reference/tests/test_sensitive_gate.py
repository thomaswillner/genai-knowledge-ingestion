"""Sensitive-data gate: fail-closed, 3 enforcement points (spec section 5)."""

import pytest
from conftest import FIXTURES

from gki_reference.blocked import Blocked
from gki_reference.pipeline import ReferencePipeline
from gki_reference.sensitive import scan_text


def test_synthetic_fixture_detects_all_planted_categories():
    raw = (FIXTURES / "synthetic_iam_runbook.txt").read_text(encoding="utf-8")
    result = scan_text(raw)
    rules_hit = {f.rule for f in result.findings}
    assert "EMAIL" in rules_hit
    assert "PHONE_INTL" in rules_hit
    assert "IBAN" in rules_hit
    assert "AWS_ACCESS_KEY_ID" in rules_hit


def test_findings_never_leak_full_secret():
    result = scan_text("AWS Access Key: AKIAIOSFODNN7EXAMPLE")
    assert result.findings
    for finding in result.findings:
        assert len(finding.match_preview) <= 8


def test_pipeline_blocks_on_synthetic_runbook(reference_config):
    pipeline = ReferencePipeline(reference_config)
    with pytest.raises(Blocked) as exc:
        pipeline.ingest_file(FIXTURES / "synthetic_iam_runbook.txt")
    assert exc.value.code == "sensitive_data_violation"
    # failure ledger written, staged raw deleted
    from pathlib import Path
    out = Path(reference_config["output_dir"])
    assert (out / "ledgers" / "failure.jsonl").exists()
    assert not any((out / "staging").glob("*")) or not (out / "staging").exists()
