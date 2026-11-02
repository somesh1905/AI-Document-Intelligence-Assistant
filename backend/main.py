import os
import hashlib

from fastapi import (
    FastAPI,
    UploadFile,
    File,
    HTTPException,
    Depends
)
from fastapi.responses import FileResponse
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy.exc import IntegrityError

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
from backend.models import User, Document, ChatHistory

from backend.auth import (
    hash_password,
    verify_password,
    create_access_token,
    get_current_user,
)



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
class RegisterRequest(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1, max_length=128)

@app.get("/")
def home():

    return {
        "message": "AI Document Assistant API is running!",
        "status": "success"
    }

@app.post("/ask")
def ask(
    request: QuestionRequest,
    current_user: User = Depends(get_current_user),
):
    agent_result = run_agent(request.question, current_user.id)

    if agent_result.get("status") != "success":
        return agent_result

    answer = agent_result.get("answer", "")
    sources = agent_result.get("sources", [])
    selected_tool = agent_result.get("selected_tool")

    db = SessionLocal()

    try:
        chat = ChatHistory(
            question=request.question,
            answer=answer,
            user_id=current_user.id,
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
            "chat_id": chat.id,
        }
        
    

    except Exception:
            db.rollback()
            raise HTTPException(
               status_code=500,
                detail="Failed to save chat history.",
            )

    finally:
        db.close()


@app.post("/register")
def register(request: RegisterRequest):
    name = request.name.strip()
    email = request.email.strip().lower()

    if not name:
        raise HTTPException(
            status_code=400,
            detail="Name cannot be empty."
        )

    db = SessionLocal()

    try:
        existing_user = db.query(User).filter(
            User.email == email
        ).first()

        if existing_user:
            raise HTTPException(
                status_code=409,
                detail="An account with this email already exists."
            )

        user = User(
            name=name,
            email=email,
            password_hash=hash_password(request.password)
        )

        db.add(user)
        db.commit()
        db.refresh(user)

        return {
            "status": "success",
            "message": "Account created successfully.",
            "user": {
                "id": user.id,
                "name": user.name,
                "email": user.email
            }
        }

    except HTTPException:
        db.rollback()
        raise

    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="An account with this email already exists."
        )

    finally:
        db.close()


@app.post("/login")
def login(request: LoginRequest):
    email = request.email.strip().lower()

    db = SessionLocal()

    try:
        user = db.query(User).filter(
            User.email == email
        ).first()

        if (
            not user
            or not user.password_hash
            or not verify_password(
                request.password,
                user.password_hash
            )
        ):
            raise HTTPException(
                status_code=401,
                detail="Invalid email or password."
            )

        token = create_access_token(
            user_id=user.id,
            email=user.email
        )

        return {
            "status": "success",
            "access_token": token,
            "token_type": "bearer",
            "user": {
                "id": user.id,
                "name": user.name,
                "email": user.email
            }
        }

    finally:
        db.close()


@app.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user)
):
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are allowed."
        )

    file_content = await file.read()

    if not file_content:
        raise HTTPException(
            status_code=400,
            detail="The uploaded PDF is empty."
        )

    file_hash = hashlib.sha256(file_content).hexdigest()

    db = SessionLocal()

    file_path = None
    document = None
    qdrant_upload_attempted = False

    try:
        existing_document = db.query(Document).filter(
            Document.file_hash == file_hash,
            Document.user_id == current_user.id
        ).first()

        if existing_document:
            return {
                "status": "duplicate",
                "message": "This PDF has already been uploaded.",
                "filename": existing_document.filename,
                "document_id": existing_document.id
            }

        safe_filename = (
            f"user_{current_user.id}_{file_hash}.pdf"
        )

        file_path = os.path.join(
            DOCUMENTS_DIR,
            safe_filename
        )

        with open(file_path, "wb") as f:
            f.write(file_content)

        text = extract_text_from_pdf(file_path)

        if not text.strip():
            raise HTTPException(
                status_code=400,
                detail="No readable text was found in the PDF."
            )

        chunks = split_text_into_chunks(text)

        if not chunks:
            raise HTTPException(
                status_code=400,
                detail="No text chunks could be created from this PDF."
            )

        document = Document(
            filename=file.filename,
            file_path=file_path,
            file_hash=file_hash,
            user_id=current_user.id
        )

        db.add(document)
        db.flush()

        qdrant_upload_attempted = True

        add_document_chunks(
            chunks,
            document.id,
            file.filename,
            current_user.id
        )

        db.commit()
        db.refresh(document)

        return {
            "status": "success",
            "message": "Document uploaded and processed successfully.",
            "filename": file.filename,
            "characters_extracted": len(text),
            "chunks_created": len(chunks),
            "document_id": document.id
        }

    except HTTPException:
        db.rollback()
        raise

    except Exception:
        db.rollback()

        # Remove any Qdrant chunks created by this upload attempt.
        if qdrant_upload_attempted and document is not None:
            try:
                delete_document_chunks(
                    document.id,
                    current_user.id
                )
            except Exception:
                print(
                    "Warning: Qdrant cleanup failed for document:",
                    document.id
                )

        # Remove the newly uploaded PDF.
        if file_path and os.path.exists(file_path):
            try:
                os.remove(file_path)
            except OSError:
                print("Warning: Uploaded PDF cleanup failed.")

        raise HTTPException(
            status_code=500,
            detail="Document upload failed. Please try again."
        )

    finally:
        db.close()
        await file.close()
        

