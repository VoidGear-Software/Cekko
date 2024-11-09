from sqlalchemy import select, delete, update, insert
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from .model import Server, server_members
from ..Base import engine
from ...logger import logger


async def create_server(name: str, owner_id: int) -> int:
    async with AsyncSession(engine) as session:
        try:
            new_server = Server(name=name, owner_id=owner_id)
            session.add(new_server)
            await session.flush()

            await session.execute(
                insert(server_members).values(server_id=new_server.id, user_id=owner_id)
            )

            logger.debug(f"Created Server {name} with owner {owner_id} as first member")
            return new_server.id
        except SQLAlchemyError as e:
            logger.error(f"Error creating server: {str(e)}")
            raise


async def read_server(server_id: int) -> Server:
    async with AsyncSession(engine) as session:
        query = (select(Server)
        .where(Server.id == server_id)
        .options(
            selectinload(Server.members),
            selectinload(Server.owner),
            selectinload(Server.channels),
            selectinload(Server.invites)
        ))
        result = await session.execute(query)
        server = result.scalar_one_or_none()
        if not server:
            logger.warning(f"Server with id {server_id} not found")
            raise ValueError(f"Server with id {server_id} not found")
        return server


async def read_server_by_channel_id(channel_id: int) -> Server:
    async with AsyncSession(engine) as session:
        query = (select(Server)
        .where(Server.channels.any(id=channel_id))
        .options(
            selectinload(Server.members),
            selectinload(Server.owner),
            selectinload(Server.channels),
            selectinload(Server.invites)
        ))
        result = await session.execute(query)
        server = result.scalar_one_or_none()
        if not server:
            logger.warning(f"Server with channel id {channel_id} not found")
            raise ValueError(f"Server with channel id {channel_id} not found")
        return server


async def change_owner_server(server_id: int, new_owner_id: int):
    async with AsyncSession(engine) as session:
        try:
            query = update(Server).where(Server.id == server_id).values(owner_id=new_owner_id)
            result = await session.execute(query)
            if result.rowcount == 0:
                raise ValueError(f"Server with id {server_id} not found")
            logger.info(f"Changed owner of server {server_id} to user {new_owner_id}")
        except SQLAlchemyError as e:
            logger.error(f"Error changing server owner: {str(e)}")
            raise


async def rename_server(server_id: int, new_name: str):
    async with AsyncSession(engine) as session:
        try:
            query = update(Server).where(Server.id == server_id).values(name=new_name)
            result = await session.execute(query)
            if result.rowcount == 0:
                raise ValueError(f"Server with id {server_id} not found")
            logger.debug(f"Renamed server {server_id} to {new_name}")
        except SQLAlchemyError as e:
            logger.error(f"Error renaming server: {str(e)}")
            raise


async def delete_server(server_id: int):
    async with AsyncSession(engine) as session:
        try:
            server = await session.get(Server, server_id)
            if not server:
                raise ValueError(f"Server with id {server_id} not found")
            await session.delete(server)
            await session.flush()

            logger.debug(f"Deleted server {server_id} and all related data")
        except SQLAlchemyError as e:
            logger.error(f"Error deleting server: {str(e)}")
            raise


async def join_server(server_id: int, user_id: int):
    async with AsyncSession(engine) as session:
        try:
            server = await read_server(server_id)
            await session.execute(
                insert(server_members).values(server_id=server_id, user_id=user_id)
            )
            logger.info(f"User {user_id} joined server {server_id}")
        except SQLAlchemyError as e:
            logger.error(f"Error joining server: {str(e)}")
            raise


async def leave_server(server_id: int, user_id: int):
    async with AsyncSession(engine) as session:
        try:
            result = await session.execute(
                delete(server_members).where(
                    (server_members.c.server_id is server_id) and
                    (server_members.c.user_id is user_id)
                )
            )
            if result.rowcount == 0:
                raise ValueError(f"User {user_id} is not a member of server {server_id}")
            logger.info(f"User {user_id} left server {server_id}")
        except SQLAlchemyError as e:
            logger.error(f"Error leaving server: {str(e)}")
            raise
