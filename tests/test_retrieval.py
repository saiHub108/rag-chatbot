import pytest

from rag_demo import (
    DOCUMENT_PATH,
    create_embeddings,
    load_document,
    retrieve_relevant_chunks,
)


@pytest.fixture(scope="session")
def indexed_document():
    """
    Load and embed the document once for the complete test session.

    Session scope prevents the embedding model from repeating the same
    work separately for every test.
    """
    chunks = load_document(DOCUMENT_PATH)
    chunk_vectors = create_embeddings(chunks)

    return chunks, chunk_vectors

def test_retrieves_performance_environment_risk(indexed_document):
    chunks, chunk_vectors = indexed_document

    results = retrieve_relevant_chunks(
        (
            "Which risk threatens performance testing, "
            "who owns it, and what is the mitigation?"
        ),
        chunks,
        chunk_vectors,
    )

    top_chunk = results[0]["chunk"]

    assert "RISK-001" in top_chunk
    assert "Ravi Kumar" in top_chunk
    assert "September 8" in top_chunk

def test_retrieves_partial_refund_issue(indexed_document):
    chunks, chunk_vectors = indexed_document

    results = retrieve_relevant_chunks(
        "Who owns the problem with partial-refund transactions?",
        chunks,
        chunk_vectors,
    )

    top_chunk = results[0]["chunk"]

    assert "ISSUE-014" in top_chunk
    assert "Priya Shah" in top_chunk
    assert "September 6" in top_chunk

def test_retrieves_database_decision(indexed_document):
    chunks, chunk_vectors = indexed_document

    results = retrieve_relevant_chunks(
        "Which database did the architecture board approve?",
        chunks,
        chunk_vectors,
    )

    top_chunk = results[0]["chunk"]

    assert "DEC-004" in top_chunk
    assert "PostgreSQL" in top_chunk
    assert "August 18, 2026" in top_chunk