from typing import Literal

from app.schemas.base import APIModel


class HealthResponse(APIModel):
    status: Literal["ok"]
    service_name: str
    version: str
    environment: str

