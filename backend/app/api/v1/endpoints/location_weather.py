from fastapi import APIRouter, status

from app.schemas.weather import LocationWeatherRequest, LocationWeatherResponse
from app.services.weather import get_location_weather

router = APIRouter(tags=["location-weather"])


@router.post(
    "/location-weather",
    response_model=LocationWeatherResponse,
    status_code=status.HTTP_200_OK,
    summary="Get weather and soil data for a location",
)
async def location_weather(request: LocationWeatherRequest):
    data = await get_location_weather(request.latitude, request.longitude, request.language)
    return LocationWeatherResponse(**data)
