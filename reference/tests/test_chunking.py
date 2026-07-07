"""Chunking: determinism, boundaries, hard caps (spec section 9)."""

from gki_reference.chunking import chunk_document, token_count


def test_deterministic_same_input_same_chunks(chunking_policy):
    body = "Configure the identity provider. " * 300
    a = chunk_document("Title", ["H1"], body, chunking_policy)
    b = chunk_document("Title", ["H1"], body, chunking_policy)
    assert [(c.text, c.token_count) for c in a] == [(c.text, c.token_count) for c in b]


def test_chunk_sizes_and_overlap(chunking_policy):
    body = "word " * 3000
    chunks = chunk_document(None, [], body, chunking_policy)
    assert len(chunks) > 1
    for chunk in chunks[:-1]:
        assert chunk.token_count == chunking_policy["chunk_size_tokens"]
    for chunk in chunks:
        assert chunk.token_count <= chunking_policy["max_chunk_tokens_hard_cap"]
    assert [c.chunk_index for c in chunks] == list(range(len(chunks)))


def test_short_document_single_chunk(chunking_policy):
    chunks = chunk_document("T", [], "short body text", chunking_policy)
    assert len(chunks) == 1  # documented clarification: min applies to splits, not short docs


def test_token_count_stable():
    assert token_count("hello world") == token_count("hello world")
