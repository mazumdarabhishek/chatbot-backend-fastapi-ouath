from app.utils.email_templates import *
import jwt
import os
import smtplib
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from hashlib import sha256

from app.core.config import settings


from app.core.app_logger import setup_daily_logger
import traceback
logger = setup_daily_logger(logger_name=__name__)


class SendEmail:
    
    def __init__(self, _to):
        self._to = _to
    
    def send_signup_email(self, name: str, otp: str):
        subject, body = generate_signup_email(name, otp)
        return self._send_email(subject, body)
    
    def send_password_reset_email(self, name: str, otp: str):
        subject, body = generate_password_reset_email(name, otp)
        return self._send_email(subject, body)
    
    def resend_otp_email(self, name: str, otp: str):
        subject, body = generate_resend_otp_email(name, otp)
        return self._send_email(subject, body)
    
    def send_custom_email(self, subject: str, body: str):
        return self._send_email(subject, body)
    
    
    
    def _send_email(self, subject: str, body: str):
        try:
            # Gmail SMTP configuration
            smtp_host = "smtp.gmail.com"
            smtp_port = 587  # Use 587 for TLS, or 465 for SSL
            
            # Use app password from settings
            app_password = str(settings.app_password)
            
            message = MIMEMultipart()
            message['From'] = settings.email_from
            message['To'] = self._to
            message['Subject'] = subject
            message.attach(MIMEText(body, 'html'))
            
            # Create SMTP session
            with smtplib.SMTP(smtp_host, smtp_port) as server:
                logger.info("Starting TLS encryption...")
                server.starttls()  # Enable TLS encryption
                
                logger.info("Logging into Gmail server...")
                server.login(settings.email_from, app_password)

                logger.info("Sending the email...")
                server.sendmail(
                    settings.email_from, self._to, message.as_string()
                )
                logger.info("✅ Email sent successfully via Gmail!")
                return True
                
        except smtplib.SMTPAuthenticationError:
            logger.error("❌ Gmail authentication failed. Check your email and app password.")
        except smtplib.SMTPRecipientsRefused:
            logger.error(f"❌ Recipient {self._to} was refused by Gmail server.")
        except smtplib.SMTPSenderRefused:
            logger.error(f"❌ Sender {settings.email_from} was refused by Gmail server.")
        except Exception as e:
            logger.error(f"❌ An error occurred while sending email: {e}")
            logger.debug(traceback.format_exc())
        
        return False