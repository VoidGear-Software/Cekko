from datetime import datetime, timedelta
from typing import Optional

from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from .model import Invite
from ..Base import engine
from ..Server.model import Server
from ...logger import logger


async def create_invite(creator_id: int, server_id: int, uses: int = -1,
                        duration: Optional[timedelta] = None) -> Invite:
    async with AsyncSession(engine) as session:
        expire_at = datetime.now() + (duration or timedelta(weeks=1))

        try:
            new_invite = Invite(
                creator_id=creator_id,
                server_id=server_id,
                uses=uses,
                expire_at=expire_at
            )
            session.add(new_invite)
            await session.flush()

            query = (
                select(Invite)
                .where(Invite.id == new_invite.id)
                .options(
                    selectinload(Invite.server),
                    selectinload(Invite.creator)
                )
            )
            result = await session.execute(query)
            loaded_invite = result.scalar_one()

            logger.debug(f"Created Invite {loaded_invite.id} for Server {server_id}")
            return loaded_invite
        except SQLAlchemyError as e:
            logger.warning(f"Error creating invite: {str(e)}")
            raise


async def read_invite_by_id(invite_id: int) -> Invite:
    async with AsyncSession(engine) as session:
        query = select(Invite).where(Invite.id == invite_id).options(
            selectinload(Invite.server),
            selectinload(Invite.creator),
        )
        result = await session.execute(query)
        return result.scalar_one_or_none()


async def read_invite_by_link(link: str) -> Invite:
    async with AsyncSession(engine) as session:
        query = select(Invite).where(Invite.link == link).options(
            selectinload(Invite.server),
            selectinload(Invite.creator),
        )
        result = await session.execute(query)
        return result.scalar_one_or_none()


async def use_invite(link: str) -> Server | None:
    invite = await read_invite_by_link(link)
    if not invite or not await _Validation.is_link_valid(invite):
        return None

    async with AsyncSession(engine) as session:
        invite.uses -= 1
        if invite.uses == 0:
            await session.delete(invite)
            logger.debug(f"Deleted Invite {invite} | Reason: All uses exhausted")
        else:
            await session.merge(invite)

        query = select(Server).where(Server.id == invite.server_id)
        result = await session.execute(query)
        server = result.scalar_one_or_none()

        await session.commit()
        logger.debug(f"Used Invite {invite}")
        return server


async def delete_invite(invite_id: int) -> None:
    async with AsyncSession(engine) as session:
        invite = await session.get(Invite, invite_id)
        if invite:
            await session.delete(invite)
            await session.commit()
            logger.debug(f"Deleted Invite {invite}")
        else:
            logger.warning(f"Attempted to delete non-existent invite with id {invite_id}")


class _Validation:
    @staticmethod
    async def is_link_valid(invite: Invite) -> bool:
        if invite.expire_at and invite.expire_at <= datetime.utcnow():
            await delete_invite(invite.id)
            logger.debug(f"Deleted Invite {invite} | Reason: Invite expired")
            return False
        if invite.uses == 0:
            await delete_invite(invite.id)
            logger.debug(f"Deleted Invite {invite} | Reason: No uses left")
            return False
        return True
