import pdfplumber
from pathlib import Path
import json
import openai
import base64
import os
import streamlit as st
from scripts.fill_docx import fill_doc
import fitz  # PyMuPDF

def run_pipeline(pdf_path):
    data = {}

    with pdfplumber.open(pdf_path) as pdf:
        text = "\n".join([page.extract_text() for page in pdf.pages if page.extract_text()])

    print(text)

    def extract_between(text, start, end=None):
        try:
            segment = text.split(start)[1]
            return segment.split(end)[0].strip() if end else segment.strip()
        except IndexError:
            return ""

    data['entity'] = extract_between(text, "Legal and Business", "Name:")
    data['state'] = extract_between(text, "State:", "ZIP:")
    data['services'] = extract_between(text, "coverage is desired:", "This document")
    data['revenue'] = extract_between(text, "Current $", "b)")
    data['retro_date'] = extract_between(text, "RETROACTIVE DATE OF CURRENT POLICY:", "\n")
    data['limit'] = extract_between(text, "4.", "each Claim/Annual Aggregate")
    data['program'] = "PP23X FIXED QUOTE"

    def get_page_image(pdf_path, page_number=3):
        doc = fitz.open(pdf_path)
        page = doc.load_page(page_number)
        pix = page.get_pixmap(dpi=150)
        return pix.tobytes("png")

    image_bytes = get_page_image(pdf_path)
    img_base64 = base64.b64encode(image_bytes).decode()

    openai.api_key = st.secrets["OPENAI_API_KEY"]

    response = openai.chat.completions.create(
        model="gpt-4.1",
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": (
                            "This is a screenshot from a medical application form. "
                            "Please check the form and tell me:\n"
                            "1. What was selected for Question 28 ?\n"
                            "2. What was selected for Question 29 ?\n\n"
                            "Respond in this exact JSON format:\n"
                            "{\n  \"claims\": \"Yes\" or \"No\",\n  \"disciplinary\": \"Yes\" or \"No\"\n}"
                        )
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/png;base64,{img_base64}"
                        }
                    }
                ]
            }
        ],
        max_tokens=200
    )

    try:
        result = json.loads(response.choices[0].message.content)
        data['claims'] = result.get("claims", "Unknown")
        data['disciplinary'] = result.get("disciplinary", "Unknown")
    except:
        data['claims'] = "Unknown"
        data['disciplinary'] = "Unknown"

    # Save the extracted data
    json_path = "/tmp/data.json"
    with open(json_path, "w") as f:
        json.dump(data, f, indent=2)

    output_path = "output/filled.docx"
    fill_doc("templates/quote.docx", json_path, output_path)

    return Path(output_path)
