from src.database import Database
from sqlalchemy.ext.asyncio import AsyncSession
from .contract import IUsersRepo


class UsersRepoPdb(IUsersRepo):

    def __init__(self, database: Database):
        self.database = database

    async def register_user(self, username: str, hashed_password: str, ready_session: AsyncSession | None = None) -> tuple[int, str]:
        session = ready_session or self.database.get_session()
