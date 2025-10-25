from .base import BaseModel

from sqlalchemy import Column, String, Boolean
from sqlalchemy.orm import relationship, Mapped, mapped_column
from typing import List, TYPE_CHECKING

if TYPE_CHECKING:
    from .chats import ChatSession
    from .auth import OTPVerification

class User(BaseModel):
    __tablename__ = "users"
    __table_args__ = {"schema": "wannabeaiops"}

    username: Mapped[str] = mapped_column(unique=True, index=True, nullable=False)
    email: Mapped[str] = mapped_column(unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(nullable=False)
    is_active: Mapped[bool] = mapped_column(default=True)

    sessions: Mapped[List["ChatSession"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    otp_verifications: Mapped[List["OTPVerification"]] = relationship(back_populates="user")