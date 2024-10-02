from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import declarative_base

Base = declarative_base()

engine = create_async_engine("sqlite+aiosqlite:///databank.db")


async def create_tables():
    with engine.begin() as conn:
        conn.run_sync(Base.metadata.create_all)
