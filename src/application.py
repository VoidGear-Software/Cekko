import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from starlette.middleware.sessions import SessionMiddleware
from starlette.requests import Request
from starlette.responses import RedirectResponse
from starlette.staticfiles import StaticFiles

from .data import DataAPI, create_db_and_tables
from .view import ViewApp


@asynccontextmanager
async def lifespan(application: FastAPI):
    await create_db_and_tables()
    yield


app = FastAPI(lifespan=lifespan, title="Cekko")

app.include_router(DataAPI, tags=["Api"])
app.include_router(ViewApp, tags=["View"])

app.add_middleware(SessionMiddleware, secret_key=os.getenv("SESSION_SECRET"))
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.exception_handler(401)
async def unauthorized_exception_handler(request: Request, exc: Exception):
    return RedirectResponse(url=f"/login?next={request.url.path}", status_code=303)
