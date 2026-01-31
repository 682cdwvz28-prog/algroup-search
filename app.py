from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from search_yandex_api import search_yandex

app = FastAPI()
templates = Jinja2Templates(directory="templates")


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/run", response_class=HTMLResponse)
async def run(request: Request, query: str = Form(...)):
    # Выполняем запрос к Yandex Search API
    data = await search_yandex(query)

    # Определяем, где лежит HTML
    html_raw = (
        data.get("html") or
        data.get("result") or
        data.get("response") or
        data
    )

    return templates.TemplateResponse(
        "result.html",
        {
            "request": request,
            "query": query,
            "html_raw": html_raw
        }
    )
