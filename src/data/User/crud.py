import uuid

from bcrypt import checkpw, hashpw, gensalt
from sqlalchemy import insert, select, update

from ..Base import engine
from .model import User
from .schema import UserCreate


def verify_password(user: User, password: str) -> bool:
    return checkpw(password.encode("utf8"), user.hashed_password)


def hash_password(password: str) -> bytes:
    return hashpw(password.encode("utf8"), gensalt(12))


async def authenticate_user(username: str, password: str):
    user = await get_user_by_username(username)
    if not user or not verify_password(user, password):
        return False
    return user


async def create_user(user: UserCreate) -> str:
    async with engine.connect() as conn:
        hashed_password = hash_password(password=user.password)
        session_id = str(uuid.uuid4())
        query = insert(User).values(
            username=user.username,
            email=user.email,
            hashed_password=hashed_password,
            session_id=session_id,
        )
        await conn.execute(query)
        await conn.commit()
        return session_id


async def get_user_by_username(username: str):
    async with engine.connect() as conn:
        query = select(User).where(User.username == username)
        result = await conn.execute(query)
        return result.fetchone()


async def get_user_by_email(email: str):
    async with engine.connect() as conn:
        query = select(User).where(User.email == email)
        result = await conn.execute(query)
        return result.fetchone()


async def get_user_by_session_id(session_id: str):
    if session_id is None:
        return None
    async with engine.connect() as conn:
        query = select(User).where(User.session_id == session_id)
        result = await conn.execute(query)
        return result.fetchone()


async def delete_session(session_id: str):
    async with engine.connect() as conn:
        query = update(User).where(User.session_id == session_id).values(
            session_id=""
        )
        await conn.execute(query)
        await conn.commit()


async def create_session(username: str, session_id: str):
    async with engine.connect() as conn:
        query = update(User).where(User.username == username).values(
            session_id=session_id
        )
        await conn.execute(query)
        await conn.commit()
