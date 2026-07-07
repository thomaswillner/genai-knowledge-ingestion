"""End-to-end reference run: clean fixture -> schema-valid outputs + proofs + ledgers."""

import json
from pathlib import Path

import pytest
from conftest import FIXTURES

from gki_reference.blocked import Blocked
from gki_reference.pipeline import ReferencePipeline
from gki_reference.serialize import CHUNK_SCHEMA, MANIFEST_SCHEMA, validate_record


def test_full_run_on_clean_fixture(reference_config):
    pipeline = ReferencePipeline(reference_config)
    result = pipeline.ingest_file(FIXTURES / "quality_good.txt")
    out = Path(reference_config["output_dir"])

    # chunk records exist and validate against the strict schema
    chunks_path = Path(result["chunks_path"])
    records = [json.loads(line) for line in chunks_path.read_text().splitlines()]
    assert records
    for record in records:
        validate_record(record, CHUNK_SCHEMA)
        assert record["sensitive_data_status"] == "pass"
        assert record["scope_class"] in ("architecture", "runbook", "code", "control_implementation")
        assert record["scope_confidence"] >= 0.8

    # manifest validates
    manifest = json.loads(Path(result["manifest_path"]).read_text())
    validate_record(manifest, MANIFEST_SCHEMA)
    assert manifest["counts"]["chunks"] == len(records)

    # raw deleted, deletion proof materialized under the reserved ref
    assert not (out / "staging" / "quality_good.txt").exists()
    proof_path = out / records[0]["deletion_proof_ref"]
    assert proof_path.exists()
    proof = json.loads(proof_path.read_text())
    assert proof["source_hash"] == records[0]["source_object_ref_hash"]

    # success ledger written
    ledger_lines = (out / "ledgers" / "success.jsonl").read_text().splitlines()
    assert any(json.loads(l)["doc_id"] == result["doc_id"] for l in ledger_lines)


def test_out_of_scope_fixture_blocks_and_ledgers(reference_config):
    pipeline = ReferencePipeline(reference_config)
    with pytest.raises(Blocked) as exc:
        pipeline.ingest_file(FIXTURES / "scope_out_of_scope_marketing.txt")
    assert exc.value.code == "scope_out_of_scope"


def test_null_config_key_blocks(reference_config):
    reference_config["acl_ref"] = None
    with pytest.raises(Blocked) as exc:
        ReferencePipeline(reference_config)
    assert exc.value.code == "config_invalid"
