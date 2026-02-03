import punq
from fastapi import Depends, status
from fastapi.exceptions import HTTPException
from fastapi.routing import APIRouter

from src.api.http.auth.schemas import CreateUserRequest, CreateUserResponse
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
    },
)
async def register_users_handler(
    schema: CreateUserRequest,
    container: punq.Container = Depends(init_container),
) -> CreateUserResponse:
    service: punq.Container = container.resolve(UsersService)

    try:
        id, token = await service.register_user(username=schema.username, password=schema.password)
    except ServiceException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail={"error": e.message})

    return CreateUserResponse(id=id, token=token)
