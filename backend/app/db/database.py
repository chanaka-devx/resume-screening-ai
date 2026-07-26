import ssl

from sqlalchemy.ext.asyncio import create_async_engine

from app.core.config import settings

ssl_context = ssl.create_default_context()

engine = create_async_engine(
    settings.DATABASE_URL,
    echo=True,
)