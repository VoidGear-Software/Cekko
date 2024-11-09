from typing import Annotated

from fastapi import Request, Depends, APIRouter
from fastapi.params import Query
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from src.data.schemas import UserResponse
from ..data.User.jwt import get_current_user

ViewApp = APIRouter()

templates = Jinja2Templates(directory="templates")


@ViewApp.get("/", response_class=HTMLResponse)
@ViewApp.post("/", response_class=HTMLResponse, include_in_schema=False)
async def index(request: Request, current_user: UserResponse = Depends(get_current_user)):
    ctx = {
        "request": request,
        "user": current_user
    }
    if current_user is None:
        request.session.clear()
    return templates.TemplateResponse("index.html", context=ctx)


@ViewApp.get("/login", response_class=HTMLResponse)
@ViewApp.post("/login", response_class=HTMLResponse, include_in_schema=False)
async def view_login(request: Request, next: Annotated[str, Query] = "/"):
    ctx = {
        "request": request,
        "show_login": True,
        "next": next
    }
    return templates.TemplateResponse("auth.html", context=ctx)


@ViewApp.get("/register", response_class=HTMLResponse)
@ViewApp.post("/register", response_class=HTMLResponse, include_in_schema=False)
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


@ViewApp.get("/chat", response_class=HTMLResponse)
@ViewApp.post("/chat", response_class=HTMLResponse, include_in_schema=False)
async def view_chat(request: Request, current_user: UserResponse = Depends(get_current_user)):
    ctx = {
        "request": request,
        "user": current_user
    }
    if current_user is None:
        request.session.clear()
        return RedirectResponse(url="/", status_code=303)
    return templates.TemplateResponse("chat.html", context=ctx)
