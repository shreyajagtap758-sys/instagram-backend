from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    DATABASE_URL: str
    ENCRYPTION_KEY: str
    TOTP_ISSUER: str
    ALGORITHM: str = "RS256"
    PRIVATE_KEY_PATH: str
    PUBLIC_KEY_PATH: str

    model_config = SettingsConfigDict(env_file=".env")

settings = Settings()
