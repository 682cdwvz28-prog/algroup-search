from fastapi import FastAPI, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from search_yandex_api import search_yandex

app = FastAPI()

# Папка с HTML-шаблонами
templates = Jinja2Templates(directory="templates")

# Папка со статикой (если понадобится)
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/")
async def index(request: Request):
    return templates.TemplateResponse(
        "index.html",
        {"request": request}
    )


@app.post("/run")
async def run(request: Request, query: str = Form(...)):
    results = await search_yandex(query)

    return templates.TemplateResponse(
        "results.html",
        {
            "request": request,
            "query": query,
            "results": results
        }
    )
