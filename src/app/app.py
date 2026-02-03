from functools import lru_cache

import punq

from src.config import Config
from src.database import Database, UnitOfWork
from src.repositories.tasks import ITasksRepo, TasksRepoPdb
from src.repositories.users import IUsersRepo, UsersRepoPdb
from src.services import TasksService, UsersService


@lru_cache(1)
def init_container() -> punq.Container:
    container = punq.Container()
    container.register(Config, instance=Config(), scope=punq.Scope.singleton)

    config = container.resolve(Config)

    container.register(Database, instance=Database(config), scope=punq.Scope.singleton)
    db = container.resolve(Database)

    container.register(UnitOfWork, instance=UnitOfWork(db), scope=punq.Scope.singleton)
    uow = container.resolve(UnitOfWork)


    # Repos
    container.register(ITasksRepo, instance=TasksRepoPdb(db), scope=punq.Scope.singleton)
    container.register(IUsersRepo, instance=UsersRepoPdb(db), scope=punq.Scope.singleton)

    tasks_repo = container.resolve(ITasksRepo)
    users_repo = container.resolve(IUsersRepo)

    # Services
    container.register(TasksService, instance=TasksService(tasks_repo, uow), scope=punq.Scope.singleton)
    container.register(UsersService, instance=UsersService(users_repo, uow), scope=punq.Scope.singleton)

    return container
