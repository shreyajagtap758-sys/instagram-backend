import secrets
import hashlib

from fastapi_mail import FastMail, MessageSchema, MessageType, NameEmail
from server.src.core.email_config import mail_config
from server.src.core.config import settings


def generate_raw_token() -> str:
    return secrets.token_urlsafe(32)


def hash_token(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


fastmail = FastMail(mail_config)

async def send_reset_email(email: str, token: str):

    reset_link = f"{settings.FRONTEND_URL}/reset-password/{token}"

    message = MessageSchema(
        subject="Password Reset Request",
        recipients=[NameEmail(email=email, name="")],
        body=f"""
        <h3>Password Reset</h3>
        <p>Click below to reset your password:</p>
        <a href="{reset_link}">{reset_link}</a>
        <p>This link expires in 15 minutes. DO NOT SHARE THE LINK</p>
        """,
        subtype=MessageType.html
    )

    try:
        await fastmail.send_message(message)
    except Exception as e:
        print("EMAIL FAILED:", str(e))
