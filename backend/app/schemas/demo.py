from typing import Literal

from app.schemas.base import APIModel


class DemoResetRequest(APIModel):
    scenario: Literal["healthy", "dry-soil", "heat-stress"] = "healthy"
