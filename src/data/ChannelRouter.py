from fastapi import APIRouter, HTTPException
from fastapi.params import Depends
from starlette import status
from starlette.requests import Request
from starlette.responses import Response

from .Channels import read_channel, create_channel, delete_channel, rename_channel
from .Server import read_server, read_server_by_channel_id
from .User import User, get_current_user
from .schemas import ChannelResponse

ChannelRouter = APIRouter()


@ChannelRouter.get("/{channel_id}", responses={
    404: {"description": "Not found"},
    200: {"description": "OK",
          "content": {"application/json": {"example": ChannelResponse(id=0, name="channel_name", server_id=0)}}}
}, response_model=ChannelResponse)
async def get_channel_api(channel_id: int):
    channel = await read_channel(channel_id)
    if not channel:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Channel not found")
    return ChannelResponse(id=channel.id, name=channel.name, server_id=channel.server_id)


@ChannelRouter.post("/create", responses={
    403: {"description": "Forbidden"},
    404: {"description": "Not found"},
    200: {"description": "CREATED"}
}, response_class=Response)
async def create_channel_api(request: Request, name: str, server_id: int,
                             user: User = Depends(get_current_user)) -> Response:
    server = await read_server(server_id)
    if not server:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Server not found")
    if server.owner_id != user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not Authorized")
    channel_id = await create_channel(name=name, server_id=server_id)
    return Response(status_code=status.HTTP_200_OK)


@ChannelRouter.put("/update", responses={
    403: {"description": "Forbidden"},
    404: {"description": "Not found"},
    200: {"description": "UPDATED"}
}, response_class=Response)
async def update_channel_api(request: Request, channel_name: str, channel_id: int,
                             user: User = Depends(get_current_user)) -> Response:
    await check_permissions(channel_id, user)

    await rename_channel(channel_id, channel_name)
    return Response(status_code=status.HTTP_200_OK)


@ChannelRouter.delete("/delete", responses={
    403: {"description": "Forbidden"},
    404: {"description": "Not found"},
    200: {"description": "DELETED"}
})
async def delete_channel_api(channel_id: int, user: User = Depends(get_current_user)) -> Response:
    await check_permissions(channel_id, user)

    await delete_channel(channel_id)
    return Response(status_code=status.HTTP_200_OK)


async def check_permissions(channel_id: int, user: User):
    channel = await read_channel(channel_id)
    server = await read_server_by_channel_id(channel_id)

    if not channel:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Channel not found")
    elif not server:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Server not found")
    elif server.owner_id != user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not Authorized")
