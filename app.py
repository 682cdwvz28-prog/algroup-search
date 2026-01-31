import asyncio
import uuid
from typing import Dict, List

from fastapi import FastAPI, Request, Form, WebSocket, WebSocketDisconnect
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from email_collector import split_queries, collect_emails_for_query
from send_emails import send_emails_smtp

app = FastAPI()
templates = Jinja2Templates(directory="templates")

SEARCH_SESSIONS: Dict[str, Dict[str, List[dict]]] = {}
PROGRESS: Dict[str, float] = {}
WS_CONNECTIONS: Dict[str, List[WebSocket]] = {}


async def notify_progress(search_id: str):
    value = PROGRESS.get(search_id, 0.0)
    for ws in WS_CONNECTIONS.get(search_id, []):
        try:
            await ws.send_json({"progress": value})
        except Exception:
            pass


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/search", response_class=HTMLResponse)
async def search(request: Request, raw_query: str = Form(...)):
    queries = split_queries(raw_query)
    search_id = str(uuid.uuid4())
    SEARCH_SESSIONS[search_id] = {}
    PROGRESS[search_id] = 0.0

    async def run_collection():
        total_q = len(queries) or 1
        done_q = 0

        for q in queries:
            def cb_local(p: float, q=q):
                # прогресс внутри одного запроса
                PROGRESS[search_id] = (done_q + p) / total_q

            rows = await collect_emails_for_query(q, pages=2, progress_cb=lambda p: cb_local(p))
            SEARCH_SESSIONS[search_id][q] = rows
            done_q += 1
            PROGRESS[search_id] = done_q / total_q
            await notify_progress(search_id)

        PROGRESS[search_id] = 1.0
        await notify_progress(search_id)

    asyncio.create_task(run_collection())

    return templates.TemplateResponse(
        "results.html",
        {
            "request": request,
            "search_id": search_id,
            "rows": [],  # сначала пусто, потом фронт может перезагружать/обновлять
        },
    )


@app.websocket("/ws/{search_id}")
async def ws_progress(websocket: WebSocket, search_id: str):
    await websocket.accept()
    WS_CONNECTIONS.setdefault(search_id, []).append(websocket)
    try:
        while True:
            await asyncio.sleep(1)
            await websocket.send_json({"progress": PROGRESS.get(search_id, 0.0)})
    except WebSocketDisconnect:
        WS_CONNECTIONS[search_id].remove(websocket)


@app.post("/refresh_results", response_class=HTMLResponse)
async def refresh_results(request: Request, search_id: str = Form(...)):
    all_rows: List[dict] = []
    for q, rows in SEARCH_SESSIONS.get(search_id, {}).items():
        all_rows.extend(rows)
    return templates.TemplateResponse(
        "results.html",
        {
            "request": request,
            "search_id": search_id,
            "rows": all_rows,
        },
    )


@app.post("/compose", response_class=HTMLResponse)
async def compose(
    request: Request,
    search_id: str = Form(...),
    selected: List[str] = Form(...),
):
    per_query: Dict[str, set] = {}
    for item in selected:
        q, email = item.split("|", 1)
        per_query.setdefault(q, set()).add(email)

    return templates.TemplateResponse(
        "compose.html",
        {
            "request": request,
            "search_id": search_id,
            "per_query": {k: sorted(v) for k, v in per_query.items()},
        },
    )


@app.post("/send", response_class=HTMLResponse)
async def send(
    request: Request,
    search_id: str = Form(...),
    # динамические поля body_1, emails_1, query_1, ...
    **form_data,
):
    blocks = []
    idx = 1
    while True:
        body_key = f"body_{idx}"
        emails_key = f"emails_{idx}"
        query_key = f"query_{idx}"
        if body_key not in form_data:
            break
        body = form_data[body_key]
        emails = [e.strip() for e in form_data[emails_key].split(",") if e.strip() and e != "-"]
        query = form_data[query_key]
        if emails:
            send_emails_smtp(emails, subject=f"Запрос: {query}", body=body)
        blocks.append({"query": query, "emails": emails})
        idx += 1

    return templates.TemplateResponse(
        "sent.html",
        {"request": request, "blocks": blocks},
    )
