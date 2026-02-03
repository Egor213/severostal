from datetime import datetime

from pydantic import BaseModel


class UserOutDto(BaseModel):
    id: int
    username: str
    hashed_password: str
    created_at: datetime

    # model_validate
