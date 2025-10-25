from app.services.auth_services import *
from app.schemas.auth import ResendOTPRequest
from app.utils.auth_utils import decode_token
from app.utils.auth_utils import create_and_store_otp
from app.services.email_services import SendEmail
from fastapi import APIRouter, Depends

from app.core.app_logger import setup_daily_logger
logger = setup_daily_logger(logger_name=__name__)


auth_app = APIRouter(prefix="/auth")

@auth_app.post("/signup")
async def create_user_endpoint(user: SignUpRequest, session : Session = Depends(get_session)):
    return await creat_user_account(user, session)

@auth_app.post("/login")
async def login_user_endpoint(data: LoginRequest, session : Session = Depends(get_session)):
    
    return await user_login(data, session)

@auth_app.post("/verify_otp")
async def verify_otp_endpoint(data: VerifyOTPRequest, session: Session = Depends(get_session)):
    return await verify_otp(data, session)

@auth_app.post("/resend_otp")
async def resend_otp_endpoint(data: ResendOTPRequest, session: Session = Depends(get_session)):
    decoded_token = decode_token(data.unique_token)
    if not decoded_token or 'sub' not in decoded_token or 'request_type' not in decoded_token:
        logger.warning("Invalid unique token provided for resending OTP")
        return APIResponse(status=status.HTTP_401_UNAUTHORIZED, 
                           message="Invalid Request", data=None)
    
    email = decoded_token['sub']
    request_type = decoded_token['request_type']
    response = await create_and_store_otp(session = session, email= email, request_type=request_type)
    if isinstance(response, APIResponse):
        return response
    
    _ = SendEmail(_to=email).resend_otp_email(name=email.split("@")[0], otp=response)
    return APIResponse(status=status.HTTP_200_OK, message="OTP resent successfully", data=None)

@auth_app.post("/forgot_password")
async def forgot_password_endpoint(data: ForgotPasswordRequest, session: Session = Depends(get_session)):
    return await forgot_password(data, session)

@auth_app.post("/reset_password")
async def reset_password_endpoint(data: ResetPasswordRequest, session: Session = Depends(get_session)):
    return await reset_password(data, session)


@auth_app.delete("/delete_account")
async def delete_account_endpoint(current_user: str = Depends(get_current_user),
                                  session: Session = Depends(get_session)):
    if isinstance(current_user, APIResponse):
        return current_user
    
    user = session.query(User).filter(User.id == current_user.id).first()
    if not user:
        logger.warning(f"User not found for account deletion: ID {current_user.id}")
        return APIResponse(status=status.HTTP_404_NOT_FOUND, 
                           message="User not found", data=None)
    
    return await delete_account(user, session)