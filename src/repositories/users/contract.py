from abc import ABC, abstractmethod

from sqlalchemy.ext.asyncio import AsyncSession

from src.entity.users import User


class IUsersRepo(ABC):
    @abstractmethod
    async def add_user(
        self, username: str, hashed_password: str, ready_session: AsyncSession | None = None
    ) -> int: ...

    @abstractmethod
    async def get_user_by_id(self, id: int, ready_session: AsyncSession | None = None) -> User: ...
