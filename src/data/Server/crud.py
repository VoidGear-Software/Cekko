from sqlalchemy import insert, select, delete, update

from .model import Server
from ..Base import engine
from ...logger import logger


async def create_server(name: str, owner_id: int):
    async with engine.connect() as conn:
        query = insert(Server).values(name=name, owner_id=owner_id)
        logger.debug(f"Created Server {name}")
        await conn.execute(query)


async def read_server(server_id: int) -> Server:
    async with engine.connect() as conn:
        query = select(Server).where(Server.id == server_id)
        result = await conn.execute(query)
        return await result.fetchone()


async def read_server_by_channel_id(channel_id) -> Server:
    async with engine.connect() as conn:
        query = select(Server).where(Server.channels.has(channel_id))
        result = await conn.execute(query)
        return await result.fetchone()


async def change_owner_server(server_id: int, owner_id: int):
    async with engine.connect() as conn:
        query = update(Server).where(Server.id == server_id).values(owner_id=owner_id)
        await conn.execute(query)


async def rename_server(server_id: int, name: str):
    async with engine.connect() as conn:
        query = update(Server).where(Server.id == server_id).values(name=name)
        await conn.execute(query)


async def delete_server(server_id: int):
    async with engine.connect() as conn:
        await conn.execute(delete(Server).where(Server.id == server_id))


async def join_server(server_id: int, user_id: int):
    server = await read_server(server_id)
    members = server.members.append(user_id)
    async with engine.connect() as conn:
        query = update(Server).where(Server.id == server_id).values(members=members)
        await conn.execute(query)


async def leave_server(server_id: int, user_id: int):
    server = await read_server(server_id)
    members = server.members.remove(user_id)
    async with engine.connect() as conn:
        query = update(Server).where(Server.id == server_id).values(members=members)
        await conn.execute(query)
