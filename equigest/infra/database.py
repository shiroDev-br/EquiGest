from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import registry

from equigest.settings import Settings

settings = Settings()
DATABASE_URL = settings.POSTGRES_URL

engine = create_async_engine(
    DATABASE_URL
)
mapper_registry = registry()