import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.db.models import Base
import os
from dotenv import load_dotenv

load_dotenv()

# Получаем URL базы данных из переменных окружения
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./ads_management.db")
# Преобразуем URL для асинхронного использования
ASYNC_DATABASE_URL = DATABASE_URL.replace(
    'sqlite:///', 'sqlite+aiosqlite:///', 1
)

async def init_db():
    # Создаем асинхронный движок
    engine = create_async_engine(
        ASYNC_DATABASE_URL,
        echo=True  # Включаем логирование SQL
    )

    # Создаем все таблицы
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    # Создаем фабрику сессий
    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )

    return async_session

if __name__ == "__main__":
    asyncio.run(init_db())
