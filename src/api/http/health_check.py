from fastapi.routing import APIRouter

router = APIRouter(tags=["health_check"])


@router.get("/ping")
async def health_check() -> dict:
    return {"message": "pong"}
