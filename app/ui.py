import streamlit as st
import requests

API_BASE_URL = "http://127.0.0.1:8000/api/v1"
st.set_page_config(page_title="Synthetix Academy", page_icon="🧠", layout="wide")

# Initialize Session State
if "document_id" not in st.session_state:
    st.session_state.document_id = None
if "doc_title" not in st.session_state:
    st.session_state.doc_title = ""
if "summary_data" not in st.session_state:
    st.session_state.summary_data = None
if "recommendations" not in st.session_state:
    st.session_state.recommendations = None
if "quiz_data" not in st.session_state:
    st.session_state.quiz_data = None
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

st.title("Synthetix Academy")

# --- SIDEBAR: INGESTION ---
with st.sidebar:
    st.header("1. Upload Content")
    
    # File Upload
    uploaded_file = st.file_uploader("Upload a PDF file", type=["pdf", "txt"])
    if st.button("Process Document") and uploaded_file:
        with st.spinner("Extracting text..."):
            files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
            res = requests.post(f"{API_BASE_URL}/ingest/file", files=files)
            if res.status_code == 200:
                st.session_state.document_id = res.json().get("document_id")
                st.session_state.doc_title = res.json().get("title")
                st.success(f"Indexed: {st.session_state.doc_title}")
                # Reset previous data
                st.session_state.summary_data = None
                st.session_state.quiz_data = None
                st.session_state.chat_history = []
    
    st.divider()
    
    # YouTube Upload
    youtube_url = st.text_input("Or paste a YouTube URL:")
    if st.button("Process Video") and youtube_url:
        with st.spinner("Downloading audio and transcribing via Whisper... (This may take a minute)"):
            res = requests.post(f"{API_BASE_URL}/ingest/url", json={"url": youtube_url})
            if res.status_code == 200:
                st.session_state.document_id = res.json().get("document_id")
                st.session_state.doc_title = res.json().get("title")
                st.success(f"Transcribed: {st.session_state.doc_title}")
                # Reset previous data
                st.session_state.summary_data = None
                st.session_state.quiz_data = None
                st.session_state.chat_history = []

# --- MAIN AREA ---
if st.session_state.document_id:
    st.subheader(f"Current Material: {st.session_state.doc_title}")
    
    col1, col2 = st.columns([1.5, 1])
    
    # Left Column: Summary & Links
    with col1:
        if st.button("Generate Summary & Resources"):
            with st.spinner("Analyzing content..."):
                sum_res = requests.post(f"{API_BASE_URL}/summarize/{st.session_state.document_id}")
                if sum_res.status_code == 200:
                    st.session_state.summary_data = sum_res.json().get("result")
                
                rec_res = requests.get(f"{API_BASE_URL}/recommend/{st.session_state.document_id}")
                if rec_res.status_code == 200:
                    st.session_state.recommendations = rec_res.json().get("recommendations", [])
        
        if st.session_state.summary_data:
            st.info("### 📝 AI Summary")
            st.markdown(st.session_state.summary_data)
            
        if st.session_state.recommendations:
            st.success("### 📺 Recommended Video Searches")
            for rec in st.session_state.recommendations:
                st.markdown(f"- [{rec['title']}]({rec['url']})")

    # Right Column: Quiz
    with col2:
        if st.button("Generate Quiz"):
            with st.spinner("Crafting questions..."):
                res = requests.post(f"{API_BASE_URL}/quiz/generate/{st.session_state.document_id}")
                if res.status_code == 200:
                    quiz_payload = res.json().get("quiz", {})
                    if isinstance(quiz_payload, dict) and "questions" in quiz_payload:
                        st.session_state.quiz_data = quiz_payload["questions"]
                    elif isinstance(quiz_payload, list):
                        st.session_state.quiz_data = quiz_payload
        
        if st.session_state.quiz_data:
            with st.form("quiz_form"):
                user_answers = {}
                for idx, q in enumerate(st.session_state.quiz_data):
                    st.write(f"**Q{idx+1}: {q.get('question')}**")
                    options = q.get('options', ['A', 'B', 'C', 'D'])
                    user_answers[idx] = st.radio("Select an answer:", options, key=f"q_{idx}")
                    st.divider()
                
                if st.form_submit_button("Submit Answers"):
                    for idx, q in enumerate(st.session_state.quiz_data):
                        if user_answers[idx] == q.get('correct_answer'):
                            st.success(f"Q{idx+1}: Correct!")
                        else:
                            st.error(f"Q{idx+1}: Incorrect. Answer was: {q.get('correct_answer')}")

    st.divider()
    
    # --- CHATBOT INTERFACE ---
    st.header("💬 Study Assistant")
    st.markdown("Ask questions directly about the material.")
    
    # Display chat history
    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            
    # Chat Input
    if user_query := st.chat_input("Ask a question..."):
        # Add user message to UI
        st.session_state.chat_history.append({"role": "user", "content": user_query})
        with st.chat_message("user"):
            st.markdown(user_query)
            
        # Call Backend
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                res = requests.post(
                    f"{API_BASE_URL}/chat/{st.session_state.document_id}", 
                    json={"message": user_query}
                )
                if res.status_code == 200:
                    reply = res.json().get("reply")
                    st.markdown(reply)
                    st.session_state.chat_history.append({"role": "assistant", "content": reply})
                else:
                    st.error("Error communicating with AI.")