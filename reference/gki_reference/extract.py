"""Offline extraction for the reference profile.

Handles plain text / markdown only (spec step 5 substitute: the canonical
spec mandates Tika for binary formats; the reference profile scopes to
text inputs so the pipeline is runnable with zero infrastructure).

Deterministic segmentation contract (used by scope, labeling, quality):
- title_text:   first line if it starts with "TITLE:" (value trimmed), else ""
- headings_text: concatenation of markdown heading lines ("#"-prefixed)
  and the heading marker lines used by fixtures (short lines that are not
  list items and end without punctuation are NOT treated as headings —
  only explicit "#" markers are, to stay deterministic)
- body_text / extracted_text: everything after the title line
"""

from dataclasses import dataclass


@dataclass
class ExtractedDoc:
    title: "str | None"
    headings: list
    extracted_text: str
    content_type: str
    parse_warnings: list


def extract_text_document(raw_text: str) -> ExtractedDoc:
    lines = raw_text.splitlines()
    title = None
    body_start = 0
    if lines and lines[0].startswith("TITLE:"):
        title = lines[0][len("TITLE:"):].strip() or None
        body_start = 1
    body_lines = lines[body_start:]
    headings = [ln.lstrip("#").strip() for ln in body_lines if ln.startswith("#")]
    extracted_text = "\n".join(body_lines).strip()
    return ExtractedDoc(
        title=title,
        headings=headings,
        extracted_text=extracted_text,
        content_type="text/plain",
        parse_warnings=[],
    )


def derive_summary(doc: ExtractedDoc) -> "str | None":
    """Deterministic summary: first non-empty, non-heading paragraph line."""
    for line in doc.extracted_text.splitlines():
        stripped = line.strip()
        if stripped and not stripped.startswith("#") and not stripped.startswith("-"):
            return stripped
    return None
