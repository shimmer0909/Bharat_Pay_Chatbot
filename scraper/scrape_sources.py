import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

sources = {
    "npci": "https://www.npci.org.in/circulars/upi",
    "rbi": "https://rbi.org.in/scripts/ATMView.aspx"
}

def scrape_source(name, url):
    print(f"Scraping {name}...")

    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")

    links = []

    for a in soup.find_all("a"):
        link = a.get("href")

        if link and "pdf" in link.lower():
            full_link = urljoin(url, link)
            links.append(full_link)

    return links


def main():
    all_links = {}

    for name, url in sources.items():
        links = scrape_source(name, url)
        all_links[name] = links

    for source, links in all_links.items():
        print(f"\n{source.upper()} documents:")
        for link in links:
            print(link)


if __name__ == "__main__":
    main()