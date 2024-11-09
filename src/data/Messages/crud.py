from sqlalchemy import select, insert, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.data.Base import engine
from .model import Message
from ..Server.crud import read_server_by_channel_id
from ...logger import logger


async def create_message(content: str, author_id: int,
                         recipient_id: int = None, channel_id: int = None,
                         answered_id: int = None) -> Message:
    async with AsyncSession(engine) as session:
        try:
            if recipient_id is not None and channel_id is None:
                # DM message
                if answered_id and not await _Validation.is_valid_answer_dm(answered_id, recipient_id, author_id):
                    raise ValueError("Invalid answer for DM")
            elif channel_id is not None and recipient_id is None:
                # Channel message
                if answered_id and not await _Validation.is_valid_answer_channel(answered_id, channel_id):
                    raise ValueError("Invalid answer for channel")
            else:
                raise ValueError("Must specify either recipient_id or channel_id, but not both")

            query = insert(Message).values(
                content=content,
                author_id=author_id,
                recipient_id=recipient_id,
                channel_id=channel_id,
                answered_id=answered_id
            )
            result = await session.execute(query)
            await session.commit()
            logger.debug("Created Message")
            return await read_message(result.inserted_primary_key[0])
        except Exception as e:
            logger.error(f"Error creating message: {str(e)}")
            raise


async def read_messages_for_dm(author_id: int, recipient_id: int, offset: int = 0, limit: int = 10) -> list[Message]:
    async with AsyncSession(engine) as session:
        query = (select(Message)
                 .where((Message.author_id is author_id) and (Message.recipient_id is recipient_id) |
                        (Message.author_id is recipient_id) and (Message.recipient_id is author_id))
                 .order_by(Message.timestamp.desc())
                 .offset(offset)
                 .limit(limit))
        result = await session.execute(query)
        return list(result.scalars().all())


async def read_messages_for_channel(channel_id: int, offset: int = 0, limit: int = 10) -> list[Message]:
    async with AsyncSession(engine) as session:
        query = (select(Message)
                 .where(Message.channel_id == channel_id)
                 .order_by(Message.timestamp.desc())
                 .offset(offset)
                 .limit(limit))
        result = await session.execute(query)
        return list(result.scalars().all())


async def read_message(message_id: int) -> Message:
    async with AsyncSession(engine) as session:
        query = select(Message).where(Message.id == message_id).options(
            selectinload(Message.author),
            selectinload(Message.channel),
            selectinload(Message.recipient),
            selectinload(Message.answered),
        )
        result = await session.execute(query)
        message = result.scalar_one_or_none()
        if not message:
            raise ValueError(f"Message with id {message_id} not found")
        return message


async def update_message(message_id: int, author_id: int, content: str) -> Message:
    async with AsyncSession(engine) as session:
        message = await read_message(message_id)
        if not await _Validation.can_modify_message(author_id, message):
            raise ValueError(f"User {author_id} is not authorized to update this message")

        query = update(Message).where(Message.id == message_id).values(content=content)
        await session.execute(query)
        await session.commit()
        return await read_message(message_id)


async def delete_message(author_id: int, message_id: int):
    async with AsyncSession(engine) as session:
        message = await read_message(message_id)
        if not await _Validation.can_modify_message(author_id, message):
            raise ValueError(f"User {author_id} is not authorized to delete this message")

        query = delete(Message).where(Message.id == message_id)
        await session.execute(query)
        await session.commit()


class _Validation:
    @staticmethod
    async def is_author(user_id: int, message: Message) -> bool:
        return user_id == message.author_id

    @staticmethod
    async def is_owner_server(user_id: int, message: Message) -> bool:
        if not message.channel_id:
            return False
        server = await read_server_by_channel_id(message.channel_id)
        return user_id == server.owner_id

    @staticmethod
    async def can_modify_message(user_id: int, message: Message) -> bool:
        return await _Validation.is_author(user_id, message) or await _Validation.is_owner_server(user_id, message)

    @staticmethod
    async def is_valid_answer_dm(answered_id: int, recipient_id: int, author_id: int) -> bool:
        answered_message = await read_message(answered_id)
        return answered_message.author_id not in (recipient_id, author_id)

    @staticmethod
    async def is_valid_answer_channel(answered_id: int, channel_id: int) -> bool:
        answered_message = await read_message(answered_id)
        return answered_message.channel_id == channel_id
