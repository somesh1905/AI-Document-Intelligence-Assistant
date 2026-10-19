import requests
import streamlit as st

API_URL = "http://127.0.0.1:8000"


st.set_page_config(
    page_title="AI Document Assistant",
    page_icon="🤖",
    layout="wide"
)

st.markdown(
    """
    <style>

    /* Main background */
    .stApp {
        background-color: #0e1117;
    }

    /* Sidebar */
    section[data-testid="stSidebar"] {
        background-color: #161b22;
    }

    /* Main title */
    .main-title {
        font-size: 38px;
        font-weight: 700;
        margin-bottom: 5px;
    }

    /* Subtitle */
    .subtitle {
        color: #9ca3af;
        font-size: 16px;
        margin-bottom: 30px;
    }

    /* Sidebar history title */
    .history-title {
        font-size: 20px;
        font-weight: 700;
        margin-top: 20px;
        margin-bottom: 15px;
    }

    </style>
    """,
    unsafe_allow_html=True
)


with st.sidebar:

    st.markdown(
        """
        <div style="font-size:28px;font-weight:700;">
            🤖 AI Document
        </div>

        <div style="font-size:28px;font-weight:700;">
            Assistant
        </div>

        <div style="color:#8b949e;margin-top:5px;">
            Enterprise Knowledge Assistant
        </div>
        """,
        unsafe_allow_html=True
    )

    st.divider()

    st.markdown("### 📄 Upload Document")

    uploaded_file = st.file_uploader(
        "Upload a PDF",
        type=["pdf"],
        label_visibility="collapsed"
    )

    if uploaded_file is not None:

        st.caption(
            f"📄 Selected: {uploaded_file.name}"
        )

        st.caption(
            f"📦 File size: "
            f"{uploaded_file.size / 1024:.1f} KB"
        )

        if st.button(
            "⬆️ Upload & Process",
            use_container_width=True
        ):

            status_box = st.empty()

            progress_bar = st.progress(0)

            status_box.info(
                "📤 Uploading document..."
            )

            progress_bar.progress(25)

            try:

                response = requests.post(
                    f"{API_URL}/upload",
                    files={
                        "file": (
                            uploaded_file.name,
                            uploaded_file,
                            "application/pdf"
                        )
                    },
                    timeout=120
                )

                progress_bar.progress(75)

                if response.status_code == 200:

                    result = response.json()

                    if result.get("status") == "success":

                        progress_bar.progress(100)

                        status_box.success(
                            "✅ Document processed successfully!"
                        )

                        st.markdown(
                            "### 📋 Processing Summary"
                        )

                        col1, col2 = st.columns(2)

                        with col1:

                            st.metric(
                                "📝 Characters",
                                result.get(
                                    "characters_extracted",
                                    0
                                )
                            )

                        with col2:

                            st.metric(
                                "🧩 Chunks",
                                result.get(
                                    "chunks_created",
                                    0
                                )
                            )

                        st.caption(
                            f"📄 {result.get('filename')}"
                        )

                        st.success(
                            "Your document is now available "
                            "for AI questions."
                        )

                    else:

                        progress_bar.empty()

                        status_box.error(
                            result.get(
                                "message",
                                "Document processing failed."
                            )
                        )

                else:

                    progress_bar.empty()

                    status_box.error(
                        f"Upload failed: "
                        f"{response.status_code}"
                    )

            except Exception as e:

                progress_bar.empty()

                status_box.error(
                    f"Connection error: {e}"
                )


    st.divider()

    st.markdown("### 📊 Document Dashboard")

    try:

        documents_response = requests.get(
            f"{API_URL}/documents",
            timeout=10
        )

        if documents_response.status_code == 200:

            documents_data = documents_response.json()

            documents = documents_data.get(
                "documents",
                []
            )

            document_count = len(documents)

            st.metric(
                "📚 Total Documents",
                document_count
            )

            st.caption(
                "🟢 Document system is online"
            )

            if not documents:

                st.caption(
                    "No documents uploaded yet."
                )

            else:

                for document in documents:

                    document_id = document.get(
                        "id"
                    )

                    filename = document.get(
                        "filename",
                        "Unknown document"
                    )

                    with st.expander(
                        f"📄 {filename}"
                    ):

                        st.caption(
                            f"Document ID: {document_id}"
                        )

                        if st.button(
                            "🗑️ Delete Document",
                            key=f"delete_document_{document_id}",
                            use_container_width=True
                        ):

                            try:

                                delete_response = requests.delete(
                                    f"{API_URL}/documents/{document_id}",
                                    timeout=30
                                )

                                if (
                                    delete_response.status_code
                                    == 200
                                ):

                                    delete_result = (
                                        delete_response.json()
                                    )

                                    if (
                                        delete_result.get(
                                            "status"
                                        )
                                        == "success"
                                    ):

                                        st.success(
                                            "Document deleted."
                                        )

                                        st.rerun()

                                    else:

                                        st.error(
                                            delete_result.get(
                                                "message",
                                                "Delete failed."
                                            )
                                        )

                                else:

                                    st.error(
                                        "Could not delete document."
                                    )

                            except Exception as e:

                                st.error(
                                    f"Delete error: {e}"
                                )

        else:

            st.error(
                "Could not load documents."
            )

    except Exception as e:

        st.error(
            f"Could not connect to document API: {e}"
        )


    st.divider()

    st.markdown(
        '<div class="history-title">'
        '💬 Chat History'
        '</div>',
        unsafe_allow_html=True
    )

    try:

        history_response = requests.get(
            f"{API_URL}/chat-history",
            timeout=10
        )

        if history_response.status_code == 200:

            history_data = history_response.json()

            chat_history = history_data.get(
                "chat_history",
                []
            )

            if not chat_history:

                st.caption(
                    "No chat history yet."
                )

            else:

                for chat in chat_history:

                    chat_id = chat.get(
                        "id"
                    )

                    question_text = chat.get(
                        "question",
                        ""
                    )

                    answer = chat.get(
                        "answer",
                        ""
                    )

                    created_at = chat.get(
                        "created_at",
                        ""
                    )

                    with st.expander(
                        f"💬 {question_text[:35]}"
                        + (
                            "..."
                            if len(question_text) > 35
                            else ""
                        )
                    ):

                        st.markdown(
                            "**Question**"
                        )

                        st.write(
                            question_text
                        )

                        st.markdown(
                            "**AI Answer**"
                        )

                        st.write(
                            answer
                        )

                        if created_at:

                            st.caption(
                                f"🕒 {created_at}"
                            )

                        if st.button(
                            "🗑️ Delete",
                            key=f"delete_chat_{chat_id}",
                            use_container_width=True
                        ):

                            try:

                                delete_response = requests.delete(
                                    f"{API_URL}/chat-history/{chat_id}",
                                    timeout=10
                                )

                                if (
                                    delete_response.status_code
                                    == 200
                                ):

                                    delete_result = (
                                        delete_response.json()
                                    )

                                    if (
                                        delete_result.get(
                                            "status"
                                        )
                                        == "success"
                                    ):

                                        st.success(
                                            "Chat deleted."
                                        )

                                        st.rerun()

                                    else:

                                        st.error(
                                            delete_result.get(
                                                "message",
                                                "Delete failed."
                                            )
                                        )

                                else:

                                    st.error(
                                        "Could not delete chat."
                                    )

                            except Exception as e:

                                st.error(
                                    f"Could not delete chat: {e}"
                                )

    except Exception as e:

        st.error(
            f"Could not load chat history: {e}"
        )


    st.divider()

    if st.button(
        "🧹 Clear Current Chat",
        use_container_width=True
    ):

        st.session_state.messages = []

        st.rerun()

