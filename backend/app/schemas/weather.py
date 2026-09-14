from typing import Literal

from pydantic import BaseModel


class LocationWeatherRequest(BaseModel):
    latitude: float
    longitude: float
    language: Literal["en", "my"] = "en"


class RegionInfo(BaseModel):
    name_en: str
    name_my: str


class CurrentWeather(BaseModel):
    temperature_c: float
    rainfall_7d_mm: float
    humidity_pct: int
    soil_pH_estimate: float


class Advisory(BaseModel):
    severity: Literal["info", "warning", "critical"]
    icon: str
    title_en: str
    title_my: str
    message_en: str
    message_my: str


class LocationWeatherResponse(BaseModel):
    region: RegionInfo
    current: CurrentWeather
    advisories: list[Advisory]
