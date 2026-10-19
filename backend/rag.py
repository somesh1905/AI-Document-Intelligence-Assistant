from backend.vector_store import search_documents
from backend.llm import generate_response


def retrieve_context(query, top_k=3):
    """
    Search ChromaDB and return both
    document context and source information.
    """

    results = search_documents(
        query,
        top_k=top_k
    )

    documents = results["documents"][0]
    metadatas = results["metadatas"][0]

    context = "\n\n".join(
        documents
    )

    sources = []

    for metadata in metadatas:

        sources.append(
    {
        "document_id": metadata.get("document_id"),
        "filename": metadata.get(
            "filename",
            "Unknown document"
        ),
        "chunk_index": metadata.get(
            "chunk_index"
        )
    }
)
    return context, sources


def build_prompt(query, context):
    """
    Build the prompt for the LLM.
    """

    prompt = f"""
You are an AI assistant for an enterprise organization.

Answer the user's question using ONLY the information
provided in the context below.

Do not use outside knowledge.

If the answer is not available in the context,
say:

"I could not find this information in the uploaded documents."

Keep the answer clear and concise.

Context:
--------------------
{context}
--------------------

User Question:
{query}

Answer:
"""

    return prompt


def ask_question(query):
    """
    Complete RAG pipeline:
    Search → Context → Prompt → LLM → Answer
    """

    context, sources = retrieve_context(
        query,
        top_k=2
    )

    prompt = build_prompt(
        query,
        context
    )

    answer = generate_response(
        prompt
    )

    return answer, context, sources


if __name__ == "__main__":

    print("Starting complete RAG test...")
    print("================================")

    question = "What are the working hours?"

    print("\nUser Question:")
    print(question)

    print("\nSearching documents...")

    answer, context, sources = ask_question(
        question
    )

    print("\nAI Answer:")
    print("================================")
    print(answer)

    print("\nSources:")
    print("================================")

    for source in sources:

        print(
            "Document ID:",
            source["document_id"]
        )

        print(
            "Chunk:",
            source["chunk_index"]
        )

    print("\nRAG test completed successfully!")