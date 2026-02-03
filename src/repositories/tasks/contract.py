from abc import ABC, abstractmethod

from sqlalchemy.ext.asyncio import AsyncSession

from src.entity.tasks import Task


class ITasksRepo(ABC):
    @abstractmethod
    async def get_user_tasks(
        self,
        user_id: int,
        offset: int = 0,
        limit: int = 100,
        ready_session: AsyncSession | None = None,
    ) -> list[Task]: ...

    @abstractmethod
    async def get_user_task_by_id(
        self, user_id: int, task_id: int, ready_session: AsyncSession | None = None
    ) -> Task: ...

    @abstractmethod
    async def get_user_tasks_by_title(
        self,
        user_id: int,
        title: str,
        offset: int = 0,
        limit: int = 100,
        ready_session: AsyncSession | None = None,
    ) -> list[Task]: ...

    @abstractmethod
    async def create_task(
        self, user_id: int, title: str, descr: str, ready_session: AsyncSession | None = None
    ) -> int: ...

    @abstractmethod
    async def update_task_by_id(
        self, task_id: int, update_data: dict, ready_session: AsyncSession | None = None
    ) -> bool: ...

    @abstractmethod
    async def delete_user_task_by_id(
        self, user_id: int, task_id: int, ready_session: AsyncSession | None = None
    ) -> bool: ...

    @abstractmethod
    async def mark_user_task(
        self, user_id: int, task_id: int, status: bool, ready_session: AsyncSession | None = None
    ) -> bool: ...
