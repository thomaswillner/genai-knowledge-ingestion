"""Output serialization with strict schema validation (spec section 10).

Every chunk record and manifest is validated against the canonical
schemas before being written. Schema violations are fail-closed with the
spec's normative codes.
"""

import json
from pathlib import Path

import jsonschema

from .blocked import Blocked

_SPEC_DIR = Path(__file__).resolve().parents[2] / "spec" / "schemas"


def _load_schema(name: str) -> dict:
    with open(_SPEC_DIR / name, "r", encoding="utf-8") as f:
        return json.load(f)


CHUNK_SCHEMA = _load_schema("gki.chunk-record.schema.json")
MANIFEST_SCHEMA = _load_schema("gki.manifest.schema.json")


def validate_record(record: dict, schema: dict) -> None:
    validator = jsonschema.Draft202012Validator(schema)
    errors = sorted(validator.iter_errors(record), key=lambda e: list(e.absolute_path))
    if not errors:
        return
    first = errors[0]
    if first.validator == "required":
        raise Blocked("schema_missing_required_field", first.message)
    if first.validator == "additionalProperties":
        raise Blocked("schema_unknown_field", first.message)
    raise Blocked("schema_validation_failed", first.message)


def write_jsonl(records: list, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        for record in records:
            f.write(json.dumps(record, sort_keys=True, ensure_ascii=True) + "\n")


def write_json(obj: dict, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, sort_keys=True, indent=2, ensure_ascii=True)
