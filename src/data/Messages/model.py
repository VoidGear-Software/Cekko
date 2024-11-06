from datetime import datetime

from sqlalchemy import ForeignKey, CheckConstraint, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..Base import Base


class Message(Base):
    __tablename__ = "messages"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    content: Mapped[str] = mapped_column(nullable=False)
    timestamp: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)

    answered_id: Mapped[int] = mapped_column(ForeignKey("messages.id"), nullable=True)
    answered: Mapped["Message"] = relationship("Message", foreign_keys=[answered_id])

    author_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    author: Mapped["User"] = relationship("User", foreign_keys=[author_id], back_populates="messages")

    recipient_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=True)
    recipient: Mapped["User"] = relationship("User", foreign_keys=[recipient_id])

    channel_id: Mapped[int] = mapped_column(ForeignKey("channels.id"), nullable=True)
    channel: Mapped["Channel"] = relationship("Channel", back_populates="messages")

    __table_args__ = (
        CheckConstraint(
            '(recipient_id IS NOT NULL AND channel_id IS NULL) OR (recipient_id IS NULL AND channel_id IS NOT NULL)',
            name='recipient_xor_channel'
        ),
        CheckConstraint(
            'author_id IS NOT recipient_id',
            name='author_not_recipient'
        ),
    )
