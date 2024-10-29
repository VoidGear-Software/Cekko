from typing import Annotated

from fastapi import APIRouter, HTTPException, Form
from fastapi.params import Depends, Query
from starlette import status
from starlette.requests import Request
from starlette.responses import RedirectResponse

from .crud import authenticate_user, create_user
from .jwt import create_access_token, get_current_user
from .schema import UserCreate, User, Token

UserRouter = APIRouter()


@UserRouter.post("/register")
async def auth_register(request: Request,
                        username: Annotated[str, Form()],
                        password: Annotated[str, Form()],
                        email: Annotated[str, Form()],
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
                            password: Annotated[str, Form()],
                            email: Annotated[str, Form()]):
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


@UserRouter.get("/me", response_model=User)
async def read_users_me(request: Request, current_user: User = Depends(get_current_user)):
    if current_user is None:
        if 'Authorization' in request.headers:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token"
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Missing Authorization header"
            )
    return current_user
