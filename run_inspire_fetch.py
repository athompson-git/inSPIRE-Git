import requests
import json
import re
from time import sleep

# Search: papers mentioning github in fulltext
BASE_URL = "https://inspirehep.net/api/literature"

# default param dict
params = {
    "q": "fulltext:github.com/",
    "size": 250,  # results per page
    "page": 1,  # page number
    "fields": "authors,external_system_identifiers,metadata,preprint_date,earliest_date,dois,arxiv_eprints,citation_count,titles,urls" 
}

# Regex pattern to find GitHub URLs
GITHUB_REGEX = re.compile(r"https?://github\.com/[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", re.IGNORECASE)

def fetch_bibtex(inspire_id):
    """Fetch BibTeX entry for a given Inspire record ID."""
    bibtex_url = f"{BASE_URL}/{inspire_id}?format=bibtex"
    resp = requests.get(bibtex_url)
    if resp.status_code == 200:
        return resp.text
    return ""

def extract_github_links(text):
    """Extract GitHub links from text using regex."""
    return list(set(GITHUB_REGEX.findall(text)))

def run_fetch(output_file="inspire_github_papers.json", page_size=25, max_pages=5,
              verbose=False):
    # create output .json file
    # json file should contain list of papers with fields:
    # id, title, authors, arxiv, citations, year, urls

    papers = []
    
    for page in range(1, max_pages + 1):
        params_paginated = params.copy()
        params_paginated["size"] = page_size
        params_paginated["page"] = page

        resp = requests.get(BASE_URL, params=params_paginated)
        resp.raise_for_status()
        data = resp.json()

        print(f"Fetched page {page} with {len(data['hits']['hits'])} records.")

        for hit in data["hits"]["hits"]:
            metadata = hit["metadata"]
            inspire_id = hit["id"]

            # title
            title = metadata["titles"][0]["title"] if "titles" in metadata else None

            # authors
            authors = [a["full_name"] for a in metadata.get("authors", [])]

            # arXiv
            arxiv = None
            if "arxiv_eprints" in metadata:
                arxiv = metadata["arxiv_eprints"][0].get("value")

            # citation count
            citations = metadata.get("citation_count", 0)

            # year
            year = metadata.get("earliest_date", "")[:4]

            # URLs (including possibly github links if embedded)
            urls_meta = [u["value"] for u in metadata.get("urls", [])]

            # also scrape the bibtex for github links
            #bibtex = fetch_bibtex(inspire_id)
            #urls_bibtex = extract_github_links(bibtex)

            urls = list(set(urls_meta))
            # remove all non-github urls
            urls = [u for u in urls if "github.com" in u]

            if "github.com" not in " ".join(urls):
                if verbose:
                    print(f"⚠️ No GitHub link found for Inspire ID {inspire_id}, skipping.")
                continue

            # add to json object to output to .json
            # Construct record
            record = {
                "id": inspire_id,
                "title": title,
                "authors": authors,
                "arxiv": arxiv,
                "citations": citations,
                "year": year,
                "urls": urls
            }

            papers.append(record)

    # Save to JSON file
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(papers, f, indent=2, ensure_ascii=False)

    print(f"Saved {len(papers)} records to {output_file}")

        

if __name__ == "__main__":
    run_fetch(max_pages=10, page_size=250)