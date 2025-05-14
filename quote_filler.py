from scripts.extract_data import run_pipeline

def generate_filled_doc(pdf_path: str):
    return run_pipeline(pdf_path)
