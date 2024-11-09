import random
import string
from datetime import datetime, timedelta

from sqlalchemy import ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..Base import Base


def _generate_random_string(length=8):
    characters = string.ascii_letters + string.digits
    random_string = ''.join(random.choice(characters) for _ in range(length))
    return f"{random_string}"


class Invite(Base):
    __tablename__ = "invites"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    link: Mapped[str] = mapped_column(index=True, nullable=False, default=_generate_random_string(9))
    uses: Mapped[int] = mapped_column(nullable=False, default=-1)
    expire_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now() + timedelta(weeks=1))

    creator_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    creator: Mapped["User"] = relationship("User", foreign_keys=[creator_id])

    server_id: Mapped[int] = mapped_column(ForeignKey("servers.id"), nullable=False)
    server: Mapped["Server"] = relationship("Server", foreign_keys=[server_id], back_populates="invites")
