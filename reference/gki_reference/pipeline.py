"""Reference pipeline: spec execution contract steps 5-12 + 15-16.

Covered: offline extraction (text), normalization, 3-pass sensitive
verification, scope gate, labeling, quality scoring, chunking,
serialization with strict schema validation, raw deletion with proof,
success/failure ledgers.

Out of scope for the reference profile (see docs/PROFILES.md): portal
retrieval (steps 1-4 beyond local staging), Tika, Presidio/Gitleaks
services, ACL systems, publish-to-index.
"""

import datetime
import json
import shutil
import uuid
from pathlib import Path

from . import SCHEMA_VERSION
from .blocked import Blocked
from .chunking import chunk_document, token_count
from .extract import derive_summary, extract_text_document
from .fingerprints import file_sha256, fingerprint, text_sha256
from .labeling import label as run_labeling
from .quality import score_document
from .scope import classify
from .sensitive import (PII_CONFIG_HASH, PII_RULESET_ID, SECRETS_CONFIG_HASH,
                        SECRETS_RULESET_ID, scan_summary, scan_text)
from .serialize import (CHUNK_SCHEMA, MANIFEST_SCHEMA, validate_record,
                        write_json, write_jsonl)

REQUIRED_CONFIG_KEYS = [
    "dataset_id", "dataset_version", "index_version", "source_id",
    "acl_ref", "output_dir", "scope_policy", "labeling_policy",
    "quality_policy", "chunking_policy",
]


def _utcnow() -> str:
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _load_policy(repo_root: Path, ref) -> dict:
    if isinstance(ref, dict):
        return ref
    with open(repo_root / ref, "r", encoding="utf-8") as f:
        return json.load(f)


