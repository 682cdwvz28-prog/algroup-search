def normalize_search_results(data):
    results = []

    for block in data.get("results", []):
        doc = block.get("doc", {})
        url = doc.get("url")
        title = doc.get("title")
        snippet = doc.get("snippet")

        if url:
            results.append({
                "url": url,
                "title": title,
                "snippet": snippet
            })

    return results
