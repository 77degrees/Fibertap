from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Application
    app_name: str = "Fibertap"
    debug: bool = False

    # Database
    database_url: str = "postgresql+asyncpg://fibertap:fibertap@localhost:5432/fibertap"

    # Redis
    redis_url: str = "redis://localhost:6379/0"

    # Security
    secret_key: str = "change-me-in-production"
    access_token_expire_minutes: int = 60 * 24 * 7  # 1 week

    # CORS
    cors_origins: list[str] = ["http://localhost:3000"]

    # External APIs
    incogni_api_key: str | None = None
    hibp_api_key: str | None = None

    # Email notifications
    smtp_host: str | None = None
    smtp_port: int = 587
    smtp_user: str | None = None
    smtp_password: str | None = None
    smtp_from_email: str | None = None
    notification_email: str | None = None  # Where to send alerts

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
