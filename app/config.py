from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    # Модель конфигурации для pydantic
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8', extra='ignore')

    # Переменные окружения
    DATABASE_URL: str = "sqlite+aiosqlite:///./data/ads_management.db"
    TELEGRAM_BOT_TOKEN: Optional[str] = None
    
    # Настройки Facebook
    FACEBOOK_APP_ID: Optional[str] = None
    FACEBOOK_APP_SECRET: Optional[str] = None
    
    # Настройки OpenAI
    OPENAI_API_KEY: Optional[str] = None
    
    # Настройки приложения
    RENDER: bool = False
    MOCK_MODE: bool = True
    RENDER_EXTERNAL_URL: str = "http://localhost:8000"

    @property
    def FB_REDIRECT_URI(self) -> str:
        return f"{self.RENDER_EXTERNAL_URL}/auth/facebook/callback"

    @property
    def FB_SCOPE(self) -> str:
        return "ads_management,ads_read"

# Создаем единственный экземпляр настроек
settings = Settings()
