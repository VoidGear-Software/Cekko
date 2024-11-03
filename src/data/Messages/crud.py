from sqlalchemy import insert

from src.data.Base import engine
from src.data.User import User
from .model import Message


async def create_private_message(content: str, author: User, recipient: User):
    async with engine.connect() as conn:
        query = insert(Message).values(content=content, author=author, recipient=recipient)
        conn.execute(query)


async def create_server_message(content: str, author: User, channel: Channel):
    async with engine.connect() as conn:
        query = insert(Message).values(content=content, author=author, recipient=recipient)
        conn.execute(query)
