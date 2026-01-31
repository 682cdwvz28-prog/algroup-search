import os
import httpx

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
            "searchType": "SEARCH_TYPE_RU",
            "queryText": query
        },
        "page": {
            "page": page,
            "pageSize": 10
        },
        "folderId": FOLDER_ID
    }

    async with httpx.AsyncClient(timeout=20) as client:
        resp = await client.post(SEARCH_URL, headers=headers, json=payload)

        print("=== YANDEX DEBUG START ===")
        print("STATUS:", resp.status_code)
        print("TEXT:", resp.text)
        print("=== YANDEX DEBUG END ===")

        resp.raise_for_status()
        return resp.json()
