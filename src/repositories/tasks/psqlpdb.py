from src.database import Database
from src.repositories.tasks.contract import ITasksRepo


class TasksRepoPdb(ITasksRepo):

    def __init__(self, database: Database):
        self.database = database

    async def get_tasks(self, user_id: int, offset: int = 0, limit: int = 100) -> list[dict]:
        print("get all tasks")

    async def get_task_by_id(self) -> dict: ...

    async def create_task(self) -> int: ...

    async def update_task(self) -> bool: ...
