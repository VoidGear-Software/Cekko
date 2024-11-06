from fastapi import APIRouter
from fastapi.params import Depends

from .Server import create_server
from .User import User
from .User.jwt import get_current_user

ServerRouter = APIRouter()


@ServerRouter.post("/create")
async def create_server_api(server_name: str, user: User = Depends(get_current_user)):
    server = await create_server(server_name, user)
    return server