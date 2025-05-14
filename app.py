import streamlit as st
import subprocess
from pathlib import Path
import uuid
import os

st.set_page_config(page_title="Quote Auto-Fill", layout="centered")
st.title("📄 Upload Application to Auto-Fill Quote")

uploaded_file = st.file_uploader("Upload Application PDF", type=["pdf"])

if uploaded_file:
    # Use a unique temp path to avoid conflicts
    unique_id = str(uuid.uuid4())
    input_filename = f"{unique_id}.pdf"
    input_path = Path("input") / input_filename

    os.makedirs("input", exist_ok=True)
    os.makedirs("output", exist_ok=True)

    # Save uploaded file
    with open(input_path, "wb") as f:
        f.write(uploaded_file.read())

    st.success("✅ File uploaded")

    if st.button("✨ Generate Filled Document"):
        with st.spinner("Processing..."):
            result = subprocess.run(["python3", "scripts/extract_data.py", str(input_path)])

        output_path = Path("output/filled.docx")

        if output_path.exists():
            with open(output_path, "rb") as f:
                st.download_button("📥 Download Filled Document", f, file_name="filled.docx")
        else:
            st.error("❌ Something went wrong generating the document.")
