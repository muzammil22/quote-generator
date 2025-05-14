import streamlit as st
from pathlib import Path
import uuid
import os
from scripts.extract_data import run_pipeline as generate_filled_doc

st.set_page_config(page_title="Quote Auto-Fill", layout="centered")
st.title("📄 Upload Application to Auto-Fill Quote")

uploaded_file = st.file_uploader("Upload Application PDF", type=["pdf"])

if uploaded_file:
    unique_id = str(uuid.uuid4())
    input_path = Path("input") / f"{unique_id}.pdf"
    os.makedirs("input", exist_ok=True)
    os.makedirs("output", exist_ok=True)

    with open(input_path, "wb") as f:
        f.write(uploaded_file.read())

    st.success("✅ File uploaded")

    if st.button("✨ Generate Filled Document"):
        with st.spinner("Processing..."):
            filled_path = generate_filled_doc(str(input_path))

        if filled_path.exists():
            with open(filled_path, "rb") as f:
                st.download_button("📥 Download Filled Document", f, file_name="filled.docx")
        else:
            st.error("❌ Something went wrong.")
