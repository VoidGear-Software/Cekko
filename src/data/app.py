from fastapi import APIRouter
from starlette.templating import Jinja2Templates

from .ChannelRouter import ChannelRouter
from .InviteRouter import InviteRouter
from .MessageRouter import MessageRouter
from .ServerRouter import ServerRouter
from .UserRouter import UserRouter

DataAPI = APIRouter(prefix="/api")
templates = Jinja2Templates(directory="templates")

DataAPI.include_router(MessageRouter, prefix="/message", tags=["Message"])
DataAPI.include_router(UserRouter, prefix="/user", tags=["User"])
DataAPI.include_router(ServerRouter, prefix="/server", tags=["Server"])
DataAPI.include_router(ChannelRouter, prefix="/channel", tags=["Channel"])
DataAPI.include_router(InviteRouter, prefix="/invite", tags=["Invite"])
