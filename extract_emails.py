import httpx
import re

EMAIL_REGEX = re.compile(
    r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}",
    re.IGNORECASE
)

async def fetch_html(url: str) -> str:
    try:
        async with httpx.AsyncClient(timeout=10, follow_redirects=True) as client:
            resp = await client.get(url)
            resp.raise_for_status()
            return resp.text
    except Exception:
        return ""

def extract_emails_from_html(html: str):
    emails = set(re.findall(EMAIL_REGEX, html))
    return list(emails)

async def extract_emails_from_url(url: str):
    html = await fetch_html(url)
    if not html:
        return []
    return extract_emails_from_html(html)
