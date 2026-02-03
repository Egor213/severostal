from pydantic import BaseModel


class CreateUserRequest(BaseModel):
    username: str
    password: str


class CreateUserResponse(BaseModel):
    id: int
    token: str
