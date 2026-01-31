import os
import httpx
from iam_token import get_iam_token

FOLDER_ID = os.getenv("YANDEX_FOLDER_ID")

# Новый официальный endpoint WebSearch API
SEARCH_URL = "https://searchapi.api.cloud.yandex.net/websearch/v1/search"


async def search_yandex(query: str, page: int = 1, page_size: int = 10):
    iam_token = await get_iam_token()

    headers = {
        "Authorization": f"Bearer {iam_token}",
        "Content-Type": "application/json"
    }

    payload = {
        "folderId": FOLDER_ID,
        "query": query,
        "page": page,
        "pageSize": page_size,
        "userDevice": "desktop",
        "format": "HTML"   # HTML выдача Яндекса
    }

    async with httpx.AsyncClient(timeout=20) as client:
        resp = await client.post(
            SEARCH_URL,
            headers=headers,
            json=payload
        )
        print("RAW RESPONSE:", resp.text)  # временно для логов
        resp.raise_for_status()
        return resp.json()
