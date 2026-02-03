from dataclasses import dataclass
from src.services.exceptions import ServiceException


class UserAlreadyExistsEx(ServiceException):
    @property
    def message(self):
        return "user already exists"


class CannotCreateUserEx(ServiceException):
    @property
    def message(self):
        return "cannot create user"
