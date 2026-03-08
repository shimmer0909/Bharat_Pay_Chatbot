import json
import os
import re
import requests
from datetime import datetime

from pypdf import PdfReader
from pdf2image import convert_from_path
import pytesseract

# -----------------------------
# Configuration
# -----------------------------

METADATA_FILE = "./data/documents_metadata.json"
DOWNLOAD_FOLDER = "data"
OUTPUT_FILE = "processed_chunks.json"

CHUNK_SIZE = 400
CHUNK_OVERLAP = 100 # Increased due to stepwise guidelines or table instructions

os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)


# -----------------------------
# Load metadata
# -----------------------------

def load_metadata():

    with open(METADATA_FILE, "r") as f:
        documents = json.load(f)

    print(f"Loaded {len(documents)} documents")
    return documents


# -----------------------------
# Download PDF
# -----------------------------

def download_document(doc):

    url = doc["url"]

    safe_title = re.sub(r'[^a-zA-Z0-9_\-\.]', '_', doc["title"])

    if not safe_title.lower().endswith(".pdf"):
        filename = f"{safe_title}.pdf"
    else:
        filename = safe_title

    filepath = os.path.join(DOWNLOAD_FOLDER, filename)

    if os.path.exists(filepath):
        print("Already downloaded:", filename)
        return filepath

    try:

        r = requests.get(url, timeout=30)
        r.raise_for_status()

        with open(filepath, "wb") as f:
            f.write(r.content)

        print("Downloaded:", filename)

        return filepath

    except Exception as e:

        print("Download failed:", e)
        return None


# -----------------------------
# Normal PDF text extraction
# -----------------------------

def extract_text_from_pdf(filepath):

    try:

        reader = PdfReader(filepath)

        text = ""

        for page in reader.pages:

            page_text = page.extract_text()

            if page_text:
                text += page_text + "\n"

        return text

    except Exception as e:

        print("PDF extraction error:", e)
        return ""


# -----------------------------
# OCR extraction
# -----------------------------

def extract_text_with_ocr(filepath):

    print("Running OCR...")

    try:

        images = convert_from_path(filepath)

        text = ""

        for img in images:

            page_text = pytesseract.image_to_string(img)

            text += page_text + "\n"

        return text

    except Exception as e:

        print("OCR failed:", e)
        return ""


# -----------------------------
# Clean text
# -----------------------------

def clean_text(text):

    text = text.replace("\n", " ")
    text = text.replace("\t", " ")

    while "  " in text:
        text = text.replace("  ", " ")

    return text.strip()


# -----------------------------
# Chunk text
# -----------------------------

def chunk_text(text):
    words = text.split()
    chunks = []
    i = 0
    while i < len(words):
        chunk = words[i:i + CHUNK_SIZE]
        chunks.append(" ".join(chunk))
        i += CHUNK_SIZE - CHUNK_OVERLAP
    return chunks


# -----------------------------
# Attach metadata
# -----------------------------

def create_chunks(doc, text):

    text = clean_text(text)

    chunks = chunk_text(text)

    structured_chunks = []

    for i, chunk in enumerate(chunks):

        structured_chunks.append({
            "chunk_id": f"{doc['title']}_chunk{i}",
            "text": chunk,
            "title": doc["title"],
            "source": doc["source"],
            "document_type": doc["document_type"],
            "url": doc["url"],
            "processed_at": datetime.utcnow().isoformat()
        })

    return structured_chunks


# -----------------------------
# Main pipeline
# -----------------------------

def process_documents():

    documents = load_metadata()

    all_chunks = []

    for doc in documents:

        print("\nProcessing:", doc["title"])

        filepath = download_document(doc)

        if not filepath:
            continue

        # Try normal extraction first
        text = extract_text_from_pdf(filepath)

        # If empty → OCR
        if len(text.strip()) < 50:

            print("Text extraction failed. Trying OCR.")

            text = extract_text_with_ocr(filepath)

        if len(text.strip()) < 50:

            print("Still no text. Skipping.")
            continue

        chunks = create_chunks(doc, text)

        print("Created", len(chunks), "chunks")

        all_chunks.extend(chunks)

    return all_chunks


# -----------------------------
# Save output
# -----------------------------

def save_chunks(chunks):

    with open(OUTPUT_FILE, "w") as f:

        json.dump(chunks, f, indent=2)

    print("\nSaved", len(chunks), "chunks")


# -----------------------------
# Entry
# -----------------------------

if __name__ == "__main__":

    chunks = process_documents()

    save_chunks(chunks)