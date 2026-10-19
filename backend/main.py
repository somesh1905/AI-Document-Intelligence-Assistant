import os
import hashlib
from fastapi import FastAPI, UploadFile, File
from pydantic import BaseModel

from backend.agent import run_agent

from backend.document_processor import (
    extract_text_from_pdf,
    split_text_into_chunks
)
from backend.vector_store import (
    add_document_chunks,
    delete_document_chunks
)
from backend.database import SessionLocal
from backend.models import Document, ChatHistory

BASE_DIR = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

DOCUMENTS_DIR = os.path.join(
    BASE_DIR,
    "documents"
)

os.makedirs(
    DOCUMENTS_DIR,
    exist_ok=True
)

app = FastAPI(
    title="AI Document Intelligence & Enterprise Knowledge Assistant",
    description="RAG-powered enterprise document assistant",
    version="1.0.0"
)

class QuestionRequest(BaseModel):
    question: str

@app.get("/")
def home():

    return {
        "message": "AI Document Assistant API is running!",
        "status": "success"
    }

@app.post("/ask")
def ask(request: QuestionRequest):

    agent_result = run_agent(
        request.question
    )

    if agent_result.get("status") != "success":
        return agent_result

    answer = agent_result.get(
        "answer",
        ""
    )

    sources = agent_result.get(
        "sources",
        []
    )

    selected_tool = agent_result.get(
        "selected_tool"
    )

    db = SessionLocal()

    try:

        chat = ChatHistory(
            question=request.question,
            answer=answer
        )

        db.add(chat)

        db.commit()

        db.refresh(chat)

        return {
            "status": "success",
            "question": request.question,
            "answer": answer,
            "selected_tool": selected_tool,
            "sources": sources,
            "chat_id": chat.id
        }

    except Exception as e:

        db.rollback()

        return {
            "status": "error",
            "message": str(e)
        }

    finally:

        db.close()

@app.post("/upload")
async def upload_document(
    file: UploadFile = File(...)
):

    if not file.filename or not file.filename.lower().endswith(".pdf"):
        return {
            "status": "error",
            "message": "Only PDF files are allowed."
        }

    file_content = await file.read()

    if not file_content:
        return {
            "status": "error",
            "message": "The uploaded PDF is empty."
        }

    file_hash = hashlib.sha256(file_content).hexdigest()

    db = SessionLocal()

    try:
       
        existing_document = db.query(Document).filter(
            Document.file_hash == file_hash
        ).first()

        if existing_document:
            return {
                "status": "duplicate",
                "message": "This PDF has already been uploaded.",
                "filename": existing_document.filename,
                "document_id": existing_document.id
            }

        safe_filename = os.path.basename(file.filename)
        file_path = os.path.join(DOCUMENTS_DIR, safe_filename)

        if os.path.exists(file_path):
            name, extension = os.path.splitext(safe_filename)
            safe_filename = f"{name}_{file_hash[:8]}{extension}"
            file_path = os.path.join(DOCUMENTS_DIR, safe_filename)

        with open(file_path, "wb") as f:
            f.write(file_content)

        text = extract_text_from_pdf(file_path)

        if not text.strip():
            os.remove(file_path)
            return {
                "status": "error",
                "message": "No readable text was found in the PDF."
            }

        chunks = split_text_into_chunks(text)

        if not chunks:
            os.remove(file_path)
            return {
                "status": "error",
                "message": "No text chunks could be created from this PDF."
            }

        document = Document(
            filename=file.filename,
            file_path=file_path,
            file_hash=file_hash
        )

        db.add(document)
        db.commit()
        db.refresh(document)

        add_document_chunks(
            chunks,
            document.id,
            file.filename
        )

        return {
            "status": "success",
            "message": "Document uploaded and processed successfully.",
            "filename": file.filename,
            "characters_extracted": len(text),
            "chunks_created": len(chunks),
            "document_id": document.id
        }

    except Exception as e:
        db.rollback()

        return {
            "status": "error",
            "message": str(e)
        }

    finally:
        db.close()
        await file.close()
        
@app.get("/documents")
def get_documents():

    db = SessionLocal()

    try:

        documents = (
            db.query(Document)
            .order_by(Document.uploaded_at.desc())
            .all()
        )

        return {
            "status": "success",
            "count": len(documents),
            "documents": [
                {
                    "id": document.id,
                    "filename": document.filename,
                    "file_path": document.file_path,
                    "uploaded_at": document.uploaded_at
                }
                for document in documents
            ]
        }

    except Exception as e:

        return {
            "status": "error",
            "message": str(e)
        }

    finally:

        db.close()
        
@app.get("/chat-history")
def get_chat_history():

    db = SessionLocal()

    try:

        chats = (
            db.query(ChatHistory)
            .order_by(ChatHistory.created_at.desc())
            .all()
        )

        return {
            "status": "success",
            "count": len(chats),
            "chat_history": [
                {
                    "id": chat.id,
                    "question": chat.question,
                    "answer": chat.answer,
                    "created_at": chat.created_at
                }
                for chat in chats
            ]
        }

    except Exception as e:

        return {
            "status": "error",
            "message": str(e)
        }

    finally:

        db.close()

@app.delete("/chat-history/{chat_id}")
def delete_chat_history(chat_id: int):

    db = SessionLocal()

    try:

        chat = (
            db.query(ChatHistory)
            .filter(
                ChatHistory.id == chat_id
            )
            .first()
        )

        if not chat:

            return {
                "status": "error",
                "message": "Chat history not found."
            }

        db.delete(chat)

        db.commit()

        return {
            "status": "success",
            "message": "Chat history deleted successfully.",
            "chat_id": chat_id
        }

    except Exception as e:

        db.rollback()

        return {
            "status": "error",
            "message": str(e)
        }

    finally:

        db.close()
        
@app.delete("/documents/{document_id}")
def delete_document(document_id: int):

    db = SessionLocal()

    try:

        document = (
            db.query(Document)
            .filter(
                Document.id == document_id
            )
            .first()
        )

        if not document:

            return {
                "status": "error",
                "message": "Document not found."
            }

        file_path = document.file_path

        deleted_chunks = delete_document_chunks(
            document_id
        )

        db.delete(document)

        db.commit()

        if os.path.exists(file_path):

            os.remove(file_path)

        return {
            "status": "success",
            "message": "Document deleted successfully.",
            "document_id": document_id,
            "chunks_deleted": deleted_chunks
        }

    except Exception as e:

        db.rollback()

        return {
            "status": "error",
            "message": str(e)
        }

    finally:

        db.close()