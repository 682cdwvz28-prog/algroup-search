import os
import asyncio
from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from logging_config import setup_logging
from task_queue import TaskQueue
from worker import MailWorker
from search_yandex_api import search_yandex
from normalize import normalize_search_results
from extract_emails import extract_emails_from_url
from mailer import render_template

setup_logging()

app = FastAPI()

# static folder (Render тоже поддерживает)
if not os.path.exists("static"):
    os.makedirs("static")

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

queue = TaskQueue()
worker = MailWorker(queue)


@app.on_event("startup")
async def startup_event():
    asyncio.create_task(worker.start())


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/run", response_class=HTMLResponse)
async def run(
    request: Request,
    query: str = Form(...),
    max_sites: int = Form(5)
):
    raw = await search_yandex(query)
    sites = normalize_search_results(raw)[:max_sites]

    emails_collected = []

    for item in sites:
        url = item["url"]
        html_emails = await extract_emails_from_url(url)

        for email in html_emails:
            body = render_template()
            task = {
                "email": email,
                "subject": "Кабельно-проводниковая продукция — предложение",
                "body": body
            }
            await queue.put(task)
            emails_collected.append({"url": url, "email": email})

    return templates.TemplateResponse(
        "result.html",
        {
            "request": request,
            "query": query,
            "emails": emails_collected,
            "queued": len(emails_collected)
        }
    )
