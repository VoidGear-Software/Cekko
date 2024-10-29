from typing import Annotated

from fastapi import APIRouter, HTTPException, Form
from fastapi.params import Depends
from starlette.requests import Request
from starlette.responses import RedirectResponse

from .crud import authenticate_user, create_user
from .jwt import create_access_token, get_current_active_user
from .schema import UserCreate, User

UserRouter = APIRouter()


@UserRouter.post("/register")
async def auth_register(request: Request,
                        username: Annotated[str, Form()],
                        password: Annotated[str, Form()],
                        email: Annotated[str, Form()]):
    db_user = await create_user(UserCreate(username=username, password=password, email=email))
    if db_user is True:
        raise HTTPException(status_code=400, detail="EMail already registered")
    elif db_user is False:
        raise HTTPException(status_code=400, detail="Username already registered")
    elif db_user:
        access_token = create_access_token(data={"sub": db_user.username})
        request.session['access_token'] = access_token
        return RedirectResponse(url="/", status_code=303)
    raise HTTPException(status_code=400, detail="Could not validate credentials")


@UserRouter.post("/login")
async def auth_login(request: Request,
                     username: Annotated[str, Form()],
                     password: Annotated[str, Form()]):
    user = await authenticate_user(username, password)
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    access_token = create_access_token(data={"sub": user.username})
    request.session['access_token'] = access_token
    return RedirectResponse(url="/", status_code=303)


@UserRouter.get("/me")
async def auth_get_me(current_user: Annotated[User, Depends(get_current_active_user)]) -> User:
    return current_user
