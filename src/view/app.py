from fastapi import APIRouter
from starlette.requests import Request
from starlette.responses import HTMLResponse
from starlette.templating import Jinja2Templates

ViewApp = APIRouter()
templates = Jinja2Templates(directory="templates")


@ViewApp.get("/register", response_class=HTMLResponse)
async def auth_page(request: Request, next: str = "/"):
    return templates.TemplateResponse("auth.html", {
        "request": request,
        "auth": "register",
        "next_url": next
    })


@ViewApp.get("/login", response_class=HTMLResponse)
async def auth_page(request: Request, next: str = "/"):
    return templates.TemplateResponse("auth.html", {
        "request": request,
        "auth": "login",
        "next_url": next
    })
