from sqlalchemy import insert

from .model import Server
from src.data.Base import engine
from src.data.User import User


async def create_server(name: str, owner: User):
    async with engine.connect() as conn:
        query = insert(Server).values(name=name, owner=owner, members=[owner])
        conn.execute(query)
