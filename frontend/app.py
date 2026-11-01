import base64
import requests
import streamlit as st
import uuid


# -----------------------------------
# PAGE CONFIGURATION
# -----------------------------------

st.set_page_config(
    page_title="AI Document Assistant",
    page_icon="🤖",
    layout="wide"
)


# -----------------------------------
# API CONFIGURATION
# -----------------------------------

# Use this URL when testing your LOCAL backend.
API_URL = "https://ai-document-assistant-api-v2.onrender.com"

# For deployed backend, use:
# API_URL = "https://ai-document-assistant-api-v2.onrender.com"


# -----------------------------------
# SESSION INITIALIZATION
# -----------------------------------

if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

if "access_token" not in st.session_state:
    st.session_state.access_token = None

if "user" not in st.session_state:
    st.session_state.user = None

if "messages" not in st.session_state:
    st.session_state.messages = []

SESSION_ID = st.session_state.session_id


# -----------------------------------
# AUTHENTICATION HEADERS
# -----------------------------------

def get_auth_headers():

    token = st.session_state.get("access_token")

    if not token:
        return {}

    return {
        "Authorization": f"Bearer {token}"
    }


# -----------------------------------
# CSS DESIGN
# -----------------------------------

st.markdown(
    """
    <style>

    .stApp {
        background-color: #0e1117;
    }

    section[data-testid="stSidebar"] {
        background-color: #161b22;
    }

    .main-title {
        font-size: 38px;
        font-weight: 700;
        margin-bottom: 5px;
    }

    .subtitle {
        color: #9ca3af;
        font-size: 16px;
        margin-bottom: 30px;
    }

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


# -----------------------------------
# LOGIN AND REGISTRATION
# -----------------------------------

if not st.session_state.access_token:

    st.markdown(
        "<h1 style='text-align:center;'>"
        "🤖 AI Document Assistant"
        "</h1>",
        unsafe_allow_html=True
    )

    st.markdown(
        "<p style='text-align:center;color:#9ca3af;font-size:16px;'>"
        "Enterprise Knowledge Assistant"
        "</p>",
        unsafe_allow_html=True
    )

    st.write("")

    col1, col2, col3 = st.columns([1, 1.5, 1])

    with col2:

        login_tab, register_tab = st.tabs(
            ["Login", "Register"]
        )

        # -----------------------------------
        # LOGIN
        # -----------------------------------

        with login_tab:

            st.subheader("Welcome Back")

            login_email = st.text_input(
                "Email",
                key="login_email"
            )

            login_password = st.text_input(
                "Password",
                type="password",
                key="login_password"
            )

            if st.button(
                "Login",
                use_container_width=True
            ):

                if not login_email or not login_password:

                    st.warning(
                        "Please enter your email and password."
                    )

                else:

                    try:

                        response = requests.post(
                            f"{API_URL}/login",
                            json={
                                "email": login_email,
                                "password": login_password
                            },
                            timeout=30
                        )

                        if response.status_code == 200:

                            result = response.json()

                            st.session_state.access_token = (
                                result["access_token"]
                            )

                            st.session_state.user = (
                                result["user"]
                            )

                            st.session_state.messages = []

                            st.success(
                                "Login successful!"
                            )

                            st.rerun()

                        else:

                            try:
                                error = response.json().get(
                                    "detail",
                                    "Login failed."
                                )
                            except ValueError:
                                error = "Login failed."

                            st.error(error)

                    except requests.RequestException:

                        st.error(
                            "Could not connect to the backend server."
                        )

        # -----------------------------------
        # REGISTRATION
        # -----------------------------------

        with register_tab:

            st.subheader("Create Account")

            register_name = st.text_input(
                "Full Name",
                key="register_name"
            )

            register_email = st.text_input(
                "Email",
                key="register_email"
            )

            register_password = st.text_input(
                "Password (minimum 8 characters)",
                type="password",
                key="register_password"
            )

            if st.button(
                "Create Account",
                use_container_width=True
            ):

                if not register_name.strip():

                    st.warning(
                        "Please enter your name."
                    )

                elif not register_email.strip():

                    st.warning(
                        "Please enter your email."
                    )

                elif len(register_password) < 8:

                    st.warning(
                        "Password must contain at least 8 characters."
                    )

                else:

                    try:

                        response = requests.post(
                            f"{API_URL}/register",
                            json={
                                "name": register_name,
                                "email": register_email,
                                "password": register_password
                            },
                            timeout=30
                        )

                        if response.status_code == 200:

                            st.success(
                                "Account created successfully! "
                                "Please log in."
                            )

                        else:

                            try:
                                error = response.json().get(
                                    "detail",
                                    "Registration failed."
                                )
                            except ValueError:
                                error = "Registration failed."

                            st.error(error)

                    except requests.RequestException:

                        st.error(
                            "Could not connect to the backend server."
                        )

    # Stop dashboard from appearing before login
    st.stop()


# -----------------------------------
# SIDEBAR
# -----------------------------------

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

    # -----------------------------------
    # USER ACCOUNT
    # -----------------------------------

    current_user = st.session_state.get("user")

    if current_user:

        st.markdown("### 👤 Account")

        st.write(
            f"Welcome, **{current_user.get('name', 'User')}**"
        )

        st.caption(
            current_user.get("email", "")
        )

    if st.button(
        "🚪 Logout",
        use_container_width=True
    ):

        st.session_state.access_token = None
        st.session_state.user = None
        st.session_state.messages = []

        st.rerun()

    st.divider()
    # -----------------------------------
    # DOCUMENT DASHBOARD
    # -----------------------------------

    st.markdown("### 📊 Document Dashboard")
    
    
    # -----------------------------------
    # UPLOAD DOCUMENT
    # -----------------------------------

    st.markdown("#### 📤 Upload New Document")

    uploaded_file = st.file_uploader(
        "Choose a PDF document",
        type=["pdf"],
        key="document_uploader"
    )

    if st.button(
        "Upload Document",
        use_container_width=True,
        disabled=uploaded_file is None
    ):

        try:
            with st.spinner("Uploading and processing your PDF..."):

                upload_response = requests.post(
                    f"{API_URL}/upload",
                    headers=get_auth_headers(),
                    files={
                        "file": (
                            uploaded_file.name,
                            uploaded_file.getvalue(),
                            "application/pdf"
                        )
                    },
                    timeout=120
                )

            if upload_response.status_code in (200, 201):

                st.success("Document uploaded successfully!")

                st.json(upload_response.json())

                st.rerun()

            elif upload_response.status_code == 401:

                st.error("Session expired. Please log in again.")

                st.session_state.access_token = None
                st.session_state.user = None

                st.rerun()

            else:

                try:
                    error = upload_response.json().get(
                        "detail",
                        "Document upload failed."
                    )
                except ValueError:
                    error = "Document upload failed."

                st.error(error)

        except requests.RequestException as e:

            st.error(f"Could not connect to the server: {e}")


    try:

        documents_response = requests.get(
            f"{API_URL}/documents",
            headers=get_auth_headers(),
            timeout=15
        )

        if documents_response.status_code == 200:

            documents_data = documents_response.json()

            documents = documents_data.get(
                "documents",
                []
            )

            st.metric(
                "📚 Total Documents",
                len(documents)
            )

            st.caption("🟢 Document system is online")

            if not documents:

                st.caption("No documents uploaded yet.")

            else:

                for document in documents:

                    document_id = document.get("id")

                    filename = document.get(
                        "filename",
                        "Unknown document"
                    )

                    with st.expander(f"📄 {filename}"):

                        st.caption(
                            f"Document ID: {document_id}"
                        )

                        # VIEW PDF BUTTON
                        if st.button(
                            "👁️ View PDF",
                            key=f"view_document_{document_id}",
                            use_container_width=True
                        ):

                            try:

                                pdf_response = requests.get(
                                    f"{API_URL}/documents/{document_id}/view",
                                    headers=get_auth_headers(),
                                    timeout=30
                                )

                                if pdf_response.status_code == 200:

                                    st.session_state[
                                        f"pdf_data_{document_id}"
                                    ] = pdf_response.content

                                elif pdf_response.status_code == 401:

                                    st.error(
                                        "Session expired. Please log in again."
                                    )

                                    st.session_state.access_token = None
                                    st.session_state.user = None

                                    st.rerun()

                                else:

                                    st.error(
                                        "Could not open this PDF."
                                    )

                            except requests.RequestException:

                                st.error(
                                    "Could not connect to the document server."
                                )

                        # PDF PREVIEW
                        pdf_data = st.session_state.get(
                            f"pdf_data_{document_id}"
                        )

                        if pdf_data:

                            st.markdown("**📖 PDF Preview**")

                            st.download_button(
                                "⬇️ Download PDF",
                                data=pdf_data,
                                file_name=filename,
                                mime="application/pdf",
                                key=f"download_pdf_{document_id}",
                                use_container_width=True
                            )

                            pdf_base64 = base64.b64encode(pdf_data).decode("utf-8")

                            pdf_html = f"""
                            <div id="pdf-container" style="width:100%;"></div>

                            <script src="https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.min.js"></script>

                            <script>
                            (async function() {{
                                const container = document.getElementById("pdf-container");
                                container.innerHTML = "Loading PDF...";

                                try {{
                                     const base64Data = "{pdf_base64}";
                                    const binary = atob(base64Data);
                                    const bytes = new Uint8Array(binary.length);

                                     for (let i = 0; i < binary.length; i++) {{
                                      bytes[i] = binary.charCodeAt(i);
                                }}

                                const pdf = await pdfjsLib.getDocument({{
                                      data: bytes,
                                      disableWorker: true
                                }}).promise;

                                container.innerHTML = "";

                              for (let pageNumber = 1; pageNumber <= pdf.numPages; pageNumber++) {{
                                      const page = await pdf.getPage(pageNumber);
                                      const viewport = page.getViewport({{ scale: 1.2 }});

                                      const canvas = document.createElement("canvas");
                                      const context = canvas.getContext("2d");

                                      canvas.width = viewport.width;
                                    canvas.height = viewport.height;
                                    canvas.style.width = "100%";
                                    canvas.style.height = "auto";
                                    canvas.style.marginBottom = "15px";

                                    container.appendChild(canvas);

                                    await page.render({{
                                    canvasContext: context,
                                    viewport: viewport
                                       }}).promise;
                                       }}
                                       }} catch (error) {{
                                       container.innerHTML = "Unable to preview PDF: " + error.message;
                                       }}
                                 }})();
                                 </script>
                                 """

                            st.components.v1.html(pdf_html, height=650, scrolling=True)

                        st.divider()

                        # DELETE DOCUMENT
                        if st.button(
                            "🗑️ Delete Document",
                            key=f"delete_document_{document_id}",
                            use_container_width=True
                        ):

                            try:

                                delete_response = requests.delete(
                                    f"{API_URL}/documents/{document_id}",
                                    headers=get_auth_headers(),
                                    timeout=30
                                )

                                if delete_response.status_code == 200:

                                    st.success("Document deleted.")

                                    st.session_state.pop(
                                        f"pdf_data_{document_id}",
                                        None
                                    )

                                    st.rerun()

                                elif delete_response.status_code == 401:

                                    st.error(
                                        "Session expired. Please log in again."
                                    )

                                    st.session_state.access_token = None
                                    st.session_state.user = None

                                    st.rerun()

                                else:

                                    st.error(
                                        "Could not delete document."
                                    )

                            except requests.RequestException:

                                st.error(
                                    "Could not connect to the server."
                                )

        elif documents_response.status_code == 401:

            st.error(
                "Your session has expired. Please log in again."
            )

            st.session_state.access_token = None
            st.session_state.user = None

            st.rerun()

        else:

            st.error("Could not load documents.")

    except requests.RequestException:

        st.error("Could not connect to document API.")



    st.divider()

    # -----------------------------------
    # CHAT HISTORY
    # -----------------------------------

    st.markdown(
        '<div class="history-title">'
        '💬 Chat History'
        '</div>',
        unsafe_allow_html=True
    )

    try:

        history_response = requests.get(
            f"{API_URL}/chat-history",
            headers=get_auth_headers(),
            timeout=15
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

                    chat_id = chat.get("id")

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

                        st.markdown("**Question**")
                        st.write(question_text)

                        st.markdown("**AI Answer**")
                        st.write(answer)

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
                                    headers=get_auth_headers(),
                                    timeout=15
                                )

                                if delete_response.status_code == 200:

                                    st.success("Chat deleted.")
                                    st.rerun()

                                elif delete_response.status_code == 401:

                                    st.error(
                                        "Session expired. Please log in again."
                                    )

                                    st.session_state.access_token = None
                                    st.session_state.user = None

                                    st.rerun()

                                else:

                                    st.error(
                                        "Could not delete chat."
                                    )

                            except requests.RequestException:

                                st.error(
                                    "Could not connect to the server."
                                )

        elif history_response.status_code == 401:

            st.error(
                "Your session has expired. Please log in again."
            )

            st.session_state.access_token = None
            st.session_state.user = None

            st.rerun()

        else:

            st.error(
                "Could not load chat history."
            )

    except requests.RequestException:

        st.error(
            "Could not connect to chat history API."
        )


    st.divider()

    # -----------------------------------
    # CLEAR CURRENT CHAT
    # -----------------------------------

    if st.button(
        "🧹 Clear Current Chat",
        use_container_width=True
    ):

        st.session_state.messages = []

        st.rerun()


# -----------------------------------
# MAIN PAGE
# -----------------------------------

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


# -----------------------------------
# DISPLAY CHAT MESSAGES
# -----------------------------------

for message in st.session_state.messages:

    with st.chat_message(message["role"]):

        st.markdown(message["content"])

        if (
            message["role"] == "assistant"
            and message.get("sources")
        ):

            st.markdown("**📚 Sources**")

            for source in message["sources"]:

                filename = source.get(
                    "filename",
                    "Unknown document"
                )

                chunk_index = source.get("chunk_index")

                st.caption(
                    f"📄 {filename} • Chunk {chunk_index}"
                )


# -----------------------------------
# ASK QUESTION
# -----------------------------------

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

        st.markdown(question)

    with st.chat_message("assistant"):

        with st.spinner("Searching documents..."):

            try:

                response = requests.post(
                    f"{API_URL}/ask",
                    json={
                        "question": question
                    },
                    headers=get_auth_headers(),
                    timeout=120
                )

                if response.status_code in (200, 201):

                    result = response.json()

                    if result.get("status") == "error":

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

                elif response.status_code == 401:

                    answer = (
                        "Your session has expired. "
                        "Please log in again."
                    )

                    sources = []

                    st.session_state.access_token = None
                    st.session_state.user = None

                else:

                    answer = (
                        f"API Error: {response.status_code}"
                    )

                    sources = []

            except requests.RequestException:

                answer = (
                    "Could not connect to the AI server."
                )

                sources = []

        st.markdown(answer)

        if sources:

            st.markdown("**📚 Sources**")

            for source in sources:

                filename = source.get(
                    "filename",
                    "Unknown document"
                )

                chunk_index = source.get("chunk_index")

                st.caption(
                    f"📄 {filename} • Chunk {chunk_index}"
                )

        st.session_state.messages.append(
            {
                "role": "assistant",
                "content": answer,
                "sources": sources
            }
        )

        if not st.session_state.access_token:
            st.rerun()


# -----------------------------------
# FOOTER
# -----------------------------------

st.divider()

st.caption(
    "AI Document Intelligence & Enterprise Knowledge Assistant"
)