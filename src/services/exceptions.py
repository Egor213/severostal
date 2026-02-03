class ServiceException(Exception):
    def __init__(self, message: str | None = None):
        super().__init__(message)
        self._message = message

    @property
    def message(self) -> str:
        return self._message if self._message is not None else "Error service"


class ValidationException(ServiceException):
    pass
