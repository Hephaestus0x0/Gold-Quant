from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")
    
    DATABASE_URL: str = "postgresql://localhost/goldquant"
    
    TWELVE_DATA_API_KEY: str = ""
    TELEGRAM_BOT_TOKEN: str = ""
    TELEGRAM_CHAT_ID: str = ""
    
    ENABLE_SCHEDULER: bool = True
    
    SYMBOL: str = "XAUUSD"
    TIMEFRAMES: list[str] = ["M15", "H1", "H4", "D1"]
    
    LOG_LEVEL: str = "INFO"


settings = Settings()
