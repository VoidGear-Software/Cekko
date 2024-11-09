import asyncio
import json
from datetime import datetime
from typing import List, Dict

from fastapi import APIRouter, HTTPException, Request
from fastapi.encoders import jsonable_encoder
from fastapi.params import Depends
from sse_starlette.sse import EventSourceResponse
from starlette import status
from starlette.responses import JSONResponse

from src.data.schemas import UserResponse, MessageResponse
from src.logger import logger
from .Channels import read_channel
from .Messages import Message
from .Messages.crud import read_messages_for_channel, read_messages_for_dm, read_message, update_message, create_message
from .Server import read_server_by_channel_id
from .User import User, get_current_user, read_user_by_id

MessageRouter = APIRouter()

user_connections: Dict[int, List[asyncio.Queue]] = {}

message_example: List[MessageResponse] = [MessageResponse(
    id=0,
    content="Message 1",
    timestamp=datetime.now(),
    author=UserResponse(id=0, username="User 1"),
    answered_id=None
), MessageResponse(
    id=1,
    content="Message 2",
    timestamp=datetime.now(),
    author=UserResponse(id=1, username="User 2"),
    answered_id=0
)]


@MessageRouter.get("/ch", responses={
    404: {"description": "Not found"},
    200: {"description": "OK", "content": {"application/json": {"example": message_example}}},
}, response_model=list[MessageResponse])
async def get_messages_channel_api(channel_id: int, offset: int = 0, limit: int = 10,
                                   user: User = Depends(get_current_user)) -> JSONResponse:
    try:
        channel = await read_channel(channel_id)
        server = await read_server_by_channel_id(channel_id)
        if not any(member.id == user.id for member in server.members):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not Authorized")
        messages = await read_messages_for_channel(channel_id=channel_id, offset=offset, limit=limit)
        response: list[MessageResponse] = []
        for message in messages:
            response.append(MessageResponse(
                id=message.id,
                content=message.content,
                timestamp=message.timestamp,
                author=message.author,
                answered_id=message.answered_id
            ))
        return JSONResponse(jsonable_encoder(response), status_code=status.HTTP_200_OK)
    except Exception as e:
        logger.error(f"{str(e)}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Channel not found")


@MessageRouter.get("/dm", responses={
    404: {"description": "Not found"},
    200: {"description": "OK", "content": {"application/json": {"example": message_example}}},
}, response_model=list[MessageResponse])
async def get_messages_channel_api(recipient_id: int, offset: int = 0, limit: int = 10,
                                   user: User = Depends(get_current_user)) -> JSONResponse:
    try:
        recipient: User = await read_user_by_id(recipient_id)
        messages: list[Message] = await read_messages_for_dm(author_id=user.id,
                                                             recipient_id=recipient.id,
                                                             offset=offset, limit=limit)
        response: list[MessageResponse] = []
        for message in messages:
            response.append(MessageResponse(
                id=message.id,
                content=message.content,
                timestamp=message.timestamp,
                author=message.author,
                answered_id=message.answered_id,
            ))
        return JSONResponse(jsonable_encoder(response), status_code=status.HTTP_200_OK)
    except Exception as e:
        logger.error(f"{str(e)}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Channel not found")


@MessageRouter.put("/update")
async def update_message_api(message_id: int, content: str, user: User = Depends(get_current_user)) -> JSONResponse:
    message: Message = await read_message(message_id)
    if not message.author.id != user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not Authorized")
    updated_message: Message = await update_message(message.id, user.id, content)
    return JSONResponse(jsonable_encoder(updated_message), status_code=status.HTTP_200_OK)


@MessageRouter.post("/dm/send_message")
async def send_message_dm_api(content: str, recipient_id: int, answered_id: int = None,
                              user: User = Depends(get_current_user)) -> JSONResponse:
    try:
        recipient: User = await read_user_by_id(recipient_id)
        message = await create_message(content=content, author_id=user.id, answered_id=answered_id,
                                       recipient_id=recipient.id)

        for user_id in [user.id, recipient_id]:
            if user_id in user_connections:
                for queue in user_connections[user_id]:
                    await queue.put({
                        "type": "dm_message",
                        "other_user_id": user.id if user_id == recipient_id else recipient_id,
                        "message": jsonable_encoder(message)
                    })

        return JSONResponse(jsonable_encoder(message), status_code=status.HTTP_200_OK)
    except Exception as e:
        logger.error(f"Error creating message: {str(e)}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Recipient not found")


@MessageRouter.post("/ch/send_message")
async def send_message_ch_api(content: str, channel_id: int, answered_id: int = None,
                              user: User = Depends(get_current_user)) -> JSONResponse:
    try:
        channel = await read_channel(channel_id)
        server = await read_server_by_channel_id(channel_id)
        if not any(member.id == user.id for member in server.members):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not Authorized")
        message = await create_message(content=content, author_id=user.id, answered_id=answered_id,
                                       channel_id=channel_id)

        # Notify all users in the channel
        for member in server.members:
            if member.id in user_connections:
                for queue in user_connections[member.id]:
                    await queue.put({
                        "type": "channel_message",
                        "channel_id": channel_id,
                        "message": jsonable_encoder(message)
                    })
    except Exception as e:
        logger.error(f"{str(e)}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Channel not found")


@MessageRouter.get("/stream")
async def stream_user_messages(request: Request, user: User = Depends(get_current_user)):
    async def event_generator():
        if user.id not in user_connections:
            user_connections[user.id] = []

        queue = asyncio.Queue()
        user_connections[user.id].append(queue)

        try:
            while True:
                if await request.is_disconnected():
                    break

                message = await queue.get()
                logger.info(user_connections)
                yield json.dumps(message)
        except asyncio.CancelledError:
            pass
        finally:
            user_connections[user.id].remove(queue)
            if not user_connections[user.id]:
                del user_connections[user.id]

    return EventSourceResponse(event_generator())


async def check_message(message: str):
    if message is None:
        return False
    return True
