from sqlalchemy import Table, Column, Integer, ForeignKey
from sqlalchemy.orm import Mapped, relationship, mapped_column

from ..Base import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(unique=True, index=True)
    email: Mapped[str] = mapped_column(unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(nullable=False)

    owned_servers: Mapped[list["Server"]] = relationship(
        "Server",
        back_populates="owner"
    )
    joined_servers: Mapped[list["Server"]] = relationship(
        "Server",
        secondary="server_members",
        back_populates="members"
    )
    messages: Mapped[list["Message"]] = relationship(
        "Message",
        back_populates="author",
        foreign_keys="[Message.author_id]"
    )


user_messages = Table(
    "user_messages",
    Base.metadata,
    Column("message_id", Integer, ForeignKey("messages.id"), primary_key=True),
    Column("user_id", Integer, ForeignKey("users.id"), primary_key=True)
)
