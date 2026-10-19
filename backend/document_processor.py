import os

from pypdf import PdfReader
from langchain_text_splitters import RecursiveCharacterTextSplitter


def extract_text_from_pdf(file_path):
    """
    Extract text from a PDF file.
    """

    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    reader = PdfReader(file_path)

    text = ""

    for page in reader.pages:
        page_text = page.extract_text()

        if page_text:
            text += page_text + "\n"

    return text


def split_text_into_chunks(text):
    """
    Split extracted text into smaller chunks.
    """

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200
    )

    chunks = text_splitter.split_text(text)

    return chunks


if __name__ == "__main__":

    pdf_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "documents",
        "enterprise_ai_test_document.pdf"
    )

    print("Reading PDF...")
    
    text = extract_text_from_pdf(pdf_path)

    print("PDF text extracted successfully!")
    print("Characters extracted:", len(text))

    chunks = split_text_into_chunks(text)

    print("Text split into chunks successfully!")
    print("Number of chunks:", len(chunks))

    print("\nFirst chunk:")
    print("--------------------")
    print(chunks[0])
    print("--------------------")