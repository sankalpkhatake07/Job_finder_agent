from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    app_name: str = "CareerMatch Agent"
    app_env: str = "development"
    secret_key: str = "change-me"
    admin_token: str = "change-me"
    database_url: str = "sqlite:///./career_agent.db"
    telegram_bot_token: str | None = None
    telegram_chat_id: str | None = None
    smtp_host: str | None = None
    smtp_port: int = 587
    smtp_username: str | None = None
    smtp_password: str | None = None
    alert_email_to: str | None = None
    scan_timezone: str = "Asia/Kolkata"
    match_high: float = 75
    match_medium: float = 55
    max_job_age_days: int = 14
    request_timeout: int = 20
    user_agent: str = "CareerMatchAgent/1.0"
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()
