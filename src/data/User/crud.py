from passlib.context import CryptContext
from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from .model import User
from ..Base import engine
from ..schemas import UserCreate

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def hash_password(password):
    return pwd_context.hash(password)


async def create_user(user: UserCreate) -> User | bool:
    async with AsyncSession(engine) as session:
        if await read_user_by_username(user.username) is not None:
            return False
        elif await read_user_by_email(user.email) is not None:
            return True

        hashed_password = hash_password(password=user.password)
        new_user = User(
            username=user.username,
            email=user.email,
            hashed_password=hashed_password
        )
        session.add(new_user)
        await session.flush()
        return new_user


async def read_user_by_username(username: str) -> User | None:
    async with AsyncSession(engine) as session:
        query = (
            select(User)
            .where(User.username == username)
            .options(
                selectinload(User.joined_servers),
                selectinload(User.messages),
                selectinload(User.owned_servers)
            )
        )
        result = await session.execute(query)
        return result.scalar_one_or_none()


async def read_user_by_email(email: str) -> User | None:
    async with AsyncSession(engine) as session:
        query = (
            select(User)
            .where(User.email == email)
            .options(
                selectinload(User.joined_servers),
                selectinload(User.messages),
                selectinload(User.owned_servers)
            )
        )
        result = await session.execute(query)
        return result.scalar_one_or_none()


async def read_user_by_id(user_id: int) -> User | None:
    async with AsyncSession(engine) as session:
        query = (
            select(User)
            .where(User.id == user_id)
            .options(
                selectinload(User.joined_servers),
                selectinload(User.messages),
                selectinload(User.owned_servers)
            )
        )
        result = await session.execute(query)
        return result.scalar_one_or_none()


async def change_password(user_id: int, password: str):
    async with AsyncSession(engine) as session:
        hashed_password = hash_password(password=password)
        query = update(User).where(User.id == user_id).values(hashed_password=hashed_password)
        await session.execute(query)


async def rename_user(user_id: int, name: str):
    async with AsyncSession(engine) as session:
        query = update(User).where(User.id == user_id).values(name=name)
        await session.execute(query)


async def delete_user(user_id: int) -> None:
    async with AsyncSession(engine) as session:
        query = delete(User).where(User.id == user_id)
        await session.execute(query)


async def authenticate_user(username: str, password: str) -> User | bool:
    async with AsyncSession(engine) as session:
        user = await read_user_by_username(username)
        if not user:
            return False
        if not verify_password(password, user.hashed_password):
            return False
        return user
