import datetime
from datetime import datetime as datetime_

from sqlalchemy import insert, select, delete, update

from .model import Invite
from ..Base import engine
from ..Server import Server
from ...logger import logger


async def create_invite(creator_id: int, server_id: int, uses: int = -1, duration: datetime = None) -> Invite:
    async with engine.connect() as conn:
        query = insert(Invite).values(creator_id=creator_id, server_id=server_id, uses=uses, duration=duration)
        await conn.execute(query)
        query = select(Invite).where(
            Invite.creator_id == creator_id,
            Invite.server_id == server_id,
            Invite.uses == uses,
            Invite.duration == duration
        )
        result = await conn.execute(query)
        invite = await result.fetchone()
        logger.debug(f"Created Invite {invite} with link {invite.link}")
        return invite


async def read_invite_by_id(invite_id: int) -> Invite:
    async with engine.connect() as conn:
        query = select(Invite).where(Invite.id == invite_id)
        result = await conn.execute(query)
        return await result.fetchone()


async def read_invite_by_link(link: str) -> Invite:
    async with engine.connect() as conn:
        query = select(Invite).where(Invite.link == link)
        result = await conn.execute(query)
        return await result.fetchone()


async def use_invite(link: str) -> Server:
    invite = await read_invite_by_link(link)
    if _Validation.is_link_valid(link):
        async with engine.connect() as conn:
            query = update(Invite).where(Invite.link == link).values(uses=(invite.uses - 1))
            result = await conn.execute(query)
            invite = await result.fetchone()

            if invite.uses is 0:
                await delete_invite(invite_id=invite.id)
                logger.debug(f"Deleted Invite {invite} | Reason: Invite expired")

            query = select(Server).where(Server.id == invite.server_id)
            result = await conn.execute(query)
            logger.debug(f"Created Invite {invite}")
            return await result.fetchone()


async def delete_invite(invite_id: int) -> None:
    async with engine.connect() as conn:
        query = delete(Invite).where(Invite.id == invite_id)
        await conn.execute(query)


class _Validation:

    @staticmethod
    async def is_link_valid(link: str) -> bool:
        invite = await read_invite_by_link(link)
        if invite.duration >= datetime_.now():
            await delete_invite(invite_id=invite.id)
            logger.debug(f"Deleted Invite {invite} | Reason: Invite expired")
            return False
        if invite.uses is 0:
            await delete_invite(invite_id=invite.id)
            logger.debug(f"Deleted Invite {invite} | Reason: Invite used")
            return False
        return True
