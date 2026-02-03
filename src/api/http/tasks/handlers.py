import punq
from fastapi import Depends, Response
from fastapi.routing import APIRouter

from src.api.http.depends import get_current_user
from src.app import init_container
from src.services.tasks import TasksService
from src.utils.jwt import create_access_token
from src.utils.password import get_password_hash

router = APIRouter(prefix="/tasks", tags=["Tasks"])


@router.get("/test")
async def test_handler(
    user=Depends(get_current_user),
    container: punq.Container = Depends(init_container),
) -> Response:
    # service = container.resolve(TasksService)
    # await service.get_all_tasks()
    p = get_password_hash("123")

    return Response()
