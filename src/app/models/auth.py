from .base import BaseModel
from typing import TYPE_CHECKING
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy import Column, String, ForeignKey

if TYPE_CHECKING:
    from .user import User

class OTPVerification(BaseModel):
    
    __tablename__ = "otp_verification"
    __table_args__ = {"schema": "wannabeaiops"}

    email: Mapped[str] = mapped_column(ForeignKey("wannabeaiops.users.email"), index=True, nullable=False)
    otp_code: Mapped[str] = mapped_column(nullable=False)
    request_type: Mapped[str] = mapped_column(nullable=False)  # e.g., 'signup', 'password_reset'
    expires_at: Mapped[str] = mapped_column(nullable=False)

    user: Mapped["User"] = relationship("User", back_populates="otp_verifications")