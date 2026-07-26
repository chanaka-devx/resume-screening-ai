from sqlalchemy.ext.asyncio import (
    async_sessionmaker,
    AsyncSession,
)

from app.db.database import engine

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)