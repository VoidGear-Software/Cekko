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

    invites: Mapped[list["Invite"]] = relationship(
        "Invite",
        back_populates="server",
    )
    channels: Mapped[list["Channel"]] = relationship(
        "Channel",
        back_populates="server"
    )
    members: Mapped[list["User"]] = relationship(
        "User",
        secondary="server_members",
        back_populates="joined_servers"
    )


server_members = Table(
    "server_members",
    Base.metadata,
    Column("server_id", ForeignKey("servers.id"), primary_key=True),
    Column("user_id", ForeignKey("users.id"), primary_key=True),
)