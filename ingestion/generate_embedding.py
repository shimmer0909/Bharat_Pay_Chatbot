import json
from models.embedding import generate_embedding
import re
import unicodedata

INPUT_FILE = "processed_chunks.json"
OUTPUT_FILE = "chunks_with_embeddings.json"

OCR_FIXES = {
    "UPt": "UPI",
    "Dy": "by",
    "spectied": "specified",
    "shoud": "should",
    "tago": "logo",
    "npci/upi/oc": "npci upi oc",
}

def fix_ocr(text):
    for wrong, correct in OCR_FIXES.items():
        text = text.replace(wrong, correct)

    text = re.sub(r'[^\w\s.,:%\-\/]', '', text)  # remove stray symbols
    return text

HEADER_PATTERNS = [
    "NATIONAL PAYMENTS CORPORATION OF INDIA",
    "Bandra Kurla Complex",
    "Mumbai 400",
    "contact@npci.org.in",
    "www.npci.org.in"
]

def remove_headers(text):
    for h in HEADER_PATTERNS:
        text = text.replace(h, "")
    return text

def remove_tables(text):

    text = re.sub(r'\b\d{6,}\b', ' ', text)   # large numbers
    text = re.sub(r'(\d+\s+){3,}', ' ', text) # numeric sequences
    text = re.sub(r'(\b\d+\b[\s,]*){4,}', ' ', text)

    return text

def normalize_unicode(text):

    text = unicodedata.normalize("NFKC", text)

    replacements = {
        "’": "'",
        "“": '"',
        "”": '"',
        "°": ""
    }

    for k,v in replacements.items():
        text = text.replace(k,v)

    return text

def filter_bad_chunks(text):

    letters = sum(c.isalpha() for c in text)

    if letters / max(len(text),1) < 0.2:
        return None

    return text

def remove_urls_emails(text):

    text = re.sub(r'http\S+', ' ', text)
    text = re.sub(r'\S+@\S+', ' ', text)

    return text

def remove_page_numbers(text):

    text = re.sub(r'Page\s+\d+\s+of\s+\d+', ' ', text, flags=re.I)

    return text

def clean_text(text):

    text = normalize_unicode(text)

    text = remove_headers(text)

    text = remove_tables(text)

    text = remove_urls_emails(text)

    text = remove_page_numbers(text)

    text = fix_ocr(text)

    text = filter_bad_chunks(text)

    if not text:
        return None

    text = text.lower()

    text = re.sub(r'\s+', ' ', text).strip()

    if len(text.split()) < 5:
        return None

    return text

def main():

    with open(INPUT_FILE, "r") as f:
        chunks = json.load(f)

    enriched_chunks = []

    for chunk in chunks:

        text = chunk["text"]

        text = clean_text(text)

        if not text:
            continue

        text = f"{chunk['title']} | {chunk['document_type']} | {chunk['source']} : {text}"

        embedding = generate_embedding(text)


        chunk["text"] = text
        chunk["embedding"] = embedding
        chunk["embedding_model"] = "bge-small-en"

        enriched_chunks.append(chunk)

    with open(OUTPUT_FILE, "w") as f:
        json.dump(enriched_chunks, f)

    print("Embeddings generated for", len(enriched_chunks), "chunks")


if __name__ == "__main__":
    main()