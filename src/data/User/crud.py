from passlib.context import CryptContext
from sqlalchemy import insert, select, update, delete

from .model import User
from .schema import UserCreate
from ..Base import engine


async def create_user(user: UserCreate) -> User | bool:
    if await read_user_by_username(user.username) is not None:
        return False
    elif await read_user_by_email(user.email) is not None:
        return True
    async with engine.connect() as conn:
        hashed_password = _Security.hash_password(password=user.password)
        query = insert(User).values(
            username=user.username,
            email=user.email,
            hashed_password=hashed_password
        )
        await conn.execute(query)
        await conn.commit()
        return await read_user_by_username(user.username)


async def read_user_by_username(username: str) -> User:
    async with engine.connect() as conn:
        query = select(User).where(User.username == username)
        result = await conn.execute(query)
        return result.fetchone()


async def read_user_by_email(email: str) -> User:
    async with engine.connect() as conn:
        query = select(User).where(User.email == email)
        result = await conn.execute(query)
        return result.fetchone()


async def read_user_by_id(user_id: int) -> User:
    async with engine.connect() as conn:
        query = select(User).where(User.id == user_id)
        result = await conn.execute(query)
        return result.fetchone()


async def change_password(user_id: int, password: str):
    async with engine.connect() as conn:
        hashed_password = _Security.hash_password(password=password)
        query = update(User).where(User.id == user_id).values(hashed_password=hashed_password)
        await conn.execute(query)


async def rename_user(user_id: int, name: str):
    async with engine.connect() as conn:
        query = update(User).where(User.id == user_id).values(name=name)
        await conn.execute(query)


async def delete_user(user_id: int) -> None:
    async with engine.connect() as conn:
        query = delete(User).where(User.id == user_id)
        await conn.execute(query)


async def authenticate_user(username: str, password: str) -> User | bool:
    user: User = await read_user_by_username(username)
    if not user:
        return False
    if not _Security.verify_password(password, user.hashed_password):
        return False
    return user


class _Security:
    def __init__(self):
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    def verify_password(self, plain_password, hashed_password):
        return self.pwd_context.verify(plain_password, hashed_password)

    def hash_password(self, password):
        return self.pwd_context.hash(password)
