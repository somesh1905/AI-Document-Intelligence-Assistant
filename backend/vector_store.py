import os

import chromadb
from sentence_transformers import SentenceTransformer


BASE_DIR = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

VECTORSTORE_DIR = os.path.join(
    BASE_DIR,
    "vectorstore"
)

client = chromadb.PersistentClient(
    path=VECTORSTORE_DIR
)

collection = client.get_or_create_collection(
    name="enterprise_documents"
)

embedding_model = SentenceTransformer(
    "all-MiniLM-L6-v2"
)


def add_document_chunks(chunks, document_id, filename):
    if not chunks:
        print("No chunks to add.")
        return

    embeddings = embedding_model.encode(
        chunks
    ).tolist()

    ids = [
        f"doc_{document_id}_chunk_{i}"
        for i in range(len(chunks))
    ]

    metadatas = [
        {
            "document_id": document_id,
            "filename": filename,
            "chunk_index": i
        }
        for i in range(len(chunks))
    ]

    collection.add(
        ids=ids,
        embeddings=embeddings,
        documents=chunks,
        metadatas=metadatas
    )

    print(
        f"Added {len(chunks)} chunks to ChromaDB."
    )


def search_documents(query, top_k=5):
    """
    Search ChromaDB for chunks
    similar to the user's question.
    """

    query_embedding = embedding_model.encode(
        [query]
    ).tolist()

    results = collection.query(
        query_embeddings=query_embedding,
        n_results=top_k
    )

    return results

def delete_document_chunks(document_id):
    """
    Delete all ChromaDB chunks belonging
    to a specific document.
    """

    results = collection.get(
        where={
            "document_id": document_id
        }
    )

    ids = results.get("ids", [])

    if not ids:
        print(
            f"No chunks found for document {document_id}."
        )
        return 0

    collection.delete(
        ids=ids
    )

    print(
        f"Deleted {len(ids)} chunks from ChromaDB."
    )

    return len(ids)

def clear_all_documents():
    """
    Delete all chunks from the ChromaDB collection.
    """

    results = collection.get()

    ids = results.get("ids", [])

    if not ids:
        print("ChromaDB is already empty.")
        return 0

    collection.delete(
        ids=ids
    )

    print(
        f"Deleted {len(ids)} chunks from ChromaDB."
    )

    return len(ids)


if __name__ == "__main__":

    print("ChromaDB connected successfully!")

    print(
        "Vector database location:",
        VECTORSTORE_DIR
    )

    print(
        "Collection name:",
        collection.name
    )

    print(
        "Embedding model loaded successfully!"
    )

    print("\nCurrent vector database data:")
    print("--------------------------------")

    results = collection.get(
        include=[
            "documents",
            "metadatas"
        ]
    )

    ids = results.get("ids", [])
    metadatas = results.get("metadatas", [])

    print(
        "Total chunks:",
        len(ids)
    )

    for i, metadata in enumerate(metadatas):

        print(
            f"Chunk {i + 1}:",
            metadata
        )
        