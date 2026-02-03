from src.services.exceptions import ServiceException


class UserAlreadyExistsEx(ServiceException):
    @property
    def message(self):
        return "user already exists"


class CannotCreateUserEx(ServiceException):
    @property
    def message(self):
        return "cannot create user"


class CannotLoginUserEx(ServiceException):
    @property
    def message(self):
        return "cannot login user"


class InvalidLoginParamsEx(ServiceException):
    @property
    def message(self):
        return "invalid login params"


class UserNotFoundEx(ServiceException):
    @property
    def message(self):
        return "user not found"
