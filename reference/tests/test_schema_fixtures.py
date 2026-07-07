"""Strict schema validation of the shipped JSON fixtures (fixtures README requirement)."""

import json

import pytest
from conftest import FIXTURES

from gki_reference.blocked import Blocked
from gki_reference.serialize import CHUNK_SCHEMA, MANIFEST_SCHEMA, validate_record


def _load(name):
    with open(FIXTURES / name, "r", encoding="utf-8") as f:
        return json.load(f)


def test_chunk_fixture_valid():
    validate_record(_load("schema_valid_chunk.json"), CHUNK_SCHEMA)


def test_manifest_fixture_valid():
    validate_record(_load("schema_valid_manifest.json"), MANIFEST_SCHEMA)


def test_unknown_field_blocks():
    record = _load("schema_valid_chunk.json")
    record["rogue_field"] = "x"
    with pytest.raises(Blocked) as exc:
        validate_record(record, CHUNK_SCHEMA)
    assert exc.value.code == "schema_unknown_field"


def test_missing_required_field_blocks():
    record = _load("schema_valid_chunk.json")
    del record["content_hash"]
    with pytest.raises(Blocked) as exc:
        validate_record(record, CHUNK_SCHEMA)
    assert exc.value.code == "schema_missing_required_field"
