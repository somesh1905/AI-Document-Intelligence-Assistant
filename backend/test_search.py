
from vector_store import search_documents

query = "Which certificates and internship certificates are listed in the resume?"

results = search_documents(query, top_k=10)

documents = results.get("documents", [[]])[0]
metadatas = results.get("metadatas", [[]])[0]
distances = results.get("distances", [[]])[0]

print("\n========== SEARCH RESULTS ==========\n")

for i, content in enumerate(documents):
    metadata = metadatas[i] if i < len(metadatas) else {}
    distance = distances[i] if i < len(distances) else None

    print(f"Result {i + 1}")
    print("Filename:", metadata.get("filename"))
    print("Document ID:", metadata.get("document_id"))
    print("Chunk index:", metadata.get("chunk_index"))
    print("Distance:", distance)
    print("Content:", content)
    print("-" * 70)
