import logging

from sqlalchemy.ext.asyncio import AsyncSession

from src.app.logger import NullLogger
from src.database import UnitOfWork
from src.entity.tasks import Task
from src.repositories.tasks import ITasksRepo
from src.repositories.users import IUsersRepo
from src.services.exceptions import ValidationException
from src.services.tasks.exceptions import (
    CannotCreateTaskEx,
    CannotDeleteUserTaskByIdEx,
    CannotGetUserTaskByIdEx,
    CannotGetUserTasksEx,
    CannotMarkUserTaskByIdEx,
    TaskNotFoundEx,
)
from src.services.tasks.validators import validate_task_create
from src.services.users.exceptions import UserNotFoundEx


class TasksService:

    def __init__(
        self,
        task_repo: ITasksRepo,
        user_repo: IUsersRepo,
        uow: UnitOfWork,
        logger: logging.Logger | None = None,
    ):
        self.tasks_repo = task_repo
        self.user_repo = user_repo
        self.uow = uow
        self.logger = logger or NullLogger()

    async def create_task(self, user_id: int, title: str, descr: str) -> int:
        user = await self.user_repo.get_user_by_id(user_id)
        if not user:
            self.logger.error(f"user with id: {user_id} not found")
            raise UserNotFoundEx()
        try:
            validate_task_create(title, descr)
            id = await self.tasks_repo.create_task(user_id, title, descr)
            self.logger.debug(f"task created: id={id}")
            return id
        except ValidationException as e:
            self.logger.error(f"validation error: {e}")
            raise e
        except Exception as e:
            self.logger.error(f"unknown error: {e}")
            raise CannotCreateTaskEx()

    async def get_user_task_by_id(self, user_id: int, task_id: int) -> Task:
        try:
            task = await self.tasks_repo.get_user_task_by_id(user_id, task_id)
            self.logger.debug(f"get task: id={task_id}, user={user_id}")
        except Exception as e:
            self.logger.error(f"unknown error: {e}")
            raise CannotGetUserTaskByIdEx()
        if task is None:
            raise TaskNotFoundEx()
        return task

    async def get_user_tasks(
        self, user_id: int, offset: int | None = None, limit: int | None = None
    ) -> Task:
        try:
            tasks = await self.tasks_repo.get_user_tasks(user_id, offset, limit)
            self.logger.debug(f"get tasks: user={user_id}, count_tasks={len(tasks)}")
        except Exception as e:
            self.logger.error(f"unknown error: {e}")
            raise CannotGetUserTasksEx()
        return tasks

    async def delete_user_task_by_id(self, user_id: int, task_id: int) -> bool:
        try:
            status = await self.tasks_repo.delete_user_task_by_id(user_id, task_id)
            self.logger.debug(f"delete task: id={task_id}, user={user_id}, is_deleted={status}")
            return status
        except Exception as e:
            self.logger.error(f"unknown error: {e}")
            raise CannotDeleteUserTaskByIdEx()

    async def mark_user_task_by_id(self, user_id: int, task_id: int, status: bool) -> bool:
        try:
            status = await self.tasks_repo.mark_user_task(user_id, task_id, status)
            self.logger.debug(
                f"completed status changed task: id={task_id}, user={user_id}, is_completed={status}"
            )
            return status
        except Exception as e:
            self.logger.error(f"unknown error: {e}")
            raise CannotMarkUserTaskByIdEx()
