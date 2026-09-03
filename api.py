from functools import lru_cache

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from rag_demo import (
    DOCUMENT_PATH,
    create_embeddings,
    generate_grounded_answer,
    load_document,
    retrieve_relevant_chunks,
)

API_VERSION = "0.2.0"
""" app = FastAPI(
    title="AI Delivery Intelligence Copilot API",
    description=(
        "A local-first RAG API for querying project-delivery documents "
        "with grounded answers and source citations."
    ),
    version="0.1.0",
) """

app = FastAPI(
    title="AI Delivery Intelligence Copilot API",
    description=(
        "A local-first RAG API for querying project-delivery documents "
        "with grounded answers and source citations."
    ),
    version="0.2.0",
)

class AskRequest(BaseModel):
    question: str = Field(
        min_length=3,
        max_length=500,
        description="Question about the indexed project document",
        examples=[
            "Which risk is threatening performance testing?"
        ],
    )


class SourceResponse(BaseModel):
    source_number: int
    content: str
    similarity_score: float


class AskResponse(BaseModel):
    question: str
    answer: str
    sources: list[SourceResponse]

@lru_cache(maxsize=1)
def get_document_index():
    """
    Load and embed the project document once, then reuse the index.
    """
    chunks = load_document(DOCUMENT_PATH)
    chunk_vectors = create_embeddings(chunks)

    return chunks, chunk_vectors

@app.get(
    "/health",
    summary="Check API health",
    tags=["System"],
)

def health_check():
    """Confirm that the FastAPI application is running."""
    return {
        "status": "healthy",
        "service": "AI Delivery Intelligence Copilot",
        "version": API_VERSION,
    }

@app.post(
    "/ask",
    response_model=AskResponse,
    summary="Ask a question about the project",
    tags=["RAG"],
)
def ask_project_question(request: AskRequest):
    """
    Retrieve relevant project evidence and generate a grounded answer.
    """
    try:
        chunks, chunk_vectors = get_document_index()

        retrieved_chunks = retrieve_relevant_chunks(
            request.question,
            chunks,
            chunk_vectors,
        )

        answer = generate_grounded_answer(
            request.question,
            retrieved_chunks,
        )

        sources = [
            SourceResponse(
                source_number=number,
                content=result["chunk"],
                similarity_score=round(result["score"], 3),
            )
            for number, result in enumerate(
                retrieved_chunks,
                start=1,
            )
        ]

        return AskResponse(
            question=request.question,
            answer=answer,
            sources=sources,
        )

    except FileNotFoundError as error:
        raise HTTPException(
            status_code=500,
            detail="The project document could not be found.",
        ) from error

    except Exception as error:
        raise HTTPException(
            status_code=503,
            detail=(
                "The local AI service is unavailable. "
                "Confirm that Ollama is running."
            ),
        ) from error