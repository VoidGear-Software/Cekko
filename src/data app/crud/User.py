from sqlalchemy import insert, select

from ..models import User, engine


async def create_user(username: str, email: str, hashed_password: str, full_name: str):
    async with engine.connect() as con:
        query = insert(User).values(
            username=username,
            email=email,
            hashed_password=hashed_password,
            full_name=full_name
        )
        con.execute(query)
        con.commit()


async def get_user(id: int):
    async with engine.connect() as con:
        query = select(User).where(User.id == id)
        result = await con.fetch_one(query)
        return result
