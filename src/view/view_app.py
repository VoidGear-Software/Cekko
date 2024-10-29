from typing import Annotated

from fastapi import Request, Depends, APIRouter
from fastapi.params import Query
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from starlette.responses import RedirectResponse

from ..data.User.jwt import get_current_user
from ..data.User.schema import User

ViewApp = APIRouter()

templates = Jinja2Templates(directory="templates")


@ViewApp.get("/", response_class=HTMLResponse)
async def index(request: Request, current_user: User = Depends(get_current_user)):
    ctx = {
        "request": request,
        "user": current_user
    }
    return templates.TemplateResponse("index.html", context=ctx)


@ViewApp.get("/login", response_class=HTMLResponse)
async def view_login(request: Request, next: Annotated[str, Query] = "/"):
    ctx = {
        "request": request,
        "show_login": True,
        "next": next
    }
    return templates.TemplateResponse("auth.html", context=ctx)


@ViewApp.get("/register", response_class=HTMLResponse)
async def view_register(request: Request, next: Annotated[str, Query] = "/"):
    ctx = {
        "request": request,
        "show_login": False,
        "next": next
    }
    return templates.TemplateResponse("auth.html", context=ctx)


@ViewApp.post("/logout")
async def view_logout(request: Request):
    request.session.clear()
    return RedirectResponse(url="/", status_code=303)
