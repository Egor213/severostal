from src.repositories.tasks import ITasksRepo
from src.database import UnitOfWork


class TasksService:

    def __init__(self, task_repo: ITasksRepo, uow: UnitOfWork):
        self.tasks_repo = task_repo
        self.uow = uow

    async def get_all_tasks(self):
        await self.tasks_repo.get_tasks(1)
