from src.repositories.users import IUsersRepo
from src.database import UnitOfWork

class UsersService:

    def __init__(self, users_repo: IUsersRepo, uow: UnitOfWork):
        self.users_repo = users_repo
        self.uow = uow

    async def register_user(self, username: str, password: str):
        print("Hello")
        return 1, "das23"
