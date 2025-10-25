from passlib.context import CryptContext
import secrets
import string
from fastapi import HTTPException, status
from datetime import datetime, timedelta, timezone
import jwt
from sqlalchemy.orm import Session
from app.models.user import User
from app.schemas.auth import SignUpRequest, VerifyOTPRequest, LoginRequest, Token, ForgotPasswordRequest, ResetPasswordRequest
from app.schemas.common import APIResponse
from app.utils.auth_utils import (is_password_strong_enough, hash_password, 
                                  verify_password, create_and_store_otp, create_access_token, decode_token)
from app.services.email_services import SendEmail
from app.models.auth import OTPVerification

from app.core.config import settings
from uuid import uuid4

from app.core.app_logger import setup_daily_logger
logger = setup_daily_logger(logger_name=__name__)


async def creat_user_account(data: SignUpRequest, session: Session):
    
    user_exists = session.query(User).filter(User.email == data.email).first()
    
    if user_exists:
        logger.info(f"Attempt to create an account with existing email: {data.email}")
        return APIResponse(status= status.HTTP_400_BAD_REQUEST, 
                           message="Email already exists", data=None)

    if not is_password_strong_enough(data.password):
        logger.info(f"Weak password attempt during signup for email: {data.email}")
        return APIResponse(status= status.HTTP_400_BAD_REQUEST, 
                           message="Weak Password", 
                           data = None)
        
    
    user = User()
    user.id = str(uuid4())
    user.username = data.username
    user.email = data.email
    user.hashed_password = hash_password(data.password)
    user.is_active = False
    user.created_at = datetime.now(timezone.utc)
    session.add(user)
    session.commit()
    session.refresh(user)
    
    otp = await create_and_store_otp(session, user.email, request_type='signup')
    # convert user into dict
    allowed = ["name", "email", "device_type"]
    user_dict = user.to_dict(allowed_fields= allowed)
    
    # Create a unqique token to verify the purpose of the service i.e. signup
    to_encode = {"sub": user.email, "request_type": 'signup'}
    token = create_access_token(data = to_encode, expires_delta= timedelta(minutes=15))
    
    _ = SendEmail(user.email).send_signup_email(data.username, otp)


    user_dict.update({"unique_token": token})
    logger.info(f"User account created successfully")
    return APIResponse(status= status.HTTP_201_CREATED, 
                       message="User created successfully. Please verify your email to activate your account.",
                      data= user_dict)


async def verify_otp(data: VerifyOTPRequest, session: Session):
    decoded_token = decode_token(data.unique_token)
    # check the decoded token validity along with the presence of request type
    if not decoded_token or 'sub' not in decoded_token or 'request_type' not in decoded_token:
        logger.info(f"Invalid or expired token received for OTP verification: {data.unique_token}")
        return APIResponse(status=status.HTTP_401_UNAUTHORIZED, 
                           message="Invalid or expired token", data=None)
    
    email = decoded_token['sub']
    request_type = decoded_token['request_type']
    user = session.query(User).filter(User.email == email).first()
    if not user:
        logger.info(f"OTP verification attempt for non-existent user: {email}")
        return APIResponse(status=status.HTTP_404_BAD_REQUEST,
                           message="User not found", data=None)
        

    if user.is_active:
        logger.info(f"OTP verification attempt for already verified user: {email}")
        return APIResponse(status=status.HTTP_400_BAD_REQUEST,
                           message="User already verified", data=None)


    otp_record = session.query(OTPVerification).filter(OTPVerification.email == email, OTPVerification.otp_code == data.otp).first()

    if not otp_record:
        logger.info(f"Invalid OTP attempt for user: {email}")
        return APIResponse(status=status.HTTP_400_BAD_REQUEST,
                           message="Invalid OTP", data=None)
        
    
    if otp_record.request_type != request_type:
        logger.info(f"OTP purpose mismatch for user: {email}. Expected {otp_record.request_type}, got {request_type}.")
        return APIResponse(status=status.HTTP_400_BAD_REQUEST,
                           message="OTP purpose mismatch", data=None)
        
    
    expires_at = datetime.fromisoformat(otp_record.expires_at) if isinstance(otp_record.expires_at, str) else otp_record.expires_at
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)
    if expires_at < datetime.now(timezone.utc):
        logger.info(f"Expired OTP attempt for user: {email}")
        return APIResponse(status=status.HTTP_400_BAD_REQUEST,
                           message="OTP has expired", data=None)
        
    
    user.is_active = True
    user.updated_at = datetime.now(timezone.utc)
    session.add(user)
    session.delete(otp_record)
    session.commit()
       
    return APIResponse(status=status.HTTP_200_OK,
                          message="OTP verified successfully",
                          data=None)
    

