from typing import Annotated

from fastapi import APIRouter, HTTPException, Form
from fastapi.params import Query
from fastapi.requests import Request
from fastapi.responses import RedirectResponse

from src.data.schemas import UserCreate, TokenResponse, UserResponse
from .User import read_user_by_id, User
from .User.crud import authenticate_user, create_user
from .User.jwt import create_access_token

UserRouter = APIRouter()

user_example = UserResponse(id=0, username="username")


@UserRouter.get("/{user_id}", responses={
    404: {"description": "Not found"},
    200: {"description": "OK", "content": {"application/json": {"example": user_example}}},
}, response_model=UserResponse)
async def get_user_api(request: Request, user_id: int) -> UserResponse:
    user = await read_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return UserResponse(id=user.id, username=user.username)


@UserRouter.post("/register", responses={
    400: {"description": "Email/Username already registered"},
}, response_class=RedirectResponse)
async def register_api(request: Request, username: Annotated[str, Form()], email: Annotated[str, Form()],
                       password: Annotated[str, Form()], next: Annotated[str, Query] = "/") -> RedirectResponse:
    user: User = await create_user(UserCreate(username=username, password=password, email=email))
    if user is True:
        response = RedirectResponse(url="/register?next=" + next, status_code=307)
        response.set_cookie(
            key="register_error_email",
            value="Email is already registered",
            max_age=5,
            httponly=True
        )
        return response
    elif user is False:
        response = RedirectResponse(url="/register?next=" + next, status_code=307)
        response.set_cookie(
            key="register_error_username",
            value="Username is already registered",
            max_age=5,
            httponly=True
        )
        return response
    elif user:
        access_token = create_access_token(data={"sub": user.username})
        request.session['access_token'] = access_token
        return RedirectResponse(url=next, status_code=307)
    raise HTTPException(status_code=400, detail="Could not validate credentials")


@UserRouter.post("/login", responses={
    400: {"description": "Incorrect credentials"},
}, response_class=RedirectResponse)
async def login_api(request: Request, username: Annotated[str, Form()], password: Annotated[str, Form()],
                    next: Annotated[str, Query] = "/") -> RedirectResponse:
    user = await authenticate_user(username, password)
    if user is False:
        response = RedirectResponse(url="/login?next=" + next, status_code=307)
        response.set_cookie(
            key="login_error",
            value="Incorrect username or password",
            max_age=5,
            httponly=True
        )
        return response
    access_token = create_access_token(data={"sub": user.username})
    request.session['access_token'] = access_token

    return RedirectResponse(url=next, status_code=307)


@UserRouter.post("/register/jwt", responses={
    400: {"description": "Email/Username already registered"},
}, response_model=TokenResponse)
async def register_jwt_api(username: Annotated[str, Form()], email: Annotated[str, Form()],
                           password: Annotated[str, Form()]) -> TokenResponse:
    db_user = await create_user(UserCreate(username=username, password=password, email=email))
    if db_user:
        access_token = create_access_token(data={"sub": db_user.username})
        return TokenResponse(access_token=access_token, token_type="bearer")
    raise HTTPException(status_code=400, detail="Username already registered")


@UserRouter.post("/login/jwt", responses={
    400: {"description": "Incorrect credentials"},
}, response_model=TokenResponse)
async def login_jwt_api(username: Annotated[str, Form()], password: Annotated[str, Form()]) -> TokenResponse:
    user = await authenticate_user(username, password)
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    access_token = create_access_token(data={"sub": user.username})
    return TokenResponse(access_token=access_token, token_type="bearer")
