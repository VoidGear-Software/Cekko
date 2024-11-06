from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

e
from ..Base import Base


class Channel(Base):
    __tablename__ = "channels"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(nullable=False)

    server_id: Mapped[int] = mapped_column(ForeignKey('servers.id'), nullable=False)
    server: Mapped["Server"] = relationship("Server", back_populates="channels")

    messages: Mapped[list["Message"]] = relationship("Message", back_populates="channel")
