from sqlalchemy import Integer
from sqlalchemy.orm import Mapped, relationship
from sqlalchemy.testing.schema import mapped_column

from ..Base import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(unique=True, index=True, nullable=False)
    email: Mapped[str] = mapped_column(unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column()

    owned_servers: Mapped[list["Server"]] = relationship("Server", back_populates="owner",
                                                         foreign_keys="Server.owner_id")
    joined_servers: Mapped[list["Server"]] = relationship(
        "Server",
        secondary="server_members",
        back_populates="members"
    )
