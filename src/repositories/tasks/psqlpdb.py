from contextlib import asynccontextmanager
from datetime import datetime, timezone

from sqlalchemy import delete, desc, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import Database
from src.database.models import Task as TaskModel
from src.entity.tasks import Task
from src.repositories.tasks.contract import ITasksRepo


class TasksRepoPdb(ITasksRepo):

    def __init__(self, database: Database):
        self.database = database

    @asynccontextmanager
    async def get_session(self, ready_session: AsyncSession | None = None):
        if ready_session:
            yield ready_session
        else:
            async with self.database.get_session() as session:
                yield session

    async def get_user_tasks(
        self,
        user_id: int,
        offset: int = 0,
        limit: int = 100,
        ready_session: AsyncSession | None = None,
    ) -> list[Task]:
        async with self.get_session(ready_session) as session:
            stmt = (
                select(TaskModel)
                .where(TaskModel.user_id == user_id)
                .order_by(desc(TaskModel.created_at))
                .offset(offset)
                .limit(limit)
            )
            result = await session.execute(stmt)
            tasks = result.scalars().all()

            return [
                Task(
                    id=task.id,
                    user_id=task.user_id,
                    title=task.title,
                    description=task.description,
                    is_completed=task.is_completed,
                    created_at=task.created_at,
                    updated_at=task.updated_at,
                )
                for task in tasks
            ]

    async def get_user_task_by_id(
        self, user_id: int, task_id: int, ready_session: AsyncSession | None = None
    ) -> Task:
        async with self.get_session(ready_session) as session:
            stmt = select(TaskModel).where(TaskModel.id == task_id, TaskModel.user_id == user_id)
            result = await session.execute(stmt)
            task = result.scalar_one_or_none()

            if task:
                return Task(
                    id=task.id,
                    user_id=task.user_id,
                    title=task.title,
                    description=task.description,
                    is_completed=task.is_completed,
                    created_at=task.created_at,
                    updated_at=task.updated_at,
                )
            return None

    async def get_user_tasks_by_title(
        self,
        user_id: int,
        title: str,
        offset: int = 0,
        limit: int = 100,
        ready_session: AsyncSession | None = None,
    ) -> list[Task]:
        async with self.get_session(ready_session) as session:
            stmt = (
                select(TaskModel)
                .where(TaskModel.user_id == user_id, TaskModel.title.ilike(f"%{title}%"))
                .order_by(desc(TaskModel.created_at))
                .offset(offset)
                .limit(limit)
            )
            result = await session.execute(stmt)
            tasks = result.scalars().all()

            return [
                Task(
                    id=task.id,
                    user_id=task.user_id,
                    title=task.title,
                    description=task.description,
                    is_completed=task.is_completed,
                    created_at=task.created_at,
                    updated_at=task.updated_at,
                )
                for task in tasks
            ]

    async def create_task(
        self, user_id: int, title: str, descr: str, ready_session: AsyncSession | None = None
    ) -> int:
        async with self.get_session(ready_session) as session:
            task = TaskModel(user_id=user_id, title=title, description=descr, is_completed=False)
            session.add(task)
            await session.commit()
            return task.id

    async def update_task_by_id(
        self, task_id: int, update_data: dict, ready_session: AsyncSession | None = None
    ) -> bool:
        async with self.get_session(ready_session) as session:
            if update_data:
                update_data["updated_at"] = datetime.now(timezone.utc)
                stmt = (
                    update(TaskModel)
                    .where(
                        TaskModel.id == task_id,
                    )
                    .values(**update_data)
                )
                await session.execute(stmt)
                await session.commit()

            return True

    async def delete_user_task_by_id(
        self, user_id: int, task_id: int, ready_session: AsyncSession | None = None
    ) -> bool:
        async with self.get_session(ready_session) as session:
            stmt = delete(TaskModel).where(
                TaskModel.id == task_id,
                TaskModel.user_id == user_id,
            )
            result = await session.execute(stmt)
            await session.commit()

            return result.rowcount > 0

    async def mark_user_task(
        self, user_id: int, task_id: int, status: bool, ready_session: AsyncSession | None = None
    ) -> bool:
        current_time = datetime.now(timezone.utc).replace(tzinfo=None)
        async with self.get_session(ready_session) as session:
            stmt = (
                update(TaskModel)
                .where(
                    TaskModel.id == task_id,
                    TaskModel.user_id == user_id,
                )
                .values(is_completed=status, updated_at=current_time)
            )
            result = await session.execute(stmt)
            await session.commit()
            return result.rowcount > 0
