from typing import Annotated

from fastapi import APIRouter, HTTPException, Form
from fastapi.params import Query
from fastapi.requests import Request
from fastapi.responses import RedirectResponse

from .User.crud import authenticate_user, create_user
from .User.jwt import create_access_token
from .User.schema import UserCreate, Token

UserRouter = APIRouter()


@UserRouter.post("/register")
async def auth_register(request: Request,
                        username: Annotated[str, Form()],
                        email: Annotated[str, Form()],
                        password: Annotated[str, Form()],
                        next: Annotated[str, Query] = "/"):
    db_user = await create_user(UserCreate(username=username, password=password, email=email))
    if db_user is True:
        raise HTTPException(status_code=400, detail="EMail already registered")
    elif db_user is False:
        raise HTTPException(status_code=400, detail="Username already registered")
    elif db_user:
        access_token = create_access_token(data={"sub": db_user.username})
        request.session['access_token'] = access_token
        return RedirectResponse(url=next, status_code=303)
    raise HTTPException(status_code=400, detail="Could not validate credentials")


@UserRouter.post("/login")
async def auth_login(request: Request,
                     username: Annotated[str, Form()],
                     password: Annotated[str, Form()],
                     next: Annotated[str, Query] = "/"):
    user = await authenticate_user(username, password)
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    access_token = create_access_token(data={"sub": user.username})
    request.session['access_token'] = access_token
    return RedirectResponse(url=next, status_code=303)


@UserRouter.post("/register/jwt", response_model=Token)
async def auth_register_jwt(username: Annotated[str, Form()],
                            email: Annotated[str, Form()],
                            password: Annotated[str, Form()]
                            ):
    db_user = await create_user(UserCreate(username=username, password=password, email=email))
    if db_user:
        access_token = create_access_token(data={"sub": db_user.username})
        return {"access_token": access_token, "token_type": "bearer"}
    raise HTTPException(status_code=400, detail="Username already registered")


@UserRouter.post("/login/jwt", response_model=Token)
async def auth_login_jwt(username: Annotated[str, Form()],
                         password: Annotated[str, Form()]):
    user = await authenticate_user(username, password)
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}
