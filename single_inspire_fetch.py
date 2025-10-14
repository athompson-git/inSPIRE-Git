import requests

# Example search: papers mentioning github in fulltext
url = "https://inspirehep.net/api/literature"
params = {
    "q": "fulltext:github.com/",
    "size": 5,  # adjust as needed
    "fields": "authors,external_system_identifiers,metadata,preprint_date,earliest_date,dois,arxiv_eprints,citation_count,titles,urls" 
}

resp = requests.get(url, params=params)
resp.raise_for_status()
data = resp.json()

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
    urls = [u["value"] for u in metadata.get("urls", [])]

    print({
        "id": inspire_id,
        "title": title,
        "authors": authors,
        "arxiv": arxiv,
        "citations": citations,
        "year": year,
        "urls": urls
    })
