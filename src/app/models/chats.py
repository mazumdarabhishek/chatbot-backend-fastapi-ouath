from .base import BaseModel
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy import Column, String, ForeignKey
from typing import List, TYPE_CHECKING

if TYPE_CHECKING:
    from .user import User

class ChatSession(BaseModel):
    __tablename__ = "chat_sessions"
    __table_args__ = {"schema": "wannabeaiops"}

    user_id: Mapped[str] = mapped_column(ForeignKey("wannabeaiops.users.id"), index=True, nullable=False)
    thread_id: Mapped[str] = mapped_column(index=True, nullable=False)

    user : Mapped['User'] = relationship(back_populates="sessions")
    transcripts : Mapped[List["ChatTranscript"]] = relationship(back_populates="chat_session", cascade="all, delete-orphan")

    


class ChatTranscript(BaseModel):
    __tablename__ = "chat_transcripts"
    __table_args__ = {"schema": "wannabeaiops"}

    thread_id: Mapped[str] = mapped_column(ForeignKey("wannabeaiops.chat_sessions.id"), index=True, nullable=False)
    message: Mapped[str] = mapped_column(nullable=False)
    sender: Mapped[str] = mapped_column(nullable=False)  # e.g., 'user' or 'bot'

    chat_session: Mapped["ChatSession"] = relationship(back_populates="transcripts")