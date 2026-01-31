import os
import httpx
import base64

FOLDER_ID = os.getenv("YANDEX_FOLDER_ID")
API_KEY = os.getenv("YANDEX_SEARCH_API_KEY")

SEARCH_URL = "https://searchapi.api.cloud.yandex.net/v2/web/search"


async def search_yandex(query: str, page: int = 1):

    headers = {
        "Authorization": f"Api-Key {API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "query": {
            "searchType": "WEB",
            "queryText": query,
            "familyMode": "NONE",
            "page": str(page),
            "fixTypoMode": "DEFAULT"
        },
        "sortSpec": {
            "sortMode": "RELEVANCE",
            "sortOrder": "DESC"
        },
        "groupSpec": {
            "groupMode": "FLAT",
            "groupsOnPage": 10,
            "docsInGroup": 1
        },
        "maxPassages": 0,
        "region": "213",
        "l10N": "ru",
        "folderId": FOLDER_ID,
        "responseFormat": "HTML",
        "userAgent": "Mozilla/5.0"
    }

    async with httpx.AsyncClient(timeout=20) as client:
        resp = await client.post(SEARCH_URL, headers=headers, json=payload)
        print("DEBUG:", resp.text)
        resp.raise_for_status()
        data = resp.json()

        raw = data.get("rawData")
        if raw:
            return base64.b64decode(raw).decode("utf-8")

        return None
