import os
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):

    # DB / Security
    DATABASE_URL: str
    ENCRYPTION_KEY: str
    TOTP_ISSUER: str
    ALGORITHM: str = "RS256"

    PRIVATE_KEY_PATH: str
    PUBLIC_KEY_PATH: str

    #frontend
    FRONTEND_URL: str

    # EMAIL (CONFIG VALUES ONLY)
    MAIL_USERNAME: str
    MAIL_PASSWORD: str
    MAIL_FROM: str

    MAIL_PORT: int = 587
    MAIL_SERVER: str = "smtp.gmail.com"

    MAIL_STARTTLS: bool = True
    MAIL_SSL_TLS: bool = False
    USE_CREDENTIALS: bool = True


    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()
