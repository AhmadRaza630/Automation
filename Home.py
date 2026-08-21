"""
Home Page — AI Automation MVP Suite
--------------------------------------
This is the entry point. Run only this file:
    streamlit run Home.py

Streamlit auto-detects everything inside the "pages" folder and adds it
to the sidebar navigation + this home page links to each one directly.
"""

import streamlit as st

st.set_page_config(page_title="AI Automation Suite", page_icon="🤖", layout="centered")

st.title("🤖 AI Automation MVP Suite")
st.caption("Pick a tool below. Each one runs inside this same app — no separate commands needed.")

st.markdown("---")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("### 📄")
    st.markdown("**Document Extractor**")
    st.markdown("Turn invoices, lab reports, or purchase orders into clean structured data (Excel).")
    st.page_link("pages/1_Document_Extractor.py", label="Open Tool →", icon="📄")

with col2:
    st.markdown("### 💬")
    st.markdown("**Reminder Generator**")
    st.markdown("Turn a customer/patient list into personalized WhatsApp, SMS, or Email reminders.")
    st.page_link("pages/2_Reminder_Generator.py", label="Open Tool →", icon="💬")

with col3:
    st.markdown("### 🔍")
    st.markdown("**Document Q&A**")
    st.markdown("Upload any document (safety sheet, contract, policy) and ask it questions directly.")
    st.page_link("pages/3_Document_QA.py", label="Open Tool →", icon="🔍")

st.markdown("---")
st.info("💡 Tip: You can also switch between tools anytime using the sidebar on the left.")
