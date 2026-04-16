from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base
from app.models.note import Note

if TYPE_CHECKING:
    from app.models.note import Note
    from app.models.user import User


class Category(Base):
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)

    user: Mapped[User] = relationship("User", back_populates="categories")
    notes: Mapped[list[Note]] = relationship(
        "Note", back_populates="category", cascade="all, delete-orphan"
    )
