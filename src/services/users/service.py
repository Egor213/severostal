from src.database import UnitOfWork
from src.repositories.users import IUsersRepo

from asyncpg.exceptions import UniqueViolationError
from src.services.users.exceptions import UserAlreadyExistsEx, CannotCreateUserEx
from logging import Logger


class UsersService:

    def __init__(self, users_repo: IUsersRepo, uow: UnitOfWork, logger: Logger | None = None):
        self.users_repo = users_repo
        self.logger = logger
        self.uow = uow

    async def register_user(self, username: str, password: str):
        try:
            id = await self.users_repo.add_user(username, password)
            return id
        except UniqueViolationError:
            self.logger.error(f"user with username: {username} already exists")
            raise UserAlreadyExistsEx()
        except Exception as e:
            self.logger.error(f"unknown error: {e}")
            raise CannotCreateUserEx()
