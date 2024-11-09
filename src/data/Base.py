from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import declarative_base, sessionmaker

Base = declarative_base()

engine = create_async_engine("sqlite+aiosqlite:///database.db",
                             connect_args={"check_same_thread": False, "autocommit": True})
Session = sessionmaker(autocommit=False, autoflush=False, bind=engine)


async def create_db_and_tables():
    from ..data.Messages import Message
    from ..data.Invites import Invite
    from ..data.Channels import Channel
    from ..data.Server import Server
    from ..data.User import User
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
