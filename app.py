import streamlit as st
import subprocess
from pathlib import Path

st.set_page_config(page_title="Quote Auto-Fill", layout="centered")
st.title("📄 Upload Application to Auto-Fill Quote")

uploaded_file = st.file_uploader("Upload Application PDF", type=["pdf"])

if uploaded_file:
    input_path = "input/application.pdf"
    with open(input_path, "wb") as f:
        f.write(uploaded_file.read())

    st.success("✅ File uploaded")

    if st.button("✨ Generate Filled Document"):
        with st.spinner("Processing..."):
            result = subprocess.run(["python3", "scripts/extract_data.py", input_path])

        filled_path = Path("output/filled.docx")
        if filled_path.exists():
            with open(filled_path, "rb") as f:
                st.download_button("📥 Download Filled Document", f, file_name="filled.docx")
        else:
            st.error("❌ Something went wrong.")
