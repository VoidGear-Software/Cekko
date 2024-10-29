from fastapi import APIRouter
from starlette.templating import Jinja2Templates

from .User import UserRouter

DataAPI = APIRouter(prefix="/api")
templates = Jinja2Templates(directory="templates")

DataAPI.include_router(UserRouter, prefix="/user", tags=["user"])
