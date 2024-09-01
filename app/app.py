from contextlib import asynccontextmanager

from fastapi import FastAPI
from starlette.requests import Request
from starlette.templating import Jinja2Templates

from .routers import software_router, chat_router, file_router


@asynccontextmanager
async def lifespan(application: FastAPI):
    yield


# for no docs add ", docs_url=None, redoc_url=None"
app = FastAPI(lifespan=lifespan, title="Cekko")
templates = Jinja2Templates(directory="templates")

app.include_router(software_router)
app.include_router(chat_router)
app.include_router(file_router)


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
