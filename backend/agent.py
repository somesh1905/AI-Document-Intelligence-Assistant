from backend.vector_store import search_documents
from backend.database import SessionLocal
from backend.models import Document, ChatHistory
from backend.llm import generate_response

def document_search_tool(query):
    """
    Search enterprise documents and return the
    most relevant document chunks with clean sources.
    """

    results = search_documents(query, top_k=10)

    documents = results.get("documents", [[]])[0]
    metadatas = results.get("metadatas", [[]])[0]
    distances = results.get("distances", [[]])[0]

    if not documents:
        return {
            "status": "no_results",
            "message": "No relevant documents found."
        }

    retrieved_chunks = []

    for i, document in enumerate(documents):
        metadata = metadatas[i] if i < len(metadatas) else {}
        distance = distances[i] if i < len(distances) else None

        retrieved_chunks.append({
            "content": document,
            "filename": metadata.get("filename", "Unknown document"),
            "document_id": metadata.get("document_id"),
            "chunk_index": metadata.get("chunk_index"),
            "distance": distance
        })

    retrieved_chunks.sort(
        key=lambda item: (
            item["distance"]
            if item["distance"] is not None
            else float("inf")
        )
    )

    best_chunk = retrieved_chunks[0]
    best_document_id = best_chunk["document_id"]

    relevant_chunks = [
        item for item in retrieved_chunks
        if item["document_id"] == best_document_id
    ]

    sources = []
    seen_chunks = set()

    for item in relevant_chunks:
        key = (
            item["document_id"],
            item["chunk_index"],
            item["content"].strip()
        )

        if key in seen_chunks:
            continue

        seen_chunks.add(key)

        sources.append({
            "content": item["content"],
            "filename": item["filename"],
            "document_id": item["document_id"],
            "chunk_index": item["chunk_index"]
        })

        if len(sources) >= 3:
            break

    if not sources:
        return {
            "status": "no_results",
            "message": "No relevant documents found."
        }

    return {
        "status": "success",
        "results": sources
    }


def document_list_tool():
    """
    Get all uploaded documents from MySQL.
    """

    db = SessionLocal()

    try:

        documents = (
            db.query(Document)
            .order_by(
                Document.uploaded_at.desc()
            )
            .all()
        )

        if not documents:

            return {
                "status": "no_documents",
                "message": "No documents are uploaded."
            }

        document_list = []

        for document in documents:

            document_list.append(
                {
                    "document_id": document.id,
                    "filename": document.filename,
                    "uploaded_at": str(
                        document.uploaded_at
                    )
                }
            )

        return {
            "status": "success",
            "count": len(document_list),
            "documents": document_list
        }

    except Exception as e:

        return {
            "status": "error",
            "message": str(e)
        }

    finally:

        db.close()

def chat_history_tool(limit=10):
    """
    Get recent questions and answers from MySQL.
    """

    db = SessionLocal()

    try:

        chats = (
            db.query(ChatHistory)
            .order_by(
                ChatHistory.created_at.desc()
            )
            .limit(limit)
            .all()
        )

        if not chats:

            return {
                "status": "no_history",
                "message": "No chat history found."
            }

        history = []

        for chat in chats:

            history.append(
                {
                    "chat_id": chat.id,
                    "question": chat.question,
                    "answer": chat.answer,
                    "created_at": str(
                        chat.created_at
                    )
                }
            )

        return {
            "status": "success",
            "count": len(history),
            "chat_history": history
        }

    except Exception as e:

        return {
            "status": "error",
            "message": str(e)
        }

    finally:

        db.close()

def decide_tool(question):
    """
    Ask the LLM which tool should be used
    for the user's question.
    """

    prompt = f"""
You are an AI agent for an enterprise document assistant.

You have three tools:

1. document_search
   Use this when the user asks about information
   contained in enterprise documents.

2. document_list
   Use this when the user asks which documents
   are uploaded or available.

3. chat_history
   Use this when the user asks about previous
   questions, previous answers, or conversation history.

Choose exactly ONE tool.

Return ONLY one of these values:

document_search
document_list
chat_history

User Question:
{question}

Tool:
"""

    decision = generate_response(prompt)

    decision = decision.strip().lower()

    if "document_list" in decision:
        return "document_list"

    if "chat_history" in decision:
        return "chat_history"

    return "document_search"


def run_agent(question):
    """
    Let the AI Agent choose a tool,
    execute it, and generate a final answer.
    """

    selected_tool = decide_tool(
        question
    )

    if selected_tool == "document_search":

        tool_result = document_search_tool(
            question
        )

    elif selected_tool == "document_list":

        tool_result = document_list_tool()

    elif selected_tool == "chat_history":

        tool_result = chat_history_tool()

    else:

        return {
            "status": "error",
            "message": "Unknown tool selected."
        }

    prompt = f"""
You are an enterprise AI assistant.

Answer the user's question using ONLY
the information returned by the selected tool.

Do not invent information.

Keep the answer clear, professional,
and concise.

User Question:
{question}

Selected Tool:
{selected_tool}

Tool Result:
{tool_result}

Generate the final answer for the user.
"""

    answer = generate_response(
        prompt
    )

    sources = []

    if selected_tool == "document_search":

        results = tool_result.get(
            "results",
            []
        )

        for result in results:

            sources.append(
                {
                    "filename": result.get(
                        "filename",
                        "Unknown document"
                    ),
                    "document_id": result.get(
                        "document_id"
                    ),
                    "chunk_index": result.get(
                        "chunk_index"
                    )
                }
            )

    return {
        "status": "success",
        "answer": answer,
        "selected_tool": selected_tool,
        "sources": sources
    }

if __name__ == "__main__":

    print("Testing AI Agent Tools...")
    print("========================================")

    print("\n1. Testing Document Search Tool")
    print("----------------------------------------")

    question = "What are the working hours?"

    result = document_search_tool(
        question
    )

    print("\nSearch Question:")
    print(question)

    print("\nSearch Result:")
    print(result)

    print("\n\n2. Testing Document List Tool")
    print("----------------------------------------")

    documents = document_list_tool()

    print("\nDocument List:")
    print(documents)

    print("\n\n3. Testing Chat History Tool")
    print("----------------------------------------")

    history = chat_history_tool()

    print("\nChat History:")
    print(history)
    

    print("\nAI Agent tools test completed!")
    
    print("\n\n4. Testing AI Agent Decision Making")
    print("----------------------------------------")

    test_questions = [
        "What are the working hours?",
        "What documents are uploaded?",
        "What did I ask previously?"
    ]

    for question in test_questions:

        decision = decide_tool(
            question
        )

        print("\nQuestion:")
        print(question)

        print("Selected Tool:")
        print(decision)

    print("\nAI Agent decision test completed!")

    print("\n\n5. Testing Complete AI Agent")
    print("----------------------------------------")

    agent_question = "What are the working hours?"

    agent_result = run_agent(
        agent_question
    )

    print("\nUser Question:")
    print(agent_question)

    print("\nAI Agent Answer:")
    print("----------------------------------------")
    print(agent_result.get("answer"))

    print("\nSelected Tool:")
    print(agent_result.get("selected_tool"))

    print("\nSources:")
    print(agent_result.get("sources"))

    print("\nComplete AI Agent test completed!")