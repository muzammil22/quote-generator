import pdfplumber
import json
import sys
import os
import openai
import subprocess
from pdf2image import convert_from_path
from PIL import Image
from io import BytesIO
import base64
import streamlit as st

# === Step 0: Init ===
pdf_path = sys.argv[1]
data = {}

# === Step 1: Extract Text Data ===
with pdfplumber.open(pdf_path) as pdf:
    text = "\n".join([page.extract_text() for page in pdf.pages if page.extract_text()])

def extract_between(text, start, end=None):
    try:
        segment = text.split(start)[1]
        return segment.split(end)[0].strip() if end else segment.strip()
    except IndexError:
        return ""

print(text)

data['entity'] = extract_between(text, "Legal and Business", "Name")
data['state'] = extract_between(text, "State:", "ZIP:")
data['services'] = extract_between(text, "coverage is desired:", "This document")
data['revenue'] = extract_between(text, "Current $", "b)")
data['retro_date'] = extract_between(text, "RETROACTIVE DATE OF CURRENT POLICY:", "\n")
data['limit'] = extract_between(text, "4.", "each Claim/Annual Aggregate")
data['program'] = "PP23X FIXED QUOTE"

# === Step 2: GPT-4 Vision — Detect Q28 + Q29 from page 4 ===

def get_claims_disciplinary_from_gpt(pdf_path):
    print("🖼️ Converting page 4 to image...")
    images = convert_from_path(pdf_path, first_page=4, last_page=4)
    img = images[0]

    # Save for visual debug (optional)
    img.save("output/q28_q29_crop.png")

    buffered = BytesIO()
    img.save(buffered, format="PNG")
    img_base64 = base64.b64encode(buffered.getvalue()).decode()

    print("🚀 Sending image to GPT-4o...\n")
    
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

    content = response.choices[0].message.content

    try:
        result = json.loads(content)
        return result.get("claims", "Unknown"), result.get("disciplinary", "Unknown")
    except:
        print("⚠️ GPT-4o response could not be parsed as JSON:")
        print(content)
        return "Unknown", "Unknown"

claims, disciplinary = get_claims_disciplinary_from_gpt(pdf_path)
data['claims'] = claims
data['disciplinary'] = disciplinary

# === Write the final combined data ===
json_path = "/tmp/data.json"
with open(json_path, "w") as f:
    json.dump(data, f, indent=2)
print("✅ Data written to /tmp/data.json")

# === Call fill_docx.py to create final document ===
print("🧾 Generating final filled.docx...")
subprocess.run([
    "python3", "scripts/fill_docx.py",
    "templates/quote.docx",
    json_path,
    "output/filled.docx"
])
print("✅ filled.docx generated in /output/")