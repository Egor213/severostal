import punq
from fastapi import Depends, status
from fastapi.exceptions import HTTPException
from fastapi.routing import APIRouter

from src.api.http.auth.schemas import (
    CreateUserRequest,
    CreateUserResponse,
    LoginUserRequest,
    LoginUserResponse,
)
from src.api.http.schemas import ErrorSchema
from src.app import init_container
from src.services.exceptions import ServiceException
from src.services.users import UsersService

router = APIRouter(tags=["Auth"])


@router.post(
    "/register",
    status_code=status.HTTP_201_CREATED,
    description="Эндпоинт создаёт нового пользователя",
    responses={
        status.HTTP_201_CREATED: {"model": CreateUserResponse},
        status.HTTP_400_BAD_REQUEST: {"model": ErrorSchema},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": ErrorSchema},
    },
)
async def register_users_handler(
    schema: CreateUserRequest,
    container: punq.Container = Depends(init_container),
) -> CreateUserResponse:

    service: punq.Container = container.resolve(UsersService)
    try:
        token = await service.register_user(username=schema.username, password=schema.password)
    except ServiceException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail={"error": e.message})
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "Internal server error"},
        )

    return CreateUserResponse(token=token)


@router.post(
    "/login",
    status_code=status.HTTP_200_OK,
    description="Эндпоинт для авторизации пользователя",
    responses={
        status.HTTP_200_OK: {"model": LoginUserRequest},
        status.HTTP_400_BAD_REQUEST: {"model": ErrorSchema},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": ErrorSchema},
    },
)
async def login_users_handler(
    schema: LoginUserRequest,
    container: punq.Container = Depends(init_container),
) -> LoginUserResponse:

    service: punq.Container = container.resolve(UsersService)
    try:
        token = await service.login_user(username=schema.username, password=schema.password)
    except ServiceException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail={"error": e.message})
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "Internal server error"},
        )

    return LoginUserResponse(token=token)
