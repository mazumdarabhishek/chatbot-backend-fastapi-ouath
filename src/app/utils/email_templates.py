# --- Static Configuration ---
from app.core.config import settings
COMPANY_NAME = settings.company_name

# -------------------------------------------------------------------
# 1. SIGN UP / ACCOUNT VERIFICATION TEMPLATE
# -------------------------------------------------------------------

# Placeholders: {user_name}, {otp_code}, {company_name}
SIGNUP_HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
<style>
  body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
  .container {{ width: 90%; max-width: 600px; margin: 20px auto; padding: 20px; border: 1px solid #ddd; border-radius: 8px; }}
  .header {{ text-align: center; margin-bottom: 20px; }}
  .otp-code {{ font-size: 32px; font-weight: bold; text-align: center; letter-spacing: 5px; margin: 30px 0; padding: 15px; background-color: #f2f2f2; border-radius: 5px; }}
  .footer {{ font-size: 12px; color: #777; text-align: center; margin-top: 20px; }}
  .warning {{ font-size: 14px; color: #555; text-align: center; }}
</style>
</head>
<body>
  <div class="container">
    <div class="header">
      <h2>Welcome Aboard!</h2>
    </div>
    <p>Hello {user_name},</p>
    <p>Thank you for signing up with {company_name}. Please use the One-Time Password (OTP) below to verify your email address and complete your registration.</p>
    
    <div class="otp-code">{otp_code}</div>
    
    <p class="warning">This code will expire in <strong>10 minutes</strong>. For your security, do not share this code with anyone.</p>
    <p>If you did not initiate this request, you can safely ignore this email.</p>
    <div class="footer">
      <p>&copy; {company_name}. All rights reserved.</p>
    </div>
  </div>
</body>
</html>
"""

def generate_signup_email(user_name, otp_code):
    """
    Generates the subject and HTML body for a signup verification email.
    
    Returns:
        A tuple containing (subject, html_body)
    """
    subject = f"{otp_code} is your verification code for {COMPANY_NAME}"
    
    html_body = SIGNUP_HTML_TEMPLATE.format(
        user_name=user_name,
        otp_code=otp_code,
        company_name=COMPANY_NAME
    )
    
    return subject, html_body

# -------------------------------------------------------------------
# 2. FORGOT PASSWORD / PASSWORD RESET TEMPLATE
# -------------------------------------------------------------------

# Placeholders: {user_name}, {otp_code}, {company_name}
PASSWORD_RESET_HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
<style>
  body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
  .container {{ width: 90%; max-width: 600px; margin: 20px auto; padding: 20px; border: 1px solid #ddd; border-radius: 8px; }}
  .header {{ text-align: center; margin-bottom: 20px; }}
  .otp-code {{ font-size: 32px; font-weight: bold; text-align: center; letter-spacing: 5px; margin: 30px 0; padding: 15px; background-color: #f2f2f2; border-radius: 5px; }}
  .footer {{ font-size: 12px; color: #777; text-align: center; margin-top: 20px; }}
  .warning {{ font-size: 14px; color: #555; text-align: center; }}
</style>
</head>
<body>
  <div class="container">
    <div class="header">
      <h2>Password Reset Request</h2>
    </div>
    <p>Hello {user_name},</p>
    <p>We received a request to reset the password for your {company_name} account. Enter the One-Time Password (OTP) below to continue.</p>
    
    <div class="otp-code">{otp_code}</div>
    
    <p class="warning">This code will expire in <strong>10 minutes</strong>. For your security, do not share this code with anyone.</p>
    <p><strong>If you did not request a password reset,</strong> please ignore this email. No changes have been made to your account.</p>
    <div class="footer">
      <p>&copy; {company_name}. All rights reserved.</p>
    </div>
  </div>
</body>
</html>
"""

def generate_password_reset_email(user_name, otp_code):
    """
    Generates the subject and HTML body for a password reset email.
    
    Returns:
        A tuple containing (subject, html_body)
    """
    subject = f"{otp_code} is your password reset code for {COMPANY_NAME}"
    
    html_body = PASSWORD_RESET_HTML_TEMPLATE.format(
        user_name=user_name,
        otp_code=otp_code,
        company_name=COMPANY_NAME
    )
    
    return subject, html_body


RESEND_PASSWORD_HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
<style>
  body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
  .container {{ width: 90%; max-width: 600px; margin: 20px auto; padding: 20px; border: 1px solid #ddd; border-radius: 8px; }}
  .header {{ text-align: center; margin-bottom: 20px; }}
  .otp-code {{ font-size: 32px; font-weight: bold; text-align: center; letter-spacing: 5px; margin: 30px 0; padding: 15px; background-color: #f2f2f2; border-radius: 5px; }}
  .footer {{ font-size: 12px; color: #777; text-align: center; margin-top: 20px; }}
  .warning {{ font-size: 14px; color: #555; text-align: center; }}
</style>
</head>
<body>
  <div class="container">
    <div class="header">
      <h2>Your New Password Reset Code</h2>
    </div>
    <p>Hello {user_name},</p>
    <p>As requested, here is a new One-Time Password (OTP) to reset the password for your {company_name} account.</p>
    <div class="otp-code">{otp_code}</div>
    <p class="warning">This new code will expire in <strong>10 minutes</strong>. Please use it promptly.</p>
    <p><strong>If you did not request this,</strong> please ignore this email. Your account remains secure.</p>
    <div class="footer">
      <p>&copy; {company_name}. All rights reserved.</p>
    </div>
  </div>
</body>
</html>
"""

def generate_resend_password_email(user_name, otp_code):
    """
    Generates the subject and HTML body for a resend password reset email.
    
    Returns:
        A tuple containing (subject, html_body)
    """
    subject = f"{otp_code} is your new password reset code for {COMPANY_NAME}"
    html_body = RESEND_PASSWORD_HTML_TEMPLATE.format(
        user_name=user_name,
        otp_code=otp_code,
        company_name=COMPANY_NAME
    )
    return subject, html_body

# -------------------------------------------------------------------
# 3. ACCOUNT DELETION CONFIRMATION TEMPLATE
# -------------------------------------------------------------------

def generate_account_delete_completion_email(user_name):
    """
    Generates the subject and HTML body for an account deletion confirmation email.
    
    Returns:
        A tuple containing (subject, html_body)
    """
    subject = "Your account has been successfully deleted"
    
    html_body = f"""
    <!DOCTYPE html>
    <html>
    <head>
    <style>
      body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
      .container {{ width: 90%; max-width: 600px; margin: 20px auto; padding: 20px; border: 1px solid #ddd; border-radius: 8px; }}
      .header {{ text-align: center; margin-bottom: 20px; }}
      .footer {{ font-size: 12px; color: #777; text-align: center; margin-top: 20px; }}
    </style>
    </head>
    <body>
      <div class="container">
        <div class="header">
          <h2>Account Deletion Confirmation</h2>
        </div>
        <p>Hello {user_name},</p>
        <p>This email is to confirm that your account with {COMPANY_NAME} has been successfully deleted along with all associated data.</p>
        <p>We're sorry to see you go. If you have any feedback or if there's anything we could have done better, please let us know.</p>
        <p>Thank you for having been a part of {COMPANY_NAME}.</p>
        <div class="footer">
          <p>&copy; {COMPANY_NAME}. All rights reserved.</p>
        </div>
      </div>
    </body>
    </html>
    """
    
    return subject, html_body


# -------------------------------------------------------------------
# 4. resend OTP EMAIL TEMPLATE
# -------------------------------------------------------------------
RESEND_OTP_HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
<style>
  body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
  .container {{ width: 90%; max-width: 600px; margin: 20px auto; padding: 20px; border: 1px solid #ddd; border-radius: 8px; }}
  .header {{ text-align: center ; margin-bottom: 20px; }}
  .otp-code {{ font-size: 32px; font-weight: bold; text-align: center; letter-spacing: 5px; margin: 30px 0; padding: 15px; background-color: #f2f2f2; border-radius: 5px; }}
  .footer {{ font-size: 12px; color: #777; text-align: center; margin-top: 20px; }}
  .warning {{ font-size: 14px; color: #555; text-align: center; }}
</style>
</head>
<body>
  <div class="container">
    <div class="header">
      <h2>Your New Verification Code</h2>
    </div>
    <p>Hello {user_name},</p>
    <p>As requested, here is a new One-Time Password (OTP) to verify your email address for your {company_name} account.</p>
    <div class="otp-code">{otp_code}</div>
    <p class="warning">This new code will expire in <strong>10 minutes</strong>. Please use it promptly.</p>
    <p><strong>If you did not request this,</strong> please ignore this email. Your account remains secure.</p>
    <div class="footer">
      <p>&copy; {company_name}. All rights reserved.</p>
    </div>
  </div>
</body>
</html>
"""
def generate_resend_otp_email(user_name, otp_code):
    """
    Generates the subject and HTML body for a resend OTP email.
    
    Returns:
        A tuple containing (subject, html_body)
    """
    subject = f"{otp_code} is your new verification code for {COMPANY_NAME}"
    html_body = RESEND_OTP_HTML_TEMPLATE.format(
        user_name=user_name,
        otp_code=otp_code,
        company_name=COMPANY_NAME
    )
    return subject, html_body