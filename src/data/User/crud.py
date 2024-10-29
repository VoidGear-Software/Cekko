from passlib.context import CryptContext
from sqlalchemy import insert, select

from .model import User
from .schema import UserCreate
from ..Base import engine

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def hash_password(password):
    return pwd_context.hash(password)


async def authenticate_user(username: str, password: str) -> User | bool:
    user: User = await get_user_by_username(username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


async def create_user(user: UserCreate) -> User | bool:
    if await get_user_by_username(user.username) is not None:
        return False
    elif await get_user_by_email(user.email) is not None:
        return True
    async with engine.connect() as conn:
        hashed_password = hash_password(password=user.password)
        query = insert(User).values(
            username=user.username,
            email=user.email,
            hashed_password=hashed_password
        )
        await conn.execute(query)
        await conn.commit()
        return await get_user_by_username(user.username)


async def get_user_by_username(username: str) -> User:
    async with engine.connect() as conn:
        query = select(User).where(User.username == username)
        result = await conn.execute(query)
        return result.fetchone()


async def get_user_by_email(email: str) -> User:
    async with engine.connect() as conn:
        query = select(User).where(User.email == email)
        result = await conn.execute(query)
        return result.fetchone()
