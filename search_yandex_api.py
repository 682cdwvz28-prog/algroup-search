import os
import httpx
from iam_token import get_iam_token

FOLDER_ID = os.getenv("YANDEX_FOLDER_ID")

SEARCH_URL = "https://search-api.cloud.yandex.net/search/v1/web"


async def search_yandex(query: str, page: int = 1, page_size: int = 10):
    token = await get_iam_token()

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    payload = {
        "query": query,
        "page": page,
        "pageSize": page_size,
        "folderId": FOLDER_ID,
        "format": "HTML",       # HTML выдача Яндекса
        "userDevice": "desktop" # можно "mobile"
    }

    async with httpx.AsyncClient(timeout=20) as client:
        resp = await client.post(
            SEARCH_URL,
            headers=headers,
            json=payload
        )
        resp.raise_for_status()
        return resp.json()["html"]  # HTML выдача
