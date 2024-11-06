from sqlalchemy import insert, select, delete, update

from src.data.Base import engine
from .model import Message
from ..Server.crud import read_server_by_channel_id
from ..User import read_user_by_id
from ...logger import logger


async def create_message(content: str, author_id: int, recipient_id: int = None, channel_id: int = None,
                         answered_id: int = None) -> Message:
    if ((recipient_id is not None or channel_id is None)
            and (recipient_id is None or channel_id is not None)
            and await _Validation.is_valid_answer_dm(answered_id, recipient_id, answered_id)):
        query = insert(Message).values(content=content, author_id=author_id, recipient_id=recipient_id,
                                       channel_id=channel_id, answer_id=answered_id)
    else:
        raise ValueError("Cant send message to channel and person")
    async with engine.connect() as conn:
        result = await conn.execute(query)
        logger.debug("Created Message")
        return await result.fetchone()


async def read_message_for_dm(author_id: int, recipient_id: int, offset: int = 0, limit: int = 10) -> list[Message]:
    async with engine.connect() as conn:
        query = (select([Message]).where(Message.author_id is author_id and Message.recipient_id is recipient_id)
                 .order_by(Message.timestamp.desc())
                 .offset(offset)
                 .limit(limit))
        result = await conn.execute(query)
        return await result.fetchall()


async def read_message_for_channel(channel_id: int, offset: int = 0, limit: int = 10) -> list[Message]:
    async with engine.connect() as conn:
        query = (select([Message]).where(Message.channel_id is channel_id)
                 .order_by(Message.timestamp.desc())
                 .offset(offset)
                 .limit(limit))
        result = await conn.execute(query)
        return result.fetchall()


async def read_message_by_id(message_id: int) -> Message:
    async with engine.connect() as conn:
        query = select(Message).where(Message.id == message_id)
        result = await conn.execute(query)
        return await result.fetchone()


async def update_message(message_id: int, author_id: int, content: str) -> Message:
    if await _Validation.is_author(author_id, message_id) or await _Validation.is_owner_server(author_id, message_id):
        async with engine.connect() as conn:
            query = update(Message).where(Message.id == message_id).values(content=content)
            result = await conn.execute(query)
            return await result.fetchone()
    raise ValueError(f"User {author_id} is not the author of this Message: {message_id}")


async def delete_message(author_id: int, message_id: int) -> None:
    if await _Validation.is_author(author_id, message_id) or _Validation.is_owner_server(author_id, message_id):
        async with engine.connect() as conn:
            query = delete(Message).where(Message.id == message_id)
            await conn.execute(query)
    raise ValueError(f"User {author_id} is not the author of this Message: {message_id}")


class _Validation:
    @staticmethod
    async def is_author(user_id: int, message: int | Message) -> bool:
        if isinstance(message, int):
            message = await read_message_by_id(message)
        return user_id == message.author_id

    @staticmethod
    async def is_owner_server(user_id: int, message: int | Message) -> bool:
        if isinstance(message, int):
            message = await read_message_by_id(message)
        server = await read_server_by_channel_id(message.channel_id)
        owner = await read_user_by_id(server.owner_id)
        return user_id == owner.id

    @staticmethod
    async def is_valid_answer_dm(answered_id: int, recipient_id: int, author_id: int) -> bool:
        answered_message = await read_message_by_id(answered_id)
        return answered_message.author_id is not (recipient_id or author_id)

    @staticmethod
    async def is_valid_answer_channel(answered_id: int, channel_id: int) -> bool:
        answered_message = await read_message_by_id(answered_id)
        return answered_message.channel_id is channel_id