st.markdown(
    '<div class="main-title">'
    '🤖 AI Document Assistant'
    '</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">'
    'Ask questions about your enterprise documents '
    'and get AI-powered answers with sources.'
    '</div>',
    unsafe_allow_html=True
)

if "messages" not in st.session_state:

    st.session_state.messages = []

for message in st.session_state.messages:

    with st.chat_message(
        message["role"]
    ):

        st.markdown(
            message["content"]
        )

        if (
            message["role"] == "assistant"
            and message.get("sources")
        ):

            st.markdown(
                "**📚 Sources**"
            )

            for source in message["sources"]:

                filename = source.get(
                    "filename",
                    "Unknown document"
                )

                chunk_index = source.get(
                    "chunk_index"
                )

                st.caption(
                    f"📄 {filename}  •  "
                    f"Chunk {chunk_index}"
                )

question = st.chat_input(
    "Ask a question about your documents..."
)

if question:

    st.session_state.messages.append(
        {
            "role": "user",
            "content": question
        }
    )

    with st.chat_message("user"):

        st.markdown(
            question
        )

    with st.chat_message("assistant"):

        with st.spinner(
            "Searching documents..."
        ):

            try:

                response = requests.post(
                    f"{API_URL}/ask",
                    json={
                        "question": question
                    },
                    timeout=120
                )

                if response.status_code == 200:

                    result = response.json()

                    if result.get(
                        "status"
                    ) == "error":

                        answer = result.get(
                            "message",
                            "Something went wrong."
                        )

                        sources = []

                    else:

                        answer = result.get(
                            "answer",
                            "No answer returned."
                        )

                        sources = result.get(
                            "sources",
                            []
                        )

                else:

                    answer = (
                        f"API Error: "
                        f"{response.status_code}"
                    )

                    sources = []

            except Exception as e:

                answer = (
                    "Could not connect to "
                    f"the AI server: {e}"
                )

                sources = []

        st.markdown(
            answer
        )

        if sources:

            st.markdown(
                "**📚 Sources**"
            )

            for source in sources:

                filename = source.get(
                    "filename",
                    "Unknown document"
                )

                chunk_index = source.get(
                    "chunk_index"
                )

                st.caption(
                    f"📄 {filename}  •  "
                    f"Chunk {chunk_index}"
                )


        st.session_state.messages.append(
            {
                "role": "assistant",
                "content": answer,
                "sources": sources
            }
        )

st.divider()

st.caption(
    "AI Document Intelligence & Enterprise Knowledge Assistant"
)