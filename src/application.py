from contextlib import asynccontextmanager

from fastapi import FastAPI, Depends
from starlette.requests import Request
from starlette.responses import RedirectResponse
from starlette.templating import Jinja2Templates

from .data import DataAPI, create_db_and_tables, auth_required
from .view import ViewApp


@asynccontextmanager
async def lifespan(application: FastAPI):
    await create_db_and_tables()
    yield


# for no docs add ", docs_url=None, redoc_url=None"
app = FastAPI(lifespan=lifespan, title="Cekko")
templates = Jinja2Templates(directory="templates")

app.include_router(DataAPI, tags=["Api"])
app.include_router(ViewApp, tags=["View"])


@app.get("/")
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/protected-route")
async def protected_route(request: Request, auth: dict = Depends(auth_required)):
    return templates.TemplateResponse("protected.html", {"request": request})


@app.exception_handler(401)
async def unauthorized_exception_handler(request: Request, exc: Exception):
    return RedirectResponse(url=f"/login?next={request.url.path}", status_code=303)
