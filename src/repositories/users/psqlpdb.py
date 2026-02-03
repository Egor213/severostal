from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import AsyncSession

from src.database import Database
from src.database.models import User as UserModel
from src.entity.users import User
from src.repositories.users.contract import IUsersRepo


class UsersRepoPdb(IUsersRepo):

    def __init__(self, database: Database):
        self.database = database

    @asynccontextmanager
    async def get_session(self, ready_session: AsyncSession | None = None):
        if ready_session:
            yield ready_session
        else:
            async with self.database.get_session() as session:
                yield session

    async def add_user(
        self, username: str, hashed_password: str, ready_session: AsyncSession | None = None
    ) -> int:
        async with self.get_session(ready_session) as session:
            user = UserModel(username=username, hashed_password=hashed_password)
            session.add(user)
            await session.commit()
            return user.id, user.username

    async def get_user_by_id(self, id: int, ready_session: AsyncSession | None = None) -> User:
        pass
