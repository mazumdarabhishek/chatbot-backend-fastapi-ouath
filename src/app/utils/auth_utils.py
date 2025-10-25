from passlib.context import CryptContext
import jwt
import string
import secrets
from typing import Optional
from datetime import datetime, timedelta, timezone
from fastapi import status
from app.models.auth import OTPVerification
from app.schemas.common import APIResponse
from app.core.config import settings
from uuid import uuid4


from app.core.app_logger import setup_daily_logger
import traceback
logger = setup_daily_logger("auth_services")

SPECIAL_CHARACTERS = ['@', '#', '$', '%', '=', ':', '?', '.', '/', '|', '~', '>']

def is_password_strong_enough(password: str) -> bool:
    if len(password) < 8:
        return False

    if not any(char.isupper() for char in password):
        return False

    if not any(char.islower() for char in password):
        return False

    if not any(char.isdigit() for char in password):
        return False

    if not any(char in SPECIAL_CHARACTERS for char in password):
        return False

    return True

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(plain_password):
    return pwd_context.hash(plain_password)

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def generate_otp(length: int = settings.otp_length) -> str:

    characters = string.digits

    otp = ''.join(secrets.choice(characters) for _ in range(length))

    return otp.zfill(length)


async def create_and_store_otp(session, email: str, request_type: str) -> int:

    existing_record = session.query(OTPVerification).filter(OTPVerification.email == email).first()
    cooldown_period = timedelta(seconds = settings.otp_cooldown_period_seconds)
    now = datetime.now()
    
    if existing_record and (now - existing_record.created_at) < cooldown_period:
        logger.info(f"OTP request for {email} denied due to cooldown period.")
        return APIResponse(
            status=status.HTTP_429_TOO_MANY_REQUESTS,
            message = "OTP already requested for email less than 30 seconds ago. Please wait before requesting a new one.",
            data = None
        )

    else:
    
        otp = generate_otp()
        expires_at = datetime.now(timezone.utc) + timedelta(minutes=10)
        
        try:
            if existing_record:
                existing_record.otp_code = otp
                existing_record.created_at = now # Update the creation time
                existing_record.expires_at = expires_at
                existing_record.request_type = request_type
                session.add(existing_record)
                session.commit()
            else:
                new_otp_record = OTPVerification(
                    id=str(uuid4()),
                    email=email,
                    otp_code=otp,
                    expires_at=expires_at,
                    request_type=request_type
                )
                session.add(new_otp_record)
                session.commit()
                session.refresh(new_otp_record)
            return otp
        except Exception as e:
            # Roll back the transaction in case of an error
            session.rollback()
            logger.error(f"Error storing OTP: {e}")
            logger.error(traceback.format_exc())
            return APIResponse(
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message = "Something went wrong",
            data = None)
            
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(days= settings.access_token_expire_days)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(payload = to_encode, key = settings.secret_key, algorithm = settings.algorithm)
    
    return encoded_jwt


def decode_token(token: str):
    try:
        # The decode function returns the payload as a dictionary
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        return payload
    except jwt.PyJWTError as e:
        logger.error(f"Token validation failed: {e}")
        logger.debug(traceback.format_exc())
        return None