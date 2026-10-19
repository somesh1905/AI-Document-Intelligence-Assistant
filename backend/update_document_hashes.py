import hashlib
import os

from backend.database import SessionLocal
from backend.models import Document

db = SessionLocal()

try:
    documents = db.query(Document).filter(
        Document.file_hash.is_(None)
    ).all()

    updated = 0
    missing = 0

    for document in documents:
        if not os.path.isfile(document.file_path):
            print(f"File missing: {document.filename} (ID {document.id})")
            missing += 1
            continue

        with open(document.file_path, "rb") as pdf_file:
            file_hash = hashlib.sha256(pdf_file.read()).hexdigest()

        duplicate = db.query(Document).filter(
            Document.file_hash == file_hash
        ).first()

        if duplicate:
            print(
                f"Duplicate content found: {document.filename} "
                f"(ID {document.id}); existing ID {duplicate.id}"
            )
            continue

        document.file_hash = file_hash
        updated += 1

    db.commit()

    print(f"\nHashes saved: {updated}")
    print(f"Files missing: {missing}")

except Exception as error:
    db.rollback()
    print("Error updating hashes:", error)

finally:
    db.close()