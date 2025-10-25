from pydantic import BaseModel
from typing import Optional, Dict, Any


class SignUpRequest(BaseModel):
    username: str
    email: str
    password: str

class VerifyOTPRequest(BaseModel):
    unique_token: str
    otp: str

class LoginRequest(BaseModel):
    email: str
    password: str
    
class Token(BaseModel):
    token: str
    token_type: str
    
class ForgotPasswordRequest(BaseModel):
    email: str

class ResendOTPRequest(BaseModel):
    unique_token: str

class ResetPasswordRequest(BaseModel):
    unique_token: str
    new_password: str