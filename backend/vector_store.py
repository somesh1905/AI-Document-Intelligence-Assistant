import os
from uuid import uuid5, NAMESPACE_URL

from dotenv import load_dotenv
from qdrant_client import QdrantClient, models

load_dotenv()

QDRANT_URL = os.getenv("QDRANT_URL")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")

COLLECTION_NAME = "enterprise_documents"
EMBEDDING_MODEL = "sentence-transformers/all-minilm-l6-v2"
VECTOR_SIZE = 384

if not QDRANT_URL or not QDRANT_API_KEY:
    raise ValueError(
        "Please configure QDRANT_URL and QDRANT_API_KEY."
    )

client = QdrantClient(
    url=QDRANT_URL,
    api_key=QDRANT_API_KEY,
    cloud_inference=True,
)


def initialize_collection():
    if not client.collection_exists(COLLECTION_NAME):
        client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=models.VectorParams(
                size=VECTOR_SIZE,
                distance=models.Distance.COSINE,
            ),
        )
        print("Created Qdrant collection:", COLLECTION_NAME)
    else:
        print("Qdrant collection already exists:", COLLECTION_NAME)


initialize_collection()


def add_document_chunks(chunks, document_id, filename):
    if not chunks:
        print("No chunks to add.")
        return

    points = []

    for i, chunk in enumerate(chunks):
        point_id = str(
            uuid5(
                NAMESPACE_URL,
                f"enterprise-doc-{document_id}-chunk-{i}",
            )
        )

        points.append(
            models.PointStruct(
                id=point_id,
                vector=models.Document(
                    text=chunk,
                    model=EMBEDDING_MODEL,
                ),
                payload={
                    "document_id": int(document_id),
                    "filename": filename,
                    "chunk_index": i,
                    "text": chunk,
                },
            )
        )

    client.upload_points(
        collection_name=COLLECTION_NAME,
        points=points,
        wait=True,
    )

    print(f"Added {len(points)} chunks to Qdrant Cloud.")


def search_documents(query, top_k=5):
    results = client.query_points(
        collection_name=COLLECTION_NAME,
        query=models.Document(
            text=query,
            model=EMBEDDING_MODEL,
        ),
        limit=top_k,
        with_payload=True,
    )

    points = results.points

    return {
        "ids": [[str(point.id) for point in points]],
        "documents": [
            [point.payload.get("text", "") for point in points]
        ],
        "metadatas": [
            [
                {
                    "document_id": point.payload.get("document_id"),
                    "filename": point.payload.get("filename"),
                    "chunk_index": point.payload.get("chunk_index"),
                }
                for point in points
            ]
        ],
        "distances": [
            [1.0 - point.score for point in points]
        ],
    }


def delete_document_chunks(document_id):
    result = client.delete(
        collection_name=COLLECTION_NAME,
        points_selector=models.FilterSelector(
            filter=models.Filter(
                must=[
                    models.FieldCondition(
                        key="document_id",
                        match=models.MatchValue(
                            value=int(document_id)
                        ),
                    )
                ]
            )
        ),
        wait=True,
    )

    print(f"Requested deletion of chunks for document {document_id}.")
    return result


def clear_all_documents():
    result = client.delete(
        collection_name=COLLECTION_NAME,
        points_selector=models.FilterSelector(
            filter=models.Filter(),
        ),
        wait=True,
    )

    print("Requested deletion of all document chunks.")
    return result


if __name__ == "__main__":
    print("Qdrant Cloud connected successfully!")
    print("Collection name:", COLLECTION_NAME)

    info = client.get_collection(COLLECTION_NAME)
    print("Stored vector points:", info.points_count)