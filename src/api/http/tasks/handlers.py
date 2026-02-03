import punq
from fastapi import Depends, status
from fastapi.exceptions import HTTPException
from fastapi.routing import APIRouter

from src.api.http.depends import get_current_user
from src.api.http.schemas import ErrorSchema
from src.api.http.tasks.schemas import (
    CreateTaskRequest,
    CreateTaskResponse,
    DeleteTaskResponse,
    GetTaskResponse,
    MarkTaskResponse,
)
from src.app import init_container
from src.services.exceptions import ServiceException
from src.services.tasks import TasksService

router = APIRouter(prefix="/tasks", tags=["Tasks"])


@router.post(
    "/",
    status_code=status.HTTP_200_OK,
    description="Эндпоинт для создания таски",
    responses={
        status.HTTP_201_CREATED: {"model": CreateTaskResponse},
        status.HTTP_400_BAD_REQUEST: {"model": ErrorSchema},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": ErrorSchema},
    },
)
async def create_task_handler(
    schema: CreateTaskRequest,
    user: dict = Depends(get_current_user),
    container: punq.Container = Depends(init_container),
) -> CreateTaskResponse:

    service: punq.Container = container.resolve(TasksService)
    try:
        id = await service.create_task(
            user_id=user["id"], title=schema.title, descr=schema.description
        )
    except ServiceException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail={"error": e.message})
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "Internal server error"},
        )

    return CreateTaskResponse(id=id)


@router.get(
    "/{task_id}",
    status_code=status.HTTP_200_OK,
    description="Эндпоинт для получения таски по id",
    responses={
        status.HTTP_200_OK: {"model": GetTaskResponse},
        status.HTTP_400_BAD_REQUEST: {"model": ErrorSchema},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": ErrorSchema},
    },
)
async def get_task_by_id_handler(
    task_id: int,
    user: dict = Depends(get_current_user),
    container: punq.Container = Depends(init_container),
) -> GetTaskResponse:

    service: punq.Container = container.resolve(TasksService)
    try:
        task = await service.get_user_task_by_id(user_id=user["id"], task_id=task_id)
    except ServiceException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail={"error": e.message})
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "Internal server error"},
        )

    return GetTaskResponse(
        id=task.id,
        title=task.title,
        description=task.description,
        is_completed=task.is_completed,
        user_id=task.user_id,
        created_at=task.created_at,
        updated_at=task.updated_at,
    )


@router.get(
    "/",
    status_code=status.HTTP_200_OK,
    description="Эндпоинт для получения все тасок пользователя",
    responses={
        status.HTTP_200_OK: {"model": list[GetTaskResponse]},
        status.HTTP_400_BAD_REQUEST: {"model": ErrorSchema},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": ErrorSchema},
    },
)
async def get_task_handler(
    offset: int | None = None,
    limit: int | None = None,
    user: dict = Depends(get_current_user),
    container: punq.Container = Depends(init_container),
) -> list[GetTaskResponse]:

    service: punq.Container = container.resolve(TasksService)
    try:
        tasks = await service.get_user_tasks(user_id=user["id"], offset=offset, limit=limit)
    except ServiceException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail={"error": e.message})
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "Internal server error"},
        )

    return [
        GetTaskResponse(
            id=task.id,
            title=task.title,
            description=task.description,
            is_completed=task.is_completed,
            user_id=task.user_id,
            created_at=task.created_at,
            updated_at=task.updated_at,
        )
        for task in tasks
    ]


@router.delete(
    "/{task_id}",
    status_code=status.HTTP_200_OK,
    description="Эндпоинт для удаления таски по id",
    responses={
        status.HTTP_200_OK: {"model": DeleteTaskResponse},
        status.HTTP_400_BAD_REQUEST: {"model": ErrorSchema},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": ErrorSchema},
    },
)
async def delete_task_by_id_handler(
    task_id: int,
    user: dict = Depends(get_current_user),
    container: punq.Container = Depends(init_container),
) -> DeleteTaskResponse:

    service: punq.Container = container.resolve(TasksService)
    try:
        is_deleted = await service.delete_user_task_by_id(user_id=user["id"], task_id=task_id)
    except ServiceException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail={"error": e.message})
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "Internal server error"},
        )

    return DeleteTaskResponse(is_deleted=is_deleted)


@router.patch(
    "/{task_id}",
    status_code=status.HTTP_200_OK,
    description="Эндпоинт для удаления таски по id",
    responses={
        status.HTTP_200_OK: {"model": MarkTaskResponse},
        status.HTTP_400_BAD_REQUEST: {"model": ErrorSchema},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": ErrorSchema},
    },
)
async def mark_user_task(
    task_id: int,
    is_completed: bool,
    user: dict = Depends(get_current_user),
    container: punq.Container = Depends(init_container),
) -> MarkTaskResponse:

    service: punq.Container = container.resolve(TasksService)
    try:
        is_changed = await service.mark_user_task_by_id(
            user_id=user["id"], task_id=task_id, status=is_completed
        )
    except ServiceException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail={"error": e.message})
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "Internal server error"},
        )

    return MarkTaskResponse(is_changed=is_changed)
