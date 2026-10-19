from backend.vector_store import delete_document_chunks

duplicate_document_ids = [15, 16, 17, 18, 19, 20]

print("Starting duplicate chunk cleanup...")

for document_id in duplicate_document_ids:
    print(f"\nProcessing document ID {document_id}")
    delete_document_chunks(document_id)

print("\nDuplicate chunk cleanup completed.")