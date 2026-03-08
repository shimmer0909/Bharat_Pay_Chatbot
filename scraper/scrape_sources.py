import requests
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright
from urllib.parse import urljoin
from datetime import datetime
import json
import os


def scrape_rbi():
    print("Scraping RBI ATM circulars...")

    url = "https://rbi.org.in/scripts/ATMView.aspx"

    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")

    documents = []

    for a in soup.find_all("a", href=True):

        href = a["href"]

        if "PDF" in href.upper() and "ATM" in href.upper():

            full_link = urljoin(url, href)

            title = a.text.strip()

            if not title:
                title = href.split("/")[-1]

            documents.append({
                "title": title,
                "url": full_link,
                "source": "rbi",
                "document_type": "atm_circular",
                "scraped_at": datetime.now().isoformat()
            })

    return documents


def scrape_npci():

    print("Scraping NPCI UPI circulars via API...")

    base_url = "https://www.npci.org.in/api/circulars/upi"

    documents = []

    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept": "application/json"
    }

    years = [2026, 2025, 2024, 2023]

    for year in years:

        page = 1

        while True:

            params = {
                "pageNum": page,
                "year": year,
                "sort": "desc",
                "size": 10,
                "locale": "en"
            }

            response = requests.get(base_url, params=params, headers=headers)

            print(f"NPCI Year {year} Page {page} Status:", response.status_code)

            if response.status_code != 200:
                break

            data = response.json()

            files = data.get("data", {}).get("files", [])

            if not files:
                break

            print("Files found:", len(files))

            for item in files:

                media = item.get("media")

                if not media:
                    continue

                pdf_path = media.get("url")

                if not pdf_path:
                    continue

                pdf_url = "https://www.npci.org.in" + pdf_path

                documents.append({
                    "title": item.get("fileName"),
                    "url": pdf_url,
                    "source": "npci",
                    "document_type": "upi_circular"
                })

            page += 1

    print("NPCI DOCUMENTS FOUND:", len(documents))

    return documents


def main():

    all_documents = []

    rbi_docs = scrape_rbi()
    npci_docs = scrape_npci()

    all_documents.extend(rbi_docs)
    all_documents.extend(npci_docs)

    print(f"\nTotal documents collected: {len(all_documents)}")

    os.makedirs("data", exist_ok=True)

    with open("data/documents_metadata.json", "w") as f:
        json.dump(all_documents, f, indent=4)

    print("Saved metadata to data/documents_metadata.json")


if __name__ == "__main__":
    main()