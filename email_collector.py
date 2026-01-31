import asyncio
import re
from typing import Callable, Dict, List

import httpx
from bs4 import BeautifulSoup

from search_yandex_api import search_yandex_sites


EMAIL_RE = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")


async def extract_emails_from_url(client: httpx.AsyncClient, url: str) -> List[str]:
    """
    Загружает страницу и извлекает e‑mail адреса.
    Возвращает список строк.
    """
    try:
        resp = await client.get(url, timeout=10)
        resp.raise_for_status()
    except Exception:
        return []

    text = resp.text
    emails = set(EMAIL_RE.findall(text))

    soup = BeautifulSoup(text, "html.parser")
    for a in soup.find_all("a", href=True):
        href = a["href"]
        if href.startswith("mailto:"):
            emails.add(href[7:].split("?")[0].strip())

    return list(emails)


async def collect_emails_for_query(
    query: str,
    pages: int = 2,
    progress_cb: Callable[[float], None] | None = None,
) -> List[Dict]:
    """
    Ищет сайты по запросу, собирает e‑mail, возвращает список словарей:
    {
        "query": "...",
        "url": "...",
        "short_url": "...",
        "emails": [...]
    }
    """
    sites = await search_yandex_sites(query, pages=pages)
    total = len(sites) or 1

    rows: List[Dict] = []

    async with httpx.AsyncClient() as client:
        tasks = [extract_emails_from_url(client, url) for url in sites]
        results = await asyncio.gather(*tasks, return_exceptions=True)

    for idx, (url, emails) in enumerate(zip(sites, results)):
        if isinstance(emails, Exception) or not emails:
            rows.append(
                {
                    "query": query,
                    "url": url,
                    "short_url": url[:27] + "..." if len(url) > 30 else url,
                    "emails": ["-"],
                }
            )
        else:
            rows.append(
                {
                    "query": query,
                    "url": url,
                    "short_url": url[:27] + "..." if len(url) > 30 else url,
                    "emails": emails,
                }
            )

        if progress_cb:
            progress_cb((idx + 1) / total)

    return rows


def split_queries(raw: str) -> List[str]:
    """
    Разбивает строку вида "станок, алгруп, чпу" на список запросов.
    """
    return [q.strip() for q in raw.split(",") if q.strip()]
