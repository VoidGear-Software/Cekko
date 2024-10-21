from fastapi import APIRouter, HTTPException
from starlette.requests import Request
from starlette.responses import RedirectResponse
from starlette.templating import Jinja2Templates

from .router import UserRouter, check_login

DataAPI = APIRouter(prefix="/api")
templates = Jinja2Templates(directory="templates")

DataAPI.include_router(UserRouter, tags=["user"])


async def auth_required(request: Request):
    auth_result = await check_login(request)
    if isinstance(auth_result, RedirectResponse):
        if auth_result.headers["location"] != request.url.path:
            raise HTTPException(status_code=401, detail="Unauthorized")
    return auth_result
