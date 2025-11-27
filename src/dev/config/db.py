import os
from typing import AsyncGenerator

from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

load_dotenv()

# Crear engine asíncrono
engine = create_async_engine(
    os.getenv("DB_URL"),
    echo=True,  # Cambiar a False en producción
    future=True,
    pool_pre_ping=True,
)

# Crear session maker
async_session_maker = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False,
)


# Dependency para FastAPI
async def get_session():
    async with async_session_maker() as session:
        try:
            type(session)
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
