import os
import httpx
import base64
from iam_token import get_iam_token

FOLDER_ID = os.getenv("YANDEX_FOLDER_ID")

SEARCH_URL = "https://searchapi.api.cloud.yandex.net/v2/web/search"


async def search_yandex(query: str, page: int = 1):
    iam_token = await get_iam_token()

    headers = {
        "Authorization": f"Bearer {iam_token}",
        "Content-Type": "application/json"
    }

    payload = {
        "query": {
            "searchType": "WEB",
            "queryText": query,
            "page": page,
            "familyMode": "NONE",
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
        "region": 213,
        "l10N": "ru",
        "folderId": FOLDER_ID,
        "responseFormat": "HTML",
        "userAgent": "Mozilla/5.0"
    }

    async with httpx.AsyncClient(timeout=20) as client:
        resp = await client.post(
            SEARCH_URL,
            headers=headers,
            json=payload
        )
        resp.raise_for_status()
        data = resp.json()

        # Декодируем Base64 → HTML
        raw = data.get("rawData")
        if raw:
            decoded = base64.b64decode(raw).decode("utf-8")
            return decoded

        return None
