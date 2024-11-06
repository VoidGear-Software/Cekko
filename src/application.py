import os
from contextlib import asynccontextmanager
from http.client import HTTPException

from fastapi import FastAPI
from ratelimit import RateLimitMiddleware, Rule
from ratelimit.auths import EmptyInformation
from ratelimit.backends.simple import MemoryBackend
from ratelimit.types import Scope, Receive, Send
from starlette.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from starlette.requests import Request
from starlette.responses import RedirectResponse
from starlette.staticfiles import StaticFiles

from .data import DataAPI, create_db_and_tables
from .data.User.jwt import get_current_user
from .view import ViewApp


@asynccontextmanager
async def lifespan(application: FastAPI):
    await create_db_and_tables()
    yield


app = FastAPI(lifespan=lifespan, title="Cekko")

app.include_router(DataAPI, tags=["Api"])
app.include_router(ViewApp, tags=["View"])

app.mount("/static", StaticFiles(directory="static"), name="static")


def blocked_page(retry_after: int):
    async def block_status_429(scope: Scope, receive: Receive, send: Send) -> None:
        await send({"type": "http.response.start", "status": 429})
        await send(
            {
                "type": "http.response.body",
                "body": b"custom 429 page",
                "more_body": False,
            }
        )

    return block_status_429


async def ratelimit_auth(scope: Scope) -> [str, str]:
    return 0, "default"

app.add_middleware(SessionMiddleware, secret_key=os.getenv("SESSION_SECRET"))
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"],
                   allow_headers=["*"])
app.add_middleware(RateLimitMiddleware, backend=MemoryBackend(), authenticate=ratelimit_auth,
                   on_blocked=blocked_page(60), config={
        r"^/api/user": [
            Rule(second=15)
        ],
        r"^/api/message": [
            Rule(second=2)
        ],
    })


@app.exception_handler(400)
async def unauthorized_exception_handler(request: Request, exc: Exception):
    return RedirectResponse(url=f"/login?next=" + request.url.path, status_code=303)
