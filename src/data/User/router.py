import uuid
from typing import Annotated

from fastapi import APIRouter, HTTPException, Form
from fastapi.params import Depends
from fastapi.security import OAuth2PasswordRequestForm
from starlette.requests import Request
from starlette.responses import RedirectResponse

from .config import http_only, secure
from . import crud
from .schema import UserCreate

UserRouter = APIRouter()


@UserRouter.post("/register")
async def register(username: Annotated[str, Form()], email: Annotated[str, Form()],
                   password: Annotated[str, Form()], next: str = "/"):
    db_email = await crud.get_user_by_email(email=email)
    db_user = await crud.get_user_by_username(username=username)
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    elif db_email:
        raise HTTPException(status_code=400, detail="Email already registered")
    newUser = UserCreate(username=username, email=email, password=password)
    session_id = await crud.create_user(newUser)

    response = RedirectResponse(url=next)
    response.set_cookie(key="session_id", value=session_id, httponly=http_only, secure=secure)
    return response


@UserRouter.get("/check")
async def check_login(request: Request):
    session_id = request.cookies.get("session_id")
    if request.url.path:
        next_page = request.url.path
    else:
        next_page = "/"
    if not session_id:
        return RedirectResponse(url="/login?next=" + next_page, status_code=303)

    user = await crud.get_user_by_session_id(session_id=session_id)
    if user is not None:
        return RedirectResponse(url=request.url.path, status_code=303)
    else:
        return RedirectResponse(url="/login?next=" + next_page, status_code=303)


@UserRouter.post("/login")
async def login(next: str = "/", form: OAuth2PasswordRequestForm = Depends()):
    user = await crud.authenticate_user(form.username, form.password)
    if not user:
        raise HTTPException(status_code=401, detail="Incorrect username or password")

    session_id = str(uuid.uuid4())
    await crud.create_session(form.username, session_id)

    response = RedirectResponse(url=next, status_code=303)
    response.set_cookie(key="session_id", value=session_id, httponly=http_only, secure=secure)
    return response


@UserRouter.post("/logout")
async def logout(request: Request):
    session_id = request.cookies.get("session_id")
    if session_id:
        await crud.delete_session(session_id)

    response = RedirectResponse(url="/login", status_code=303)
    response.delete_cookie(key="session_id")
    return response
