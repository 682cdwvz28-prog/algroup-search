import asyncio
from typing import List
from urllib.parse import urlparse, urljoin

import httpx
from bs4 import BeautifulSoup


YA_SEARCH_URL = "https://ya.ru/search/"


HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/122.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "ru-RU,ru;q=0.9,en;q=0.8",
    "Referer": "https://ya.ru/",
}


def _is_good_result_url(url: str) -> bool:
    """
    Фильтруем мусор:
    - яндекс-домены
    - явные статики (css/js/png/jpg/svg)
    """
    if not url.startswith("http"):
        return False

    parsed = urlparse(url)
    host = parsed.netloc.lower()

    # отбрасываем всё яндексовое
    if "yandex." in host or host.startswith("ya.ru"):
        return False

    # отбрасываем статику
    bad_ext = (".css", ".js", ".png", ".jpg", ".jpeg", ".gif", ".svg", ".ico", ".webp")
    if parsed.path.lower().endswith(bad_ext):
        return False

    return True


async def _fetch_page(client: httpx.AsyncClient, query: str, page: int, lr: int = 2) -> List[str]:
    """
    Загружает одну страницу выдачи ya.ru/search и возвращает список URL.
    """
    params = {
        "text": query,
        "lr": str(lr),
        "p": str(page),  # номер страницы: 0,1,...
    }

    resp = await client.get(YA_SEARCH_URL, params=params, headers=HEADERS, timeout=15)
    resp.raise_for_status()

    soup = BeautifulSoup(resp.text, "lxml")

    urls: List[str] = []

    # Основные органические результаты
    # Структура может меняться, поэтому берём все <a> с href и фильтруем
    for a in soup.find_all("a", href=True):
        href = a["href"]

        # Пропускаем внутренние якоря и js-ссылки
        if href.startswith("#") or href.startswith("javascript:"):
            continue

        # Преобразуем относительные ссылки в абсолютные
        if href.startswith("/"):
            href = urljoin(YA_SEARCH_URL, href)

        if _is_good_result_url(href):
            urls.append(href)

    return urls


async def search_yandex_sites(query: str, pages: int = 2, lr: int = 2) -> List[str]:
    """
    Возвращает до 20 уникальных URL из выдачи ya.ru/search
    по первым `pages` страницам (обычно 2 достаточно).
    """
    async with httpx.AsyncClient(follow_redirects=True) as client:
        tasks = [
            _fetch_page(client, query=query, page=p, lr=lr)
            for p in range(pages)
        ]
        results_per_page = await asyncio.gather(*tasks, return_exceptions=True)

    all_urls: List[str] = []
    for res in results_per_page:
        if isinstance(res, Exception):
            continue
        all_urls.extend(res)

    # Убираем дубли, сохраняем порядок
    seen = set()
    unique_urls: List[str] = []
    for url in all_urls:
        if url not in seen:
            seen.add(url)
            unique_urls.append(url)

    # Ограничиваем топ‑20
    return unique_urls[:20]
