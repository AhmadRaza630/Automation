"""
MVP 2: AI Reminder & Follow-up Generator
------------------------------------------
Use case: Clinics, salons, chemical suppliers, any service business that
manually calls/texts customers for appointment reminders or follow-ups.
Upload a CSV of customers -> get personalized, ready-to-send messages.

Setup:
    pip install streamlit google-generativeai pandas openpyxl
    Get a free Gemini API key: https://ai.google.dev

Run:
    streamlit run mvp2_reminder_generator.py

Expected CSV columns (flexible - AI adapts to whatever you upload):
    name, appointment_date, purpose  (or similar)
"""

import streamlit as st
import os
import google.generativeai as genai
import pandas as pd
import io

st.set_page_config(page_title="AI Reminder Generator", page_icon="💬", layout="centered")

st.title("💬 AI Reminder & Follow-up Generator")
st.caption("Upload a customer/patient list — get personalized reminder messages ready to send via WhatsApp, SMS, or email.")

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
    channel = st.selectbox("Message channel", ["WhatsApp", "SMS", "Email"])
    tone = st.selectbox("Tone", ["Friendly", "Professional", "Urgent (missed payment/appointment)"])
    business_name = st.text_input("Business/Clinic name", value="Your Clinic")

st.markdown("**CSV should have columns like:** `name`, `date`, `purpose` (any names work — AI figures it out)")

uploaded_csv = st.file_uploader("Upload customer list (CSV)", type=["csv"])

if uploaded_csv:
    df = pd.read_csv(uploaded_csv)
    st.write("Preview:")
    st.dataframe(df.head(), use_container_width=True)

    if api_key and st.button("Generate Reminders", type="primary"):
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-3.6-flash")

        messages = []
        progress = st.progress(0, text="Generating messages...")

        for i, row in df.iterrows():
            row_data = row.to_dict()
            prompt = f"""
Write a short {tone.lower()} {channel} reminder message from "{business_name}" to a customer.
Customer details: {row_data}
Keep it under 40 words, natural, and include their name if available.
Return ONLY the message text, nothing else.
"""
            try:
                response = model.generate_content(prompt)
                msg = response.text.strip()
            except Exception as e:
                msg = f"Error generating message: {e}"

            messages.append(msg)
            progress.progress((i + 1) / len(df), text=f"Generated {i+1}/{len(df)}")

        df["generated_message"] = messages
        st.success("Done! Messages generated below.")
        st.dataframe(df, use_container_width=True)

        buffer = io.BytesIO()
        df.to_excel(buffer, index=False, engine="openpyxl")
        buffer.seek(0)
        st.download_button(
            "⬇️ Download messages as Excel",
            data=buffer,
            file_name="reminder_messages.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    elif not api_key:
        st.warning("Please enter your Gemini API key in the sidebar first.")
