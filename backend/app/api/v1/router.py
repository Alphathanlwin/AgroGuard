from fastapi import APIRouter

from app.api.v1.endpoints.alerts import router as alerts_router
from app.api.v1.endpoints.analytics import router as analytics_router
from app.api.v1.endpoints.assessments import router as assessments_router
from app.api.v1.endpoints.chat import router as chat_router
from app.api.v1.endpoints.crop_explanation import router as crop_explanation_router
from app.api.v1.endpoints.crop_profiles import router as crop_profiles_router
from app.api.v1.endpoints.crop_suggestion import router as crop_suggestion_router
from app.api.v1.endpoints.crop_suitability import router as crop_suitability_router
from app.api.v1.endpoints.dashboard import router as dashboard_router
from app.api.v1.endpoints.demo import router as demo_router
from app.api.v1.endpoints.devices import router as devices_router
from app.api.v1.endpoints.disease import router as disease_router
from app.api.v1.endpoints.fields import router as fields_router
from app.api.v1.endpoints.growth import router as growth_router
from app.api.v1.endpoints.health import router as health_router
from app.api.v1.endpoints.health_updates import router as health_updates_router
from app.api.v1.endpoints.location_weather import router as location_weather_router
from app.api.v1.endpoints.ndvi import router as ndvi_router
from app.api.v1.endpoints.observations import router as observations_router
from app.api.v1.endpoints.regions import router as regions_router

api_router = APIRouter()
api_router.include_router(analytics_router)
api_router.include_router(assessments_router)
api_router.include_router(alerts_router)
api_router.include_router(chat_router)
api_router.include_router(crop_explanation_router)
api_router.include_router(crop_profiles_router)
api_router.include_router(crop_suggestion_router)
api_router.include_router(crop_suitability_router)
api_router.include_router(dashboard_router)
api_router.include_router(demo_router)
api_router.include_router(devices_router)
api_router.include_router(disease_router)
api_router.include_router(fields_router)
api_router.include_router(growth_router)
api_router.include_router(health_router)
api_router.include_router(health_updates_router)
api_router.include_router(location_weather_router)
api_router.include_router(ndvi_router)
api_router.include_router(observations_router)
api_router.include_router(regions_router)

