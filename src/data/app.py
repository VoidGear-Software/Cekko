from fastapi import APIRouter
from starlette.templating import Jinja2Templates

from .Messages import MessageRouter
from .Server import ServerRouter
from .User import UserRouter

DataAPI = APIRouter(prefix="/api")
templates = Jinja2Templates(directory="templates")

DataAPI.include_router(UserRouter, prefix="/user", tags=["User"])
DataAPI.include_router(MessageRouter, prefix="/message", tags=["Message"])
DataAPI.include_router(ServerRouter, prefix="/server", tags=["Server"])
