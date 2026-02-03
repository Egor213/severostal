from datetime import datetime

from pydantic import BaseModel


class Task(BaseModel):
    id: int
    title: str
    description: str
    is_completed: bool
    user_id: int
    created_at: datetime
    updated_at: datetime
