from pydantic import BaseModel


class CreateUserRequest(BaseModel):
    username: str = "test"
    password: str = "test"


class CreateUserResponse(BaseModel):
    token: str


class LoginUserRequest(BaseModel):
    username: str = "test"
    password: str = "test"


class LoginUserResponse(BaseModel):
    token: str
