"""
MVP 3: AI Document Q&A / Compliance Assistant
-------------------------------------------------
Use case: Any industry with dense documents staff have to search manually —
Safety Data Sheets (chemical), medical protocols, insurance policies,
legal contracts, HR handbooks. Upload once, then ask questions in plain
language instead of Ctrl+F-ing a 40-page PDF.

Setup:
    pip install streamlit google-generativeai pdfplumber
    Get a free Gemini API key: https://ai.google.dev

Run:
    streamlit run mvp3_document_qa.py
"""

import streamlit as st
import os
import google.generativeai as genai
import pdfplumber

st.set_page_config(page_title="AI Document Q&A", page_icon="🔍", layout="centered")

st.title("🔍 AI Document Q&A Assistant")
st.caption("Upload a document (safety sheet, policy, contract, protocol) and ask it questions in plain language.")

with st.sidebar:
    st.header("Setup")
    # Loads from .streamlit/secrets.toml or env var if set, so you don't
    # need to paste it in every demo. Falls back to manual entry otherwise.
    default_key = ""
    try:
        default_key = st.secrets.get("GEMINI_API_KEY", "")
    except Exception:
        pass
    if not default_key:
        default_key = os.environ.get("GEMINI_API_KEY", "")

    api_key = st.text_input("Gemini API Key", value=default_key, type="password", help="Get a free key at ai.google.dev")
    st.markdown("---")
    st.markdown("**Example use cases:**\n- \"What's the max safe storage temperature for this chemical?\"\n- \"What does clause 4.2 of this contract say about termination?\"\n- \"What's the recommended dosage in this protocol?\"")

def extract_pdf_text(file):
    text = ""
    with pdfplumber.open(file) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    return text

if "doc_text" not in st.session_state:
    st.session_state.doc_text = None
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

uploaded_file = st.file_uploader("Upload a document (PDF)", type=["pdf"])

if uploaded_file:
    if st.button("Load Document"):
        with st.spinner("Reading document..."):
            st.session_state.doc_text = extract_pdf_text(uploaded_file)
            st.session_state.chat_history = []
        if st.session_state.doc_text.strip():
            st.success(f"Document loaded ({len(st.session_state.doc_text)} characters). Ask a question below.")
        else:
            st.error("Couldn't extract text — this may be a scanned/image PDF.")

if st.session_state.doc_text and api_key:
    for role, msg in st.session_state.chat_history:
        with st.chat_message(role):
            st.markdown(msg)

    question = st.chat_input("Ask a question about the document...")
    if question:
        st.session_state.chat_history.append(("user", question))
        with st.chat_message("user"):
            st.markdown(question)

        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-3.6-flash")

        prompt = f"""
You are a helpful assistant answering questions strictly based on the document below.
If the answer isn't in the document, say so clearly instead of guessing.

Document:
---
{st.session_state.doc_text[:20000]}
---

Question: {question}

Answer concisely and cite the relevant part of the document where possible.
"""
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response = model.generate_content(prompt)
                answer = response.text.strip()
                st.markdown(answer)
        st.session_state.chat_history.append(("assistant", answer))

elif st.session_state.doc_text and not api_key:
    st.warning("Please enter your Gemini API key in the sidebar first.")
