from datetime import timedelta

from fastapi import APIRouter, HTTPException
from fastapi.encoders import jsonable_encoder
from fastapi.params import Depends
from starlette import status
from starlette.responses import JSONResponse, Response

from .Invites import read_invite_by_link, use_invite, create_invite, Invite
from .Server import join_server, read_server
from .User import get_current_user, User
from .schemas import InviteResponse, ServerResponse, UserResponse

InviteRouter = APIRouter()


@InviteRouter.get("/")
async def read_invites_api(server_id: int, user: User = Depends(get_current_user)) -> JSONResponse:
    server = await read_server(server_id)
    if not server:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Server not found")
    if not any(user.id == server.id for user in server.members):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="You do not have permission to read this server")
    invites: list[InviteResponse] = []
    for invite in server.invites:
        invites.append(create_Invite_Response(invite))
    return JSONResponse(jsonable_encoder(invites), status_code=status.HTTP_200_OK)


@InviteRouter.post("/join/{link}")
async def use_invite_api(link: str, user: User = Depends(get_current_user)):
    invite = await read_invite_by_link(link)
    if not invite:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invite not found")
    if any(server.id == invite.server.id for server in user.joined_servers):
        raise HTTPException(status_code=status.HTTP_200_OK, detail="You have already joined this server")
    await join_server(invite.server.id, user.id)
    await use_invite(link)
    return Response(status_code=status.HTTP_200_OK)


@InviteRouter.post("/create")
async def create_invite_api(server_id: int, duration: timedelta = timedelta(weeks=2), uses: int = -1,
                            user: User = Depends(get_current_user)) -> InviteResponse:
    server = await read_server(server_id)
    if not any(member.id == user.id for member in server.members):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="You do not have permission to create a Invite for this server")
    invite = await create_invite(server_id, user.id, uses, duration)
    return create_Invite_Response(invite)


def create_Invite_Response(invite: Invite):
    return InviteResponse(
        id=invite.id,
        link=invite.link,
        uses=invite.uses,
        expire_at=invite.expire_at,
        server=ServerResponse(
            id=invite.server.id,
            name=invite.server.name,
            owner=UserResponse(
                id=invite.creator.id,
                username=invite.creator.username
            )
        ),
        creator=UserResponse(
            id=invite.creator.id,
            username=invite.creator.username
        ))
