from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import AsyncAdaptedQueuePool

from src.config import Config


def get_database_url(postgres_conn):
    if postgres_conn.startswith("postgresql://"):
        return postgres_conn.replace("postgresql://", "postgresql+asyncpg://")
    elif postgres_conn.startswith("postgres://"):
        return postgres_conn.replace("postgres://", "postgresql+asyncpg://")
    return postgres_conn


class Database:
    def __init__(self, config: Config):
        self.engine = create_async_engine(
            get_database_url(config.postgres_conn),
            echo=config.db.logging,
            poolclass=AsyncAdaptedQueuePool,
            pool_size=config.db.pool_size,
            max_overflow=config.db.max_overflow,
            pool_pre_ping=True,
            pool_recycle=config.db.pool_recycle,
            pool_timeout=config.db.pool_timeout,
        )

        self.session_factory = async_sessionmaker(
            self.engine,
            class_=AsyncSession,
            expire_on_commit=False,
            autoflush=False,
        )

    async def get_session(self):
        async with self.session_factory() as session:
            try:
                yield session
                session.commit()
            except:
                await session.rollback()
                raise
            finally:
                await session.close()
    
    def create_session(self) -> AsyncSession:
        return self.session_factory()

    async def close(self):
        await self.engine.dispose()
