import asyncio
from search_yandex_api import search_yandex

async def main():
    result = await search_yandex("станок ЧПУ")
    print(result)

asyncio.run(main())