async def user_login(data: LoginRequest, session: Session):
    user = session.query(User).filter(User.email == data.email).first()
    
    
    # IS ONBOARDED TRUE OR FALSE 
    if not user:
        logger.info(f"Login attempt with unregistered email: {data.email}")
        return APIResponse(status=status.HTTP_404_NOT_FOUND,
                           message="User not registered, please sign-up", data=None)
        
    
    if not user.is_active:
        # OTP EMAIL
        otp = await create_and_store_otp(session, user.email, request_type='resetpassword')
        # UNIQUE TOKEN
        token = create_access_token(data = {"sub": user.email, "request_type": "resetpassword"}, 
                                expires_delta=timedelta(minutes=15))
        _ = SendEmail(user.email).send_signup_email(user.name, otp)
        logger.info(f"Login attempt for unverified user: {data.email}. OTP resent.")
        
        return APIResponse(status= status.HTTP_200_OK,
                           message = "OTP sent to registered email for verification" , 
                           data={"unique_token": token, "is_active": user.is_active})
        
    
    if not verify_password(data.password, user.hashed_password):
        logger.info(f"Incorrect password attempt for user: {data.email}")
        return APIResponse(status= status.HTTP_400_BAD_REQUEST,
                           message = "username or password incorrect", data=None)
    
    allowed = ["name", "email", "device_type", "is_onboarded", "is_verified", "profile_picture"]
    user_dict = user.to_dict(allowed_fields= allowed)

    access_token = create_access_token(data={"sub": user.email})
    user_dict["token_details"] = Token(token=access_token, token_type= 'bearer').model_dump()
    
    return APIResponse(status=status.HTTP_202_ACCEPTED,
                       message = "Login successful",
                    data= user_dict)
   

async def forgot_password(data: ForgotPasswordRequest, session: Session):
    
    user = session.query(User).filter(User.email == data.email).first()
    
    
    if not user:
        logger.info(f"Forgot password attempt for unregistered email: {data.email}")
        return APIResponse(status=status.HTTP_404_NOT_FOUND,
                           message="User not found", data=None)
        
    
    user.is_active = False
    user.updated_at = datetime.now(timezone.utc)
    session.add(user)
    session.commit()
    session.refresh(user)
    otp = await create_and_store_otp(session, user.email, request_type='resetpassword')
    token = create_access_token(data = {"sub": user.email, "request_type": "resetpassword"}, 
                                expires_delta=timedelta(minutes=15))
    
    _ = SendEmail(user.email).send_password_reset_email(user.username, otp)
    
    return APIResponse(status=status.HTTP_202_ACCEPTED, message='Verification OTP sent to registered email',
                       data= {"unique_token": token})


async def reset_password(data : ResetPasswordRequest, session: Session):
    decoded_token = decode_token(data.unique_token)
    email = decoded_token.get("sub", "")
    request_type = decoded_token.get("request_type", "")
    if request_type != "resetpassword":
        return APIResponse(status= status.HTTP_400_BAD_REQUEST,
                           message= "Invalid Request Received",
                           data = None)
    
    user = session.query(User).filter(User.email == email).first()
    
    if not user:
        logger.info(f"Password reset attempt for non-existent user: {email}")
        return APIResponse(
            status= status.HTTP_404_NOT_FOUND,
            message = "User not Found", data = None)
        
    
    if not is_password_strong_enough(data.new_password):
        return APIResponse(status= status.HTTP_406_NOT_ACCEPTABLE,
                           message= "Please provide a strong password.",
                           data = None)
        
    
    user.hashed_password = hash_password(data.new_password)
    user.is_active = True
    user.updated_at = datetime.now(timezone.utc)
    session.add(user)
    session.commit()
    session.refresh(user)
    
    allowed = ["name", "email", "device_type"]
    user_dict = user.to_dict(allowed_fields= allowed)
    
    return APIResponse(status = status.HTTP_200_OK,
                       message="Password Reset Successful", data= user_dict)



# Delete account function
async def delete_account(user: User, session: Session):
    session.delete(user)
    session.commit()
    return APIResponse(status=status.HTTP_204_NO_CONTENT, message="Account deleted successfully", data=None)


# Dependency to check the user's authenticity at every feature call

from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends
from app.core.database import get_session

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

async def get_current_user(token: str = Depends(oauth2_scheme), session: Session = Depends(get_session)):
    """
    Dependency to validate the JWT and get the current user's email.
    """
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        user_email: str = payload.get("sub")
        if user_email is None:
            return  APIResponse(
                status=status.HTTP_401_UNAUTHORIZED,
                message = "Invalid request",
                data = None
            )
        
        user = session.query(User).filter(User.email == user_email, User.is_active==True).first()
        if user is None:
            return  APIResponse(
                status=status.HTTP_401_UNAUTHORIZED,
                message = "Un-identified user",
                data = None
            )
    except jwt.PyJWTError:
        return  APIResponse(
                status=status.HTTP_401_UNAUTHORIZED,
                message = "Invalid or Expired token",
                data = None
            )
    return user