"""
MVP 1: AI Document Data Extractor
----------------------------------
Use case: Medical labs, clinics, chemical suppliers, or any business that
manually copies data from PDFs (invoices, lab reports, purchase orders,
safety sheets) into spreadsheets. This tool automates that.

Setup:
    pip install streamlit google-generativeai pdfplumber pandas openpyxl
    Get a free Gemini API key: https://ai.google.dev

Run:
    streamlit run mvp1_document_extractor.py
"""

import streamlit as st
import os
import google.generativeai as genai
import pdfplumber
import pandas as pd
import json
import io

st.set_page_config(page_title="AI Document Extractor", page_icon="📄", layout="centered")

st.title("📄 AI Document Data Extractor")
st.caption("Upload a PDF (invoice, lab report, purchase order, etc.) and get clean structured data — no manual typing.")

# --- API Key input ---
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
    st.markdown("**Example use cases:**\n- Medical lab reports → patient + test data\n- Chemical supplier invoices → item, quantity, price\n- Purchase orders → vendor, items, totals")

def extract_pdf_text(file):
    text = ""
    with pdfplumber.open(file) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    return text

def ai_structure_data(raw_text, api_key, fields_hint):
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-3.6-flash")

    prompt = f"""
You are a data extraction engine. Extract structured data from the document text below.

If the user gave a hint about which fields to extract, use it: "{fields_hint or 'auto-detect the most relevant fields'}"

Return ONLY a valid JSON array of objects (no markdown, no explanation, no code fences).
Each object should represent one row of extracted data (e.g. one line item, one record).
If the document has only one record, return an array with a single object.

Document text:
---
{raw_text[:15000]}
---
"""
    response = model.generate_content(prompt)
    cleaned = response.text.strip().replace("```json", "").replace("```", "").strip()
    return json.loads(cleaned)

uploaded_file = st.file_uploader("Upload a PDF document", type=["pdf"])
fields_hint = st.text_input("What data do you want extracted? (optional)",
                             placeholder="e.g. patient name, test name, result, date")

if uploaded_file and api_key:
    if st.button("Extract Data", type="primary"):
        with st.spinner("Reading document..."):
            raw_text = extract_pdf_text(uploaded_file)

        if not raw_text.strip():
            st.error("Couldn't read text from this PDF. It may be a scanned image — OCR support can be added.")
        else:
            with st.spinner("AI is structuring the data..."):
                try:
                    data = ai_structure_data(raw_text, api_key, fields_hint)
                    df = pd.DataFrame(data)
                    st.success(f"Extracted {len(df)} record(s)!")
                    st.dataframe(df, use_container_width=True)

                    # Download as Excel
                    buffer = io.BytesIO()
                    df.to_excel(buffer, index=False, engine="openpyxl")
                    buffer.seek(0)
                    st.download_button(
                        "⬇️ Download as Excel",
                        data=buffer,
                        file_name="extracted_data.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )
                except Exception as e:
                    st.error(f"Something went wrong: {e}")
elif uploaded_file and not api_key:
    st.warning("Please enter your Gemini API key in the sidebar first.")
