from typing import Annotated

from fastapi import Request, Depends, APIRouter
from fastapi.params import Query
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

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
    if current_user is None:
        request.session.clear()
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


@ViewApp.get("/chat")
async def view_chat(request: Request, current_user: User = Depends(get_current_user)):
    ctx = {
        "request": request,
        "user": current_user
    }
    if current_user is None:
        request.session.clear()
        return RedirectResponse(url="/", status_code=303)
    return templates.TemplateResponse("chat.html", context=ctx)
