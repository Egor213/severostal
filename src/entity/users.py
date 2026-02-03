from datetime import datetime

from pydantic import BaseModel


class User(BaseModel):
    id: int
    password: str
    username: str
    created_at: datetime
