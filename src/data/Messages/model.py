from sqlalchemy import ForeignKey, CheckConstraint, Table, Column
from sqlalchemy.orm import Mapped, mapped_column

from ..Base import Base


class Message(Base):
    __tablename__ = "messages"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, default=1)
    content: Mapped[str] = mapped_column(nullable=False)
    author_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)

    recipient_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=True)
    channel_id: Mapped[int] = mapped_column(ForeignKey("channels.id"), nullable=True)

    __table_args__ = (
        CheckConstraint('(recipient_id IS NOT NULL AND channel_id IS NULL AND server_id IS NULL) OR '
                        '(recipient_id IS NULL AND channel_id IS NOT NULL AND server_id IS NOT NULL)',
                        name='check_message_type'),
    )


user_messages = Table(
    "user_messages",
    Column("user_id", ForeignKey("users.id"), primary_key=True),
    Column("message_id", ForeignKey("messages.id"), primary_key=True),
    Column("message_id", ForeignKey("messages.id"), primary_key=True),
)
