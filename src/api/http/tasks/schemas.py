from datetime import datetime

from pydantic import BaseModel


class CreateTaskRequest(BaseModel):
    title: str = "title"
    description: str = "description"


class CreateTaskResponse(BaseModel):
    id: int


class DeleteTaskResponse(BaseModel):
    is_deleted: bool


class GetTaskResponse(BaseModel):
    id: int = 1
    title: str = "title"
    description: str = "description"
    is_completed: bool = False
    user_id: int = 1
    created_at: datetime
    updated_at: datetime


class MarkTaskResponse(BaseModel):
    is_changed: bool
