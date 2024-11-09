from sqlalchemy import select, update
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.data.Base import engine
from src.data.Channels import Channel
from src.logger import logger


async def create_channel(name: str, server_id: int) -> int:
    async with AsyncSession(engine) as session:
        try:
            new_channel = Channel(name=name, server_id=server_id)
            session.add(new_channel)
            await session.flush()

            logger.debug(f"Created Channel {name} in server {server_id}")
            return new_channel.id
        except SQLAlchemyError as e:
            logger.error(f"Error creating Channel: {str(e)}")
            raise


async def read_channel(channel_id: int) -> Channel | None:
    async with AsyncSession(engine) as session:
        query = select(Channel).where(Channel.id == channel_id).options(
            selectinload(Channel.server),
            selectinload(Channel.messages)
        )
        result = await session.execute(query)
        channel = result.scalar_one_or_none()
        if not channel:
            logger.warning(f"Channel {channel_id} not found")
            raise ValueError(f"Channel {channel_id} not found")
        return channel


async def rename_channel(channel_id: int, name: str):
    async with AsyncSession(engine) as session:
        try:
            query = update(Channel).where(Channel.id == channel_id).values(name=name)
            result = await session.execute(query)
            if result.rowcount == 0:
                raise ValueError(f"Channel {channel_id} not found")
            logger.debug(f"Renamed Channel {channel_id} to {name}")
        except SQLAlchemyError as e:
            logger.error(f"Error Renaming Channel: {str(e)}")
            raise


async def delete_channel(channel_id: int):
    async with AsyncSession(engine) as session:
        try:
            channel = await session.get(Channel, channel_id)
            if not channel:
                raise ValueError(f"Channel {channel_id} not found")
            await session.delete(channel)
            await session.flush()

            logger.debug(f"Deleted Channel {channel_id}")
        except SQLAlchemyError as e:
            logger.error(f"Error Deleting Channel: {str(e)}")
            raise
