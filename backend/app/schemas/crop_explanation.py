from typing import Literal

from pydantic import BaseModel


class CropExplanationRequest(BaseModel):
    soil_pH: float
    rainfall_mm: float
    temperature_c: float
    crop: str
    language: Literal["en", "my"] = "en"
