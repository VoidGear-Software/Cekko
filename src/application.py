from contextlib import asynccontextmanager

from attr.validators import instance_of
from fastapi import FastAPI, Depends
from starlette.requests import Request
from starlette.responses import RedirectResponse
from starlette.templating import Jinja2Templates

from .data import DataAPI, create_db_and_tables, auth_required


@asynccontextmanager
async def lifespan(application: FastAPI):
    await create_db_and_tables()
    yield


# for no docs add ", docs_url=None, redoc_url=None"
app = FastAPI(lifespan=lifespan, title="Cekko")
templates = Jinja2Templates(directory="templates")

app.include_router(DataAPI, prefix="/api", tags=["API"])


# TODO: Next -> Startpage, Protected Page & Login / Register Site (everything basic for testing)

@app.get("/protected-route")
async def protected_route(auth: dict = Depends(auth_required)):
    return {"message": "This is a protected route"}


@app.exception_handler(401)
async def unauthorized_exception_handler(request: Request, exc: Exception):
    return RedirectResponse(url=f"/login?next={request.url.path}", status_code=303)
