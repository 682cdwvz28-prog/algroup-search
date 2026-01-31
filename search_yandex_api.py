import os
import httpx

API_KEY = os.getenv("YANDEX_SEARCH_API_KEY")

SEARCH_URL = "https://search-api.yandex.net/api/v1/search"


async def search_yandex(query: str, page: int = 1, page_size: int = 10):
    if not API_KEY:
        raise RuntimeError("YANDEX_SEARCH_API_KEY is not set")

    headers = {
        "Authorization": f"Api-Key {API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "query": query,
        "page": page,
        "pageSize": page_size,
        "format": "HTML",        # или "XML"
        "userDevice": "desktop"  # desktop / mobile
    }

    async with httpx.AsyncClient(timeout=20) as client:
        resp = await client.post(
            SEARCH_URL,
            headers=headers,
            json=payload
        )
        resp.raise_for_status()

        # Временно выводим ответ в логи, чтобы видеть структуру
        print("YANDEX SEARCH RAW RESPONSE:", resp.text)

        return resp.json()
