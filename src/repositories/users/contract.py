from abc import ABC, abstractmethod


class IUsersRepo(ABC):
    @abstractmethod
    async def register_user(self, username: str, hashed_password: str) -> tuple[int, str]: ...
