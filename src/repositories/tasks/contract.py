from abc import ABC, abstractmethod


class ITasksRepo(ABC):
    @abstractmethod
    async def get_tasks(self, user_id: int, offset: int = 0, limit: int = 100) -> list[dict]: ...

    @abstractmethod
    async def get_task_by_id(self) -> dict: ...

    @abstractmethod
    async def create_task(self) -> int: ...

    @abstractmethod
    async def update_task(self) -> bool: ...
