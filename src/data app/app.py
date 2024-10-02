from contextlib import asynccontextmanager

from fastapi import FastAPI
from starlette.requests import Request
from starlette.templating import Jinja2Templates

from models import create_tables


@asynccontextmanager
async def lifespan(application: FastAPI):
    await create_tables()
    yield


# for no docs add ", docs_url=None, redoc_url=None"
app = FastAPI(lifespan=lifespan, title="Cekko")
templates = Jinja2Templates(directory="templates")


@app.get("/")
async def root(request: Request) -> templates.TemplateResponse:
    return templates.TemplateResponse(
        name="core.html",
        request=request,
        context={
            "title": "root",
            "details": "Root"
        }
    )
