from dotenv import load_dotenv
from sqlalchemy import Column, String, Uuid, select, insert
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import declarative_base

load_dotenv()

Base = declarative_base()
engine = create_async_engine("sqlite+aiosqlite:///./databank.db")


async def create_db_and_tables():
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)


class SoftwareDB:
    class Software(Base):
        name = 'software'
        metadata = Base.metadata
        id = Column(Uuid, primary_key=True, unique=True, nullable=False)
        sw_name = Column(String, nullable=False, unique=True)
        url = Column(String, nullable=False)

    async def add(self, uuid: str, name: str, url: str):
        async with engine.connect() as conn:
            query = insert(self.Software).values(id=uuid, full_name=name, url=url)
            await conn.execute(query)

    async def get_all(self):
        async with engine.connect() as conn:
            query = select([self.Software])
            result = await conn.execute(query)
            return result

    async def get_one(self, software_id):
        async with engine.connect() as conn:
            query = select([self.Software]).where(self.Software.id == software_id)
            result = await conn.execute(query)
            return result
