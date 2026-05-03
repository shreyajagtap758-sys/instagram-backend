from sqlalchemy.ext.asyncio.engine import create_async_engine
from sqlalchemy.ext.asyncio import async_sessionmaker

from server.src.core.config import settings

from server.src.models import Base

engine = create_async_engine(
    settings.DATABASE_URL,
    echo=False
)

session_local = async_sessionmaker(
    engine,
    expire_on_commit=False
)

async def get_session():
    async with session_local() as session:
        yield session

