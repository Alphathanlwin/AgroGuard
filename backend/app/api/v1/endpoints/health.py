from typing import Annotated

from fastapi import APIRouter, Depends, status

from app.core.config import Settings, get_settings
from app.schemas.health import HealthResponse

router = APIRouter(tags=["health"])


@router.get(
    "/health",
    response_model=HealthResponse,
    status_code=status.HTTP_200_OK,
    summary="Get API health",
)
async def health(settings: Annotated[Settings, Depends(get_settings)]) -> HealthResponse:
    return HealthResponse(
        status="ok",
        service_name=settings.app_name,
        version=settings.app_version,
        environment=settings.environment,
    )

