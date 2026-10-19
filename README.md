# AI Document Intelligence & Enterprise Knowledge Assistant

## Project Overview

The AI Document Intelligence & Enterprise Knowledge Assistant is an AI-powered application that allows users to upload PDF documents and ask questions about their contents using natural language.

The system uses Retrieval-Augmented Generation (RAG) to retrieve relevant information from uploaded documents and generate concise answers with source references.

## Key Features

- Upload and process PDF documents.
- Extract text and split it into manageable chunks.
- Generate embeddings using Sentence Transformers.
- Store and retrieve document chunks using ChromaDB.
- Generate AI answers using the Groq LLM API.
- Display source documents and chunk references.
- Store document metadata and chat history in MySQL.
- Prevent duplicate PDF uploads using SHA-256 hashing.
- View and delete uploaded documents.
- View and delete chat history.
- Use an interactive Streamlit interface.
- Access backend APIs through FastAPI and Swagger UI.

## Technology Stack

| Component | Technology |
|---|---|
| Programming Language | Python |
| Frontend | Streamlit |
| Backend API | FastAPI |
| Relational Database | MySQL |
| Vector Database | ChromaDB |
| Embedding Model | all-MiniLM-L6-v2 |
| LLM Integration | Groq API |
| RAG Framework | LangChain |
| PDF Processing | pypdf |
| ORM | SQLAlchemy |

## Project Architecture

1. Users upload PDFs through the Streamlit interface.
2. The backend extracts text from the documents.
3. The extracted text is divided into chunks.
4. Sentence Transformers converts the chunks into embeddings.
5. ChromaDB stores the embeddings for semantic retrieval.
6. When a user asks a question, the system retrieves relevant document chunks.
7. The Groq LLM generates an answer using the retrieved information.
8. The application displays the answer and its source references.
9. MySQL stores document metadata and chat history.

## Project Structure

```text
AI Document Assistant/
├── backend/
│   ├── main.py
│   ├── agent.py
│   ├── rag.py
│   ├── llm.py
│   ├── vector_store.py
│   ├── document_processor.py
│   ├── database.py
│   ├── models.py
│   └── ingest_document.py
├── documents/
├── vectorstore/
├── app.py
├── requirements.txt
├── .env
└── README.md
```

## Setup Instructions

### 1. Clone or download the project

Open Anaconda Prompt or Command Prompt and navigate to the project directory.

```bat
cd /d "C:\AI Document Assistant"
```

### 2. Activate the Conda environment

```bat
conda activate aidoc
```

### 3. Install dependencies

```bat
pip install -r requirements.txt
```

### 4. Configure environment variables

Create or update the `.env` file in the project root.

```env
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=your_mysql_password
MYSQL_DATABASE=enterprise_ai
GROQ_API_KEY=your_groq_api_key
```

Replace the example values with your own credentials. Never publish your actual API key or database password.

### 5. Start MySQL

Ensure the MySQL service is running and that the `enterprise_ai` database and required tables are configured.

### 6. Start the FastAPI backend

Open a terminal and run:

```bat
conda activate aidoc
cd /d "C:\AI Document Assistant"
uvicorn backend.main:app --reload
```

API documentation:

http://127.0.0.1:8000/docs

### 7. Start the Streamlit frontend

Open a second terminal and run:

```bat
conda activate aidoc
cd /d "C:\AI Document Assistant"
streamlit run app.py
```

Open the local URL printed by Streamlit in your browser.

## Example Questions

- What are the working hours?
- What should employees do if they receive a suspicious email?
- Which project is mentioned in the uploaded résumé?
- Which certificates are listed in the document?

## Testing

The application has been tested with enterprise policy and résumé PDFs. Tests covered document retrieval, question answering, source references, document listing, and document management.

## Security Notes

- Keep `.env` private.
- Never commit API keys, database passwords, or personal documents to a public repository.
- Add `.env`, private PDFs, and generated database/vector-store files to `.gitignore` where appropriate.

## Future Improvements

- Improve retrieval relevance using similarity thresholds or reranking.
- Support additional document formats.
- Add user authentication and role-based access control.
- Improve source citations with page numbers.
- Add automated tests and deployment support.

## Author

Developed as an AI and document-intelligence project using Python, RAG, vector search, and large language models.