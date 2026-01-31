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

# search_id -> {"queries": [...], "results": {query: [rows...]}}
SEARCH_SESSIONS: Dict[str, Dict] = {}
# search_id -> float (0.0–1.0)
PROGRESS: Dict[str, float] = {}


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/search", response_class=HTMLResponse)
async def search(request: Request, raw_query: str = Form(...)):
    """
    1) Разбиваем строку на запросы
    2) Создаём search_id
    3) Сохраняем список запросов, пустые результаты
    4) Отдаём results.html с пустой таблицей — дальше всё делает WebSocket
    """
    queries = split_queries(raw_query)
    search_id = str(uuid.uuid4())

    SEARCH_SESSIONS[search_id] = {
        "queries": queries,
        "results": {},  # query -> rows
    }
    PROGRESS[search_id] = 0.0

    return templates.TemplateResponse(
        "results.html",
        {
            "request": request,
            "search_id": search_id,
            "rows": [],
        },
    )


@app.websocket("/ws/{search_id}")
async def ws_progress(websocket: WebSocket, search_id: str):
    """
    WebSocket:
    - запускает сбор сайтов и e‑mail
    - шлёт прогресс
    - по завершении даёт 100% и закрывается
    """
    await websocket.accept()

    session = SEARCH_SESSIONS.get(search_id)
    if not session:
        await websocket.send_json({"error": "unknown search_id"})
        await websocket.close()
        return

    queries: List[str] = session["queries"]
    total_q = len(queries) or 1
    done_q = 0

    try:
        for q in queries:
            # локальный callback прогресса внутри одного запроса
            async def progress_cb_inner(p: float, q=q):
                PROGRESS[search_id] = (done_q + p) / total_q
                await websocket.send_json({"progress": PROGRESS[search_id]})

            # обёртка, чтобы передать async‑callback в sync‑сигнатуру
            def progress_cb(p: float, q=q):
                asyncio.create_task(progress_cb_inner(p, q))

            rows = await collect_emails_for_query(
                q,
                pages=2,
                progress_cb=progress_cb,
            )
            session["results"][q] = rows
            done_q += 1
            PROGRESS[search_id] = done_q / total_q
            await websocket.send_json({"progress": PROGRESS[search_id]})

        PROGRESS[search_id] = 1.0
        await websocket.send_json({"progress": 1.0, "done": True})
        await websocket.close()

    except WebSocketDisconnect:
        return
    except Exception as e:
        await websocket.send_json({"error": str(e)})
        await websocket.close()


@app.post("/refresh_results", response_class=HTMLResponse)
async def refresh_results(request: Request, search_id: str = Form(...)):
    """
    Возвращает только таблицу результатов (results_table.html)
    """
    session = SEARCH_SESSIONS.get(search_id)
    all_rows: List[dict] = []

    if session:
        for q, rows in session["results"].items():
            all_rows.extend(rows)

    return templates.TemplateResponse(
        "results_table.html",
        {"request": request, "rows": all_rows},
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
        emails = [
            e.strip()
            for e in form_data[emails_key].split(",")
            if e.strip() and e != "-"
        ]
        query = form_data[query_key]

        if emails:
            send_emails_smtp(emails, subject=f"Запрос: {query}", body=body)

        blocks.append({"query": query, "emails": emails})
        idx += 1

    return templates.TemplateResponse(
        "sent.html",
        {"request": request, "blocks": blocks},
    )