@app.get("/documents")
def get_documents(
    current_user: User = Depends(get_current_user),
):
    db = SessionLocal()

    try:
        documents = (
            db.query(Document)
            .filter(Document.user_id == current_user.id)
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
                    "uploaded_at": document.uploaded_at
                }
                for document in documents
            ]
        }

    except Exception as e:
           import traceback
           traceback.print_exc()
           print(f"UPLOAD ERROR: {repr(e)}", flush=True)

           print("========== DOCUMENT UPLOAD ERROR ==========")
           traceback.print_exc()
           print("============================================")

           db.rollback()
           raise HTTPException(
            status_code=500,
            detail="Failed to retrieve your documents."
        )

    finally:
        db.close()

@app.get("/documents/{document_id}/view")
def view_document(
    document_id: int,
    current_user: User = Depends(get_current_user)
):
    db = SessionLocal()

    try:
        document = (
            db.query(Document)
            .filter(
                Document.id == document_id,
                Document.user_id == current_user.id
            )
            .first()
        )

        if not document:
            raise HTTPException(
                status_code=404,
                detail="Document not found."
            )

        file_path = document.file_path

        if not file_path or not os.path.isfile(file_path):
            raise HTTPException(
                status_code=404,
                detail="PDF file is not available."
            )

        return FileResponse(
            path=file_path,
            media_type="application/pdf",
            filename=document.filename,
            content_disposition_type="inline"
        )

    except HTTPException:
        raise

    except Exception as e:
        import traceback
        
        print("========== DOCUMENT UPLOAD ERROR ==========", flush=True)
        traceback.print_exc()
        print(f"UPLOAD ERROR: {repr(e)}", flush=True)
        print("============================================", flush=True)

        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Unable to open this document."
        )

    finally:
        db.close()

@app.get("/chat-history")
def get_chat_history(
    current_user: User = Depends(get_current_user)
):
    db = SessionLocal()

    try:
        chats = (
            db.query(ChatHistory)
            .filter(ChatHistory.user_id == current_user.id)
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
        import traceback
        
        print("========== DOCUMENT UPLOAD ERROR ==========", flush=True)
        traceback.print_exc()
        print(f"UPLOAD ERROR: {repr(e)}", flush=True)
        print("============================================", flush=True)

        db.rollback()

        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve your chat history."
        )

    finally:
        db.close()

@app.delete("/chat-history/{chat_id}")
def delete_chat_history(
    chat_id: int,
    current_user: User = Depends(get_current_user)
):
    db = SessionLocal()

    try:
        chat = (
            db.query(ChatHistory)
            .filter(
                ChatHistory.id == chat_id,
                ChatHistory.user_id == current_user.id
            )
            .first()
        )

        if not chat:
            raise HTTPException(
                status_code=404,
                detail="Chat history not found."
            )

        db.delete(chat)
        db.commit()

        return {
            "status": "success",
            "message": "Chat history deleted successfully.",
            "chat_id": chat_id
        }

    except HTTPException:
        raise

    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Failed to delete chat history."
        )

    finally:
        db.close()

@app.get("/documents/{document_id}/view")
def view_document(
    document_id: int,
    current_user: User = Depends(get_current_user)
):
    db = SessionLocal()

    try:
        document = (
            db.query(Document)
            .filter(
                Document.id == document_id,
                Document.user_id == current_user.id
            )
            .first()
        )

        if not document:
            raise HTTPException(
                status_code=404,
                detail="Document not found."
            )

        if not os.path.isfile(document.file_path):
            raise HTTPException(
                status_code=404,
                detail="PDF file not found."
            )

        return FileResponse(
            path=document.file_path,
            media_type="application/pdf",
            filename=document.filename,
            content_disposition_type="inline"
        )

    finally:
        db.close()
        
@app.delete("/documents/{document_id}")
def delete_document(
    document_id: int,
    current_user: User = Depends(get_current_user)
):
    db = SessionLocal()

    try:
        document = (
            db.query(Document)
            .filter(
                Document.id == document_id,
                Document.user_id == current_user.id
            )
            .first()
        )

        if not document:
            raise HTTPException(
                status_code=404,
                detail="Document not found."
            )

        file_path = document.file_path

        deleted_chunks = delete_document_chunks(
            document_id,
            current_user.id
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

    except HTTPException:
        raise

    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Failed to delete document."
        )

    finally:
        db.close()