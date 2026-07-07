import json
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "reference"))

FIXTURES = REPO_ROOT / "tests" / "fixtures"


def load_policy(rel_path: str) -> dict:
    with open(REPO_ROOT / rel_path, "r", encoding="utf-8") as f:
        return json.load(f)


def load_fixture_doc(name: str):
    from gki_reference.extract import extract_text_document
    raw = (FIXTURES / name).read_text(encoding="utf-8")
    return extract_text_document(raw)


@pytest.fixture
def scope_policy():
    return load_policy("spec/policies/presets/scope.CYBERSEC_TECH_ONLY_V1.json")


@pytest.fixture
def labeling_policy():
    return load_policy("spec/policies/presets/labeling.LABELING_MIN_V2.json")


@pytest.fixture
def quality_policy():
    return load_policy("spec/policies/presets/quality.QUALITY_MIN_V1.json")


@pytest.fixture
def chunking_policy():
    return load_policy("spec/policies/presets/chunking.CHUNKING_BASELINE_V1.json")


@pytest.fixture
def reference_config(tmp_path):
    with open(REPO_ROOT / "config" / "reference-config.json", "r", encoding="utf-8") as f:
        config = json.load(f)
    config["output_dir"] = str(tmp_path / "out")
    return config
