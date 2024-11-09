from typing import List

from sqlalchemy import ForeignKey, Table, Column
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..Base import Base


class Server(Base):
    __tablename__ = "servers"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(index=True, nullable=False)

    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    owner: Mapped["User"] = relationship(
        "User",
        back_populates="owned_servers"
    )

    invites: Mapped[List["Invite"]] = relationship(
        "Invite",
        back_populates="server",
        cascade="all, delete-orphan"
    )
    channels: Mapped[List["Channel"]] = relationship(
        "Channel",
        back_populates="server",
        cascade="all, delete-orphan"
    )
    members: Mapped[List["User"]] = relationship(
        "User",
        secondary="server_members",
        back_populates="joined_servers",
        cascade="all, delete"
    )


server_members = Table(
    "server_members",
    Base.metadata,
    Column("user_id", ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
    Column("server_id", ForeignKey("servers.id", ondelete="CASCADE"), primary_key=True)
)
