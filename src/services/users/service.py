import logging

from sqlalchemy.exc import IntegrityError

from src.app.logger import NullLogger
from src.database import UnitOfWork
from src.repositories.users import IUsersRepo
from src.services.exceptions import ValidationException
from src.services.users.exceptions import (
    CannotCreateUserEx,
    CannotLoginUserEx,
    InvalidLoginParamsEx,
    UserAlreadyExistsEx,
)
from src.services.users.validators import validate_user_input
from src.utils.jwt import create_access_token
from src.utils.password import get_password_hash, verify_password


class UsersService:

    def __init__(
        self, users_repo: IUsersRepo, uow: UnitOfWork, logger: logging.Logger | None = None
    ):
        self.users_repo = users_repo
        self.logger = logger or NullLogger()
        self.uow = uow

    async def register_user(self, username: str, password: str):
        try:
            validate_user_input(username, password)
            hashed_password = get_password_hash(password)
            id = await self.users_repo.add_user(username, hashed_password)
            token = create_access_token({"id": id})
            self.logger.debug(f"user created: id={id}, username={username}")
            return token
        except ValidationException as e:
            self.logger.error(f"validation error: {e}")
            raise e
        except IntegrityError as e:
            error_msg = str(e).lower()
            if "duplicate key" in error_msg and "users_username_key" in error_msg:
                self.logger.error(f"user with username: {username} already exists")
                raise UserAlreadyExistsEx()

            self.logger.error(f"database integrity error: {e}")
            raise CannotCreateUserEx(reason="Database integrity error")
        except Exception as e:
            self.logger.error(f"unknown error: {e}")
            raise CannotCreateUserEx()

    async def login_user(self, username: str, password: str):
        try:
            user = await self.users_repo.get_user_by_username(username)
        except Exception as e:
            self.logger.error(f"unknown error: {e}")
            raise

        if not user or not verify_password(password, user.hashed_password):
            self.logger.error(f"invalid loging params: {e}")
            raise InvalidLoginParamsEx()

        try:
            validate_user_input(username, password)
            token = create_access_token({"id": user.id})
            self.logger.debug(f"user login: id={user.id}, username={user.username}")
            return token
        except ValidationException as e:
            self.logger.error(f"validation error: {e}")
            raise e
        except Exception as e:
            self.logger.error(f"unknown error: {e}")
            raise CannotLoginUserEx()
