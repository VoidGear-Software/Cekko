from sqlalchemy import insert, select, update, delete

from src.data.Base import engine
from src.data.Channels import Channel


async def create_channel(name: str, server_id: int):
    async with engine.connect() as conn:
        query = insert(Channel).values(name=name, server_id=server_id)
        await conn.execute(query)


async def read_channel(channel_id: int) -> Channel:
    async with engine.connect() as conn:
        query = select(Channel).where(Channel.id == channel_id)
        result = await conn.execute(query)
        return result.fetchone()


async def rename_channel(channel_id: int, name: str):
    async with engine.connect() as conn:
        query = update(Channel).where(Channel.id == channel_id).values(name=name)
        await conn.execute(query)


async def delete_channel(channel_id: int):
    async with engine.connect() as conn:
        query = delete(Channel).where(Channel.id == channel_id)
        await conn.execute(query)
