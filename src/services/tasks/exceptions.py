from src.services.exceptions import ServiceException


class CannotCreateTaskEx(ServiceException):
    @property
    def message(self):
        return "cannot create task"


class CannotGetUserTaskByIdEx(ServiceException):
    @property
    def message(self):
        return "cannot get user task by id"


class TaskNotFoundEx(ServiceException):
    @property
    def message(self):
        return "task not founnd"


class CannotGetUserTasksEx(ServiceException):
    @property
    def message(self):
        return "cannot get user tasks"


class CannotDeleteUserTaskByIdEx(ServiceException):
    @property
    def message(self):
        return "cannot delete user task by id"


class CannotMarkUserTaskByIdEx(ServiceException):
    @property
    def message(self):
        return "cannot change mark user task by id"
