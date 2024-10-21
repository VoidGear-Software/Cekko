import uuid

from fastapi import APIRouter, HTTPException
from fastapi.params import Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from starlette.requests import Request
from starlette.responses import RedirectResponse

from .config import http_only, secure
from ..crud import User
from ..schemas import UserCreate

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


@router.post("/register")
async def register(user: UserCreate):
    db_email = await User.get_user_by_email(email=user.email)
    db_user = await User.get_user_by_username(username=user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    elif db_email:
        raise HTTPException(status_code=400, detail="Email already registered")
    session_id = await User.create_user(user)

    response = RedirectResponse(url="/")
    response.set_cookie(key="session_id", value=session_id, httponly=http_only, secure=secure)
    return response


@router.post("/check")
async def check_login(request: Request):
    session_id = request.cookies.get("session_id")
    if not session_id:
        return RedirectResponse(url="/login", status_code=303)

    user = await User.get_user_by_session_id(session_id=session_id)
    if user is not None:
        return RedirectResponse(url=request.url.path, status_code=303)
    else:
        return RedirectResponse(url="/login", status_code=303)


@router.post("/login")
async def login(request: Request, form: OAuth2PasswordRequestForm = Depends()):
    user = await User.authenticate_user(form.username, form.password)
    if not user:
        raise HTTPException(status_code=401, detail="Incorrect username or password")

    session_id = str(uuid.uuid4())
    next_url = request.query_params.get("next", "/")
    await User.create_session(form.username, session_id)

    response = RedirectResponse(url=next_url, status_code=303)
    response.set_cookie(key="session_id", value=session_id, httponly=http_only, secure=secure)
    return response


@router.post("/logout")
async def logout(request: Request):
    session_id = request.cookies.get("session_id")
    if session_id:
        await User.delete_session(session_id)

    response = RedirectResponse(url="/login", status_code=303)
    response.delete_cookie(key="session_id")
    return response
