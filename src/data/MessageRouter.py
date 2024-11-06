from fastapi import APIRouter, WebSocket
from fastapi.params import Depends

from src.logger import logger
from .User.jwt import get_current_user
from .User.schema import User

MessageRouter = APIRouter()

connected_users = {}


@MessageRouter.websocket("/send_message")
async def websocket_endpoint(websocket: WebSocket, channel: int, server: int,
                             current_user: User = Depends(get_current_user)):
    await websocket.accept()
    for user, user_ws in connected_users.items():
        await user_ws.send_text(current_user.username + " joined")
    logger.info("WebSocket request by " + current_user.username)
    connected_users[current_user.id] = websocket

    try:
        while True:
            data = await websocket.receive_text()
            if check_message(data):
                logger.info("WebSocket received " + data)
                for user, user_ws in connected_users.items():
                    logger.info(f"{user}, {current_user.id}")
                    await user_ws.send_text(current_user.username + ": " + data)
    except Exception as e:
        logger.error(f"WebSocket error: {str(e)}")
    finally:
        del connected_users[current_user.id]


async def check_message(message: str):
    if message is None:
        return False
    return True
