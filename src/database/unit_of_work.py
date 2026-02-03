from src.database.db import Database
from sqlalchemy.ext.asyncio import AsyncSession

class UnitOfWork():

    def __init__(self, database: Database):
        self.database = database
        self.session: AsyncSession | None = None
    

    async def __aenter__(self) -> AsyncSession:
        self.session = self.database.create_session()
        return self.session


    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            if exc_type:
                await self.session.rollback()
            else:
                await self.session.commit()
            await self.session.close()