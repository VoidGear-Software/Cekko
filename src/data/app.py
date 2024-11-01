from fastapi import APIRouter
from starlette.templating import Jinja2Templates

from .Chat import ChatRouter
from .User import UserRouter

DataAPI = APIRouter(prefix="/api")
templates = Jinja2Templates(directory="templates")

DataAPI.include_router(UserRouter, prefix="/user", tags=["user"])
DataAPI.include_router(ChatRouter, prefix="/chat", tags=["chat"])
