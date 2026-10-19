import os

from document_processor import (
    extract_text_from_pdf,
    split_text_into_chunks
)

from vector_store import add_document_chunks


BASE_DIR = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)


PDF_PATH = os.path.join(
    BASE_DIR,
    "documents",
    "enterprise_ai_test_document.pdf"
)


DOCUMENT_ID = 1


print("Starting document ingestion...")
print("PDF:", PDF_PATH)


text = extract_text_from_pdf(PDF_PATH)

print("PDF text extracted successfully!")
print("Characters:", len(text))


chunks = split_text_into_chunks(text)

print("Text split successfully!")
print("Number of chunks:", len(chunks))

add_document_chunks(
    chunks,
    DOCUMENT_ID
)


print("Document ingestion completed successfully!")