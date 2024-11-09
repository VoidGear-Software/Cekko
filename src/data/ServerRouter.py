from fastapi import APIRouter, HTTPException
from fastapi.encoders import jsonable_encoder
from fastapi.params import Depends
from starlette import status
from starlette.responses import JSONResponse

from .Server import create_server, rename_server, delete_server, read_server, Server
from .User import User
from .User.jwt import get_current_user
from .schemas import ServerResponse, UserResponse
from ..logger import logger

ServerRouter = APIRouter()


@ServerRouter.get("/{server_id}", responses={
    404: {"description": "Not found"},
    401: {"description": "Unauthorized"},
    200: {"description": "OK", "content": {"application/json": {
        "example": ServerResponse(id=0, name="server_name", owner=UserResponse(id=0, username="user_name"))}}}
}, response_class=JSONResponse)
async def get_server_api(server_id: int, user: User = Depends(get_current_user)) -> JSONResponse:
    logger.debug(user)
    if user is None:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No Authorization")
    server: Server = await read_server(server_id)
    if server is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Server not found")
    logger.debug(server.members[0].id)
    if any(member.id is server.id for member in server.members):
        server_response = ServerResponse(
            id=server.id,
            name=server.name,
            owner=UserResponse(id=server.owner.id, username=server.owner.username)
        )
        return JSONResponse(jsonable_encoder(server_response), status_code=status.HTTP_200_OK)
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="No Authorization")


@ServerRouter.post("/create", responses={
    401: {"description": "Unauthorized"},
    200: {"description": "CREATED", "content": {"application/json": {"example": {"id": 0}}}}
}, response_class=JSONResponse)
async def create_server_api(server_name: str, user: User = Depends(get_current_user)) -> JSONResponse:
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="No Authorization")
    server_id = await create_server(server_name, user.id)
    return JSONResponse({"id": server_id}, status_code=status.HTTP_200_OK)


@ServerRouter.put("/update", responses={
    404: {"description": "Not found"},
    401: {"description": "Unauthorized"},
    200: {"description": "CREATED"}
})
async def update_server_api(server_id: int, server_name: str, user: User = Depends(get_current_user)):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="No Authorization")
    server: Server = await read_server(server_id)
    if server is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Server not found")
    if user.id is server.owner.id:
        await rename_server(server_id, server_name)
        return JSONResponse("OK", status_code=status.HTTP_200_OK)
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="No Authorization")


@ServerRouter.delete("/delete", responses={
    404: {"description": "Not found"},
    401: {"description": "Unauthorized"},
    200: {"description": "OK"}
})
async def delete_server_api(server_id: int, user: User = Depends(get_current_user)):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="No Authorization")
    server: Server = await read_server(server_id)
    if server is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Server not found")
    if user.id is server.owner.id:
        await delete_server(server_id)
        return JSONResponse("OK", status_code=status.HTTP_200_OK)
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="No Authorization")
