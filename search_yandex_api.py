import os
import httpx
import base64
import xml.etree.ElementTree as ET

FOLDER_ID = os.getenv("YANDEX_FOLDER_ID")
API_KEY = os.getenv("YANDEX_SEARCH_API_KEY")

SEARCH_URL = "https://searchapi.api.cloud.yandex.net/v2/web/search"


async def search_yandex(query: str, page: int = 1):
    headers = {
        "Authorization": f"Api-Key {API_KEY}",
        "Content-Type": "application/json",
    }

    payload = {
        "query": {
            "searchType": "SEARCH_TYPE_RU",
            "queryText": query,
        },
        "page": {
            "page": page,
            "pageSize": 10,
        },
        "folderId": FOLDER_ID,
    }

    async with httpx.AsyncClient(timeout=20) as client:
        resp = await client.post(SEARCH_URL, headers=headers, json=payload)
        print("=== YANDEX DEBUG START ===")
        print("STATUS:", resp.status_code)
        print("TEXT:", resp.text)
        print("=== YANDEX DEBUG END ===")
        resp.raise_for_status()
        data = resp.json()

    raw = data.get("rawData")
    if not raw:
        return []

    xml_text = base64.b64decode(raw).decode("utf-8")
    root = ET.fromstring(xml_text)

    results = []
    for doc in root.findall(".//doc"):
        title = doc.findtext("title")
        url = doc.findtext("url")
        domain = doc.findtext("domain")
        snippet = doc.findtext("headline")
        if title and url:
            results.append(
                {
                    "title": title,
                    "url": url,
                    "domain": domain,
                    "snippet": snippet,
                }
            )
    return results


async def search_yandex_sites(query: str, pages: int = 2) -> list[str]:
    urls: list[str] = []
    for p in range(1, pages + 1):
        items = await search_yandex(query, page=p)
        for it in items:
            u = it["url"]
            if u not in urls:
                urls.append(u)
    return urls
