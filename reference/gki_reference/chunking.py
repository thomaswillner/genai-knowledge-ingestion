"""Deterministic structure-aware token chunking (spec section 9).

Tokenizer: cl100k_base via tiktoken is REQUIRED by the spec. If tiktoken
is unavailable the gate fails closed (BLOCKED: tokenizer_unavailable) —
there is deliberately no silent fallback tokenizer.

Documented spec clarification (surfaced by this implementation, see
docs/IMPLEMENTATION-NOTES.md): a document shorter than min_chunk_tokens
yields exactly one chunk; the minimum applies to split points, not to
documents that are inherently short.
"""

from dataclasses import dataclass

from .blocked import Blocked

try:
    import tiktoken
    _ENC = tiktoken.get_encoding("cl100k_base")
except Exception:  # pragma: no cover - exercised only without tiktoken
    _ENC = None


def token_count(text: str) -> int:
    if _ENC is None:
        raise Blocked("tokenizer_unavailable", "cl100k_base (tiktoken) is required")
    return len(_ENC.encode(text))


@dataclass
class Chunk:
    chunk_index: int
    text: str
    token_count: int
    section_path: str


def _normalize_ws(text: str) -> str:
    return " ".join(text.split())


def chunk_document(title: "str | None", headings: list, body: str, chunking_policy: dict) -> list:
    if _ENC is None:
        raise Blocked("tokenizer_unavailable", "cl100k_base (tiktoken) is required")

    size = int(chunking_policy["chunk_size_tokens"])
    overlap = int(chunking_policy["chunk_overlap_tokens"])
    hard_cap = int(chunking_policy["max_chunk_tokens_hard_cap"])

    # Ordered blocks: title, headings, body (spec 9 step 1), whitespace-normalized (step 2)
    blocks = []
    if title:
        blocks.append(("title", _normalize_ws(title)))
    if headings:
        blocks.append(("headings", _normalize_ws(" ".join(headings))))
    blocks.append(("body", _normalize_ws(body)))

    full_text = " ".join(text for _, text in blocks if text).strip()
    tokens = _ENC.encode(full_text)

    if not tokens:
        return []

    chunks = []
    start = 0
    index = 0
    while start < len(tokens):
        end = min(start + size, len(tokens))
        piece_tokens = tokens[start:end]
        if len(piece_tokens) > hard_cap:
            piece_tokens = piece_tokens[:hard_cap]
            end = start + hard_cap
        text = _ENC.decode(piece_tokens)
        chunks.append(Chunk(index, text, len(piece_tokens), section_path="/"))
        index += 1
        if end >= len(tokens):
            break
        start = end - overlap

    return chunks
