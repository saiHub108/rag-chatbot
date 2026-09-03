from pathlib import Path

import numpy as np
import ollama

DOCUMENT_PATH = Path("data/sample_project_status.txt")
EMBEDDING_MODEL = "embeddinggemma"
CHAT_MODEL = "llama3.1:8b"
TOP_K = 3

def load_document(file_path):
    """Read a document and divide it into paragraph-sized chunks"""
   # text = file_path.read(encoding="utf-8")
    text = file_path.read_text(encoding="utf-8")

    chunks = [
        paragraph.strip()
        for paragraph in text.split("\n\n")
        if paragraph.strip()
    ]

    return chunks

def create_embeddings(texts):
    """Convert text chunks into numerical vectors."""
    response = ollama.embed(
        model = EMBEDDING_MODEL,
        input = texts,
    )

    return np.array(response["embeddings"], dtype=np.float32)

def cosine_similarity(query_vector, document_vectors):
     """Measure semantic similarity between a question and every chunk."""
     query_norm = np.linalg.norm(query_vector)
     document_norms = np.linalg.norm(document_vectors, axis=1)

     return (document_vectors @ query_vector) / (
         document_norms * query_norm
     )

def retrieve_relevant_chunks(question, chunks, chunk_vectors):
    """Return the document chunks most relevant to the question."""
    question_vector = create_embeddings([question])[0]
    similarity_scores = cosine_similarity(
        question_vector,
        chunk_vectors,
    )

    best_indexes = np.argsort(similarity_scores)[::-1][:TOP_K]

    results = []

    for index in best_indexes:
        results.append(
            {
                "chunk": chunks[index],
                "score": float(similarity_scores[index]),
            }
        )

    return results

def generate_grounded_answer(question, retrieved_chunks):
    """Ask the LLM to answer using only retrieved document content."""
    context_parts = []

    for number, result in enumerate(retrieved_chunks, start=1):
        context_parts.append(
            f"[SOURCE {number}]\n{result['chunk']}"
        )

    context = "\n\n".join(context_parts)

    prompt = f"""
    Answer the question using only the supplied sources.

    Rules:
    1. Preserve every name, date, amount, status, and identifier exactly.
    2. Do not combine dates or facts from different sources.
    3. Distinguish the risk date, dependency date, and mitigation deadline.
    4. Place a citation immediately after every factual statement.
    5. Use citation format [SOURCE 1], [SOURCE 2], or [SOURCE 3].
    6. If the sources do not provide the answer, say:
    "I cannot answer that from the provided project document."

    SOURCES:
    {context}

    QUESTION:
    {question}
    """

    response = ollama.chat(
        model=CHAT_MODEL,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are an evidence-based AI Delivery Copilot. "
                    "Never invent, modify, merge, or approximate project facts."
                ),
            },
            {
                "role": "user",
                "content": prompt,
            },
        ],
        options={
            "temperature": 0,
        },
    )

    return response["message"]["content"]

def main():
    chunks = load_document(DOCUMENT_PATH)
    chunk_vectors = create_embeddings(chunks)

    question = input(
        "\nAsk a question about the project: "
    ).strip()

    if not question:
        print("Please enter a question.")
        return

    retrieved_chunks = retrieve_relevant_chunks(
        question,
        chunks,
        chunk_vectors,
    )

    print("\nRETRIEVED SOURCES:")

    for number, result in enumerate(retrieved_chunks, start=1):
        print(
            f"\nSOURCE {number} "
            f"(similarity: {result['score']:.3f})"
        )
        print(result["chunk"])

    answer = generate_grounded_answer(
        question,
        retrieved_chunks,
    )

    print("\nQUESTION:")
    print(question)

    print("\nGROUNDED ANSWER:")
    print(answer)


if __name__ == "__main__":
    main()