class ReferencePipeline:
    def __init__(self, config: dict, repo_root: "Path | None" = None):
        self.repo_root = repo_root or Path(__file__).resolve().parents[2]
        # CONFIG_VALIDATION_GATE: nulls and missing keys block, never default.
        for key in REQUIRED_CONFIG_KEYS:
            if config.get(key) is None:
                raise Blocked("config_invalid", f"required config key is null/missing: {key}")
        self.config = config
        self.scope_policy = _load_policy(self.repo_root, config["scope_policy"])
        self.labeling_policy = _load_policy(self.repo_root, config["labeling_policy"])
        self.quality_policy = _load_policy(self.repo_root, config["quality_policy"])
        self.chunking_policy = _load_policy(self.repo_root, config["chunking_policy"])
        self.output_dir = Path(config["output_dir"])
        self.run_id = config.get("run_id") or f"run-{uuid.uuid4().hex[:12]}"
        self.config_hash = fingerprint({k: v for k, v in config.items() if k != "output_dir"})

    # -- ledgers ------------------------------------------------------------
    def _ledger(self, name: str, entry: dict) -> None:
        path = self.output_dir / "ledgers" / f"{name}.jsonl"
        path.parent.mkdir(parents=True, exist_ok=True)
        entry = {"run_id": self.run_id, "timestamp_utc": _utcnow(), **entry}
        with open(path, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, sort_keys=True) + "\n")

    # -- main ---------------------------------------------------------------
    def ingest_file(self, input_path: "str | Path") -> dict:
        input_path = Path(input_path)
        doc_id = f"doc-{text_sha256(str(input_path.name))[7:19]}"
        try:
            return self._ingest(input_path, doc_id)
        except Blocked as b:
            self._ledger("failure", {
                "doc_id": doc_id, "input": str(input_path),
                "reason_code": b.code, "detail": b.detail,
            })
            raise

    def _ingest(self, input_path: Path, doc_id: str) -> dict:
        # SNAPSHOT + HASHING (step 4, local-staging form)
        source_hash = file_sha256(input_path)
        staging = self.output_dir / "staging" / input_path.name
        staging.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(input_path, staging)

        # OFFLINE EXTRACTION (step 5, reference profile: text only)
        raw_text = staging.read_text(encoding="utf-8")
        doc = extract_text_document(raw_text)
        summary = derive_summary(doc)

        # SENSITIVE PASS 1: pre-persist (step 7)
        scans = {"pass1_pre_persist": scan_text(raw_text)}
        if not scans["pass1_pre_persist"].clean:
            self._sensitive_block(doc_id, staging, scans)

        # SCOPE GATE (step 8)
        headings_text = " ".join(doc.headings)
        scope = classify(doc.title or "", headings_text, doc.extracted_text, self.scope_policy)
        if scope.decision == "OUT_OF_SCOPE":
            self._delete_staged(staging)
            raise Blocked("scope_out_of_scope", json.dumps(scope.audit))
        if scope.decision == "BLOCKED":
            self._delete_staged(staging)
            raise Blocked("scope_gate_low_confidence", json.dumps(scope.audit))

        # LABELING (step 9)
        labeling = run_labeling(doc.title or "", headings_text, doc.extracted_text, self.labeling_policy)

        # SENSITIVE PASS 2: derived fields (title/summary/labels)
        derived_text = " ".join(filter(None, [doc.title, summary] + labeling.labels))
        scans["pass2_derived_fields"] = scan_text(derived_text)
        if not scans["pass2_derived_fields"].clean:
            self._sensitive_block(doc_id, staging, scans)

        # QUALITY (step 10) — document-level, chunk-independent inputs first
        doc_tokens = token_count(doc.extracted_text)

        # CHUNKING (step 11)
        chunks = chunk_document(doc.title, doc.headings, doc.extracted_text, self.chunking_policy)
        content_hashes = [text_sha256(c.text) for c in chunks]
        duplicates = len(content_hashes) - len(set(content_hashes))
        duplicate_ratio = duplicates / max(1, len(chunks))

        expected_fields = ["title", "summary", "content_type", "section_path"]
        missing = sum(1 for v in [doc.title, summary, doc.content_type, "/"] if not v)
        missing_metadata_ratio = missing / len(expected_fields)

        quality = score_document(
            doc.extracted_text, doc_tokens, doc.title, summary,
            bool(doc.parse_warnings), duplicate_ratio, missing_metadata_ratio,
            self.quality_policy,
        )
        if not quality.passed:
            self._delete_staged(staging)
            raise Blocked("data_quality_gate",
                          f"score={quality.quality_score} flags={quality.quality_flags}")

        # Reserve deletion proof BEFORE serialization (step 11 spec ordering)
        deletion_proof_ref = f"proofs/{self.run_id}/{doc_id}.deletion-proof.json"

        # SERIALIZE (step 12) with strict schema validation
        records = [
            self._chunk_record(doc, summary, doc_id, source_hash, chunk,
                               content_hashes[i], scope, labeling, quality,
                               deletion_proof_ref)
            for i, chunk in enumerate(chunks)
        ]
        for record in records:
            validate_record(record, CHUNK_SCHEMA)

        chunks_path = self.output_dir / "sanitized" / f"{doc_id}.chunks.jsonl"
        write_jsonl(records, chunks_path)

        # SENSITIVE PASS 3: post-export scan of serialized output
        scans["pass3_post_export"] = scan_text(chunks_path.read_text(encoding="utf-8"))
        if not scans["pass3_post_export"].clean:
            chunks_path.unlink()
            self._sensitive_block(doc_id, staging, scans)

        # RAW DELETION + PROOF (step 15)
        proof = {
            "deleted_path": str(staging),
            "source_hash": source_hash,
            "deleted_at_utc": _utcnow(),
            "run_id": self.run_id,
        }
        self._delete_staged(staging)
        write_json(proof, self.output_dir / deletion_proof_ref)

        # MANIFEST + LEDGERS (step 16)
        manifest = self._manifest(doc_id, source_hash, records, scans, deletion_proof_ref)
        validate_record(manifest, MANIFEST_SCHEMA)
        manifest_path = self.output_dir / "sanitized" / f"{doc_id}.manifest.json"
        write_json(manifest, manifest_path)

        self._ledger("success", {
            "doc_id": doc_id, "chunks": len(records),
            "chunks_path": str(chunks_path), "manifest_path": str(manifest_path),
            "quality_score": quality.quality_score,
        })
        return {"doc_id": doc_id, "chunks": len(records),
                "chunks_path": str(chunks_path), "manifest_path": str(manifest_path)}

    # -- helpers ------------------------------------------------------------
    def _sensitive_block(self, doc_id: str, staging: Path, scans: dict):
        self._delete_staged(staging)
        raise Blocked("sensitive_data_violation", json.dumps(scan_summary(scans)))

    @staticmethod
    def _delete_staged(staging: Path):
        if staging.exists():
            staging.unlink()

    def _chunk_record(self, doc, summary, doc_id, source_hash, chunk,
                      content_hash, scope, labeling, quality, deletion_proof_ref) -> dict:
        extensions = {"scope": scope.audit, **labeling.extensions}
        return {
            "schema_version": SCHEMA_VERSION,
            "doc_id": doc_id,
            "title": doc.title,
            "summary": summary,
            "content_type": doc.content_type,
            "dataset_id": self.config["dataset_id"],
            "dataset_version": self.config["dataset_version"],
            "index_version": self.config["index_version"],
            "source_id": self.config["source_id"],
            "source_object_ref_hash": source_hash,
            "object_version": None,
            "section_path": chunk.section_path,
            "chunk_index": chunk.chunk_index,
            "chunk_id": f"{doc_id}:{chunk.chunk_index}",
            "content_hash": content_hash,
            "extracted_text": chunk.text,
            "token_count": chunk.token_count,
            "acl_ref": self.config["acl_ref"],
            "provenance_ref": f"provenance/{self.run_id}/{doc_id}.json",
            "scope_class": scope.scope_class or "",
            "scope_confidence": scope.scope_confidence,
            "scope_policy_fingerprint": fingerprint(self.scope_policy),
            "labels": labeling.labels,
            "label_confidence": labeling.label_confidence,
            "labeling_policy_fingerprint": fingerprint(self.labeling_policy),
            "taxonomy_version": labeling.taxonomy_version,
            "quality_score": quality.quality_score,
            "quality_flags": quality.quality_flags,
            "data_quality_policy_fingerprint": fingerprint(self.quality_policy),
            "sensitive_data_status": "pass",
            "sensitive_data_scan_summary_ref": f"scans/{self.run_id}/{doc_id}.json",
            "primary_detector_ruleset_id": PII_RULESET_ID,
            "primary_detector_config_hash": PII_CONFIG_HASH,
            "secondary_detector_ruleset_id": SECRETS_RULESET_ID,
            "secondary_detector_config_hash": SECRETS_CONFIG_HASH,
            "deletion_proof_ref": deletion_proof_ref,
            "sanitized_destination_uri": f"file://{self.output_dir}/sanitized/",
            "index_destination": self.config.get("index_destination", "reference://not-indexed"),
            "chunking_policy_fingerprint": fingerprint(self.chunking_policy),
            "extensions": extensions,
        }

    def _manifest(self, doc_id, source_hash, records, scans, deletion_proof_ref) -> dict:
        return {
            "schema_version": SCHEMA_VERSION,
            "doc_id": doc_id,
            "dataset_id": self.config["dataset_id"],
            "dataset_version": self.config["dataset_version"],
            "index_version": self.config["index_version"],
            "source_id": self.config["source_id"],
            "source_object_ref_hash": source_hash,
            "object_version": None,
            "counts": {"chunks": len(records)},
            "hashes": {"content_hashes": [r["content_hash"] for r in records]},
            "acl_ref": self.config["acl_ref"],
            "scope_policy_fingerprint": fingerprint(self.scope_policy),
            "labeling_policy_fingerprint": fingerprint(self.labeling_policy),
            "data_quality_policy_fingerprint": fingerprint(self.quality_policy),
            "chunking_policy_fingerprint": fingerprint(self.chunking_policy),
            "catalog_entry_ref": f"catalog/{self.run_id}/{doc_id}.json",
            "quality_report_ref": f"quality/{self.run_id}/{doc_id}.json",
            "run_stamps": {
                "run_id": self.run_id,
                "extraction_timestamp_utc": _utcnow(),
                "config_version": str(self.config.get("config_version", "reference-1")),
                "config_hash": self.config_hash,
            },
            "primary_detector_ruleset_id": PII_RULESET_ID,
            "primary_detector_config_hash": PII_CONFIG_HASH,
            "secondary_detector_ruleset_id": SECRETS_RULESET_ID,
            "secondary_detector_config_hash": SECRETS_CONFIG_HASH,
            "scan_summaries": scan_summary(scans),
            "deletion_proofs_summary": {"refs": [deletion_proof_ref]},
            "extensions": {},
        }
