import asyncio
from search_yandex_api import search_yandex
from normalize import normalize_search_results

async def main():
    print("Запрос в Yandex Search API v2...")

    raw = await search_yandex("станок ЧПУ")
    clean = normalize_search_results(raw)

    print("\n=== Нормализованные результаты ===")
    for item in clean:
        print(f"- {item['url']}")
        print(f"  {item['title']}")
        print(f"  {item['snippet']}\n")

asyncio.run(main())
