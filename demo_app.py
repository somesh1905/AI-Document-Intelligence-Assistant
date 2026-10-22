
import os
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv
from pypdf import PdfReader
from langchain_groq import ChatGroq

# Load local environment variables when running on your computer
load_dotenv()

st.set_page_config(
    page_title="AI Document Intelligence Assistant",
    page_icon="📚",
    layout="wide",
)

st.title("📚 AI Document Intelligence Assistant")
st.write(
    "Ask questions about the sample enterprise document "
    "and get AI-generated answers with source context."
)

PDF_PATH = (
    Path(__file__).parent
    / "demo_data"
    / "enterprise_ai_test_document.pdf"
)


@st.cache_data
def load_document(path):
    reader = PdfReader(str(path))
    pages = []

    for page_number, page in enumerate(reader.pages, start=1):
        text = page.extract_text() or ""
        if text.strip():
            pages.append(
                {
                    "page": page_number,
                    "text": text,
                }
            )

    return pages



def get_llm():
    api_key = os.getenv("GROQ_API_KEY")

    try:
        if not api_key:
            api_key = st.secrets.get("GROQ_API_KEY")
    except Exception:
        # Local secrets.toml may not exist yet.
        pass

    if not api_key:
        return None

    return ChatGroq(
        model="openai/gpt-oss-20b",
        temperature=0,
        groq_api_key=api_key,
    )



if not PDF_PATH.exists():
    st.error("The sample PDF could not be found.")
    st.stop()

try:
    pages = load_document(PDF_PATH)
except Exception as error:
    st.error(f"Could not read the sample PDF: {error}")
    st.stop()

if not pages:
    st.error("No readable text was found in the sample PDF.")
    st.stop()

with st.sidebar:
    st.header("Knowledge Base")
    st.success("Sample PDF loaded")
    st.write("**Document:** Enterprise AI Test Document")
    st.write(f"**Pages with text:** {len(pages)}")
    st.caption(
        "This public demo uses a fictional sample document. "
        "It does not access private company files."
    )

question = st.text_area(
    "Ask a question about the document",
    placeholder="Example: What are the working hours?",
    height=100,
)

if st.button("Generate Answer", type="primary"):
    if not question.strip():
        st.warning("Please enter a question first.")
    else:
        llm = get_llm()

        if llm is None:
            st.error(
                "The Groq API key is not configured. "
                "The app owner must add GROQ_API_KEY in "
                "the app's Streamlit Secrets settings."
            )
        else:
            with st.spinner("Searching the document and generating an answer..."):
                # Simple text-based retrieval for this small public demo.
                query_words = {
                    word.lower().strip(".,?!:;()")
                    for word in question.split()
                    if len(word) > 2
                }

                scored_pages = []

                for page in pages:
                    page_words = {
                        word.lower().strip(".,?!:;()")
                        for word in page["text"].split()
                    }
                    score = len(query_words & page_words)

                    if score > 0:
                        scored_pages.append((score, page))

                scored_pages.sort(
                    key=lambda item: item[0],
                    reverse=True,
                )

                selected_pages = [
                    page for _, page in scored_pages[:3]
                ]

                if not selected_pages:
                    selected_pages = pages[:3]

                context = "\n\n".join(
                    f"Source page {page['page']}:\n{page['text']}"
                    for page in selected_pages
                )

                prompt = f"""
You are an enterprise document assistant.
Answer the user's question using only the supplied document context.
If the answer is not available in the context, say that the document
does not provide enough information.
Do not invent policies, facts, or details.
Keep the answer clear and concise.

DOCUMENT CONTEXT:
{context}

USER QUESTION:
{question}

Provide the answer and mention the relevant source page number.
"""

                try:
                    answer = llm.invoke(prompt).content

                    st.subheader("Answer")
                    st.markdown(answer)

                    with st.expander("View source context"):
                        for page in selected_pages:
                            st.markdown(
                                f"**Source: Page {page['page']}**"
                            )
                            st.write(page["text"])

                except Exception as error:
                    st.error(
                        "The AI request failed. Please try again later."
                    )
                    st.caption(str(error))

with st.expander("About this demo"):
    st.write(
        "This is a lightweight public demonstration of document "
        "question answering. The full local project has a separate "
        "FastAPI backend, MySQL database, and ChromaDB vector store."
    )
