from fastapi import APIRouter, HTTPException, status

from app.ml.plant_recommender import (
    PlantDatasetUnavailableError,
    recommend_crops,
    recommend_plants,
)
from app.schemas.crop_suggestion import (
    CropSuggestionRequest,
    CropSuggestionResponse,
    PlantSuggestionRequest,
    PlantSuggestionResponse,
)

router = APIRouter(tags=["crop-suggestion"])


@router.post(
    "/crop-suggestion",
    response_model=CropSuggestionResponse,
    status_code=status.HTTP_200_OK,
    summary="Predict the best crop for current conditions",
)
def crop_suggestion(request: CropSuggestionRequest) -> CropSuggestionResponse:
    try:
        recommendations = recommend_crops(
            request.soil_ph,
            request.rainfall_mm,
            request.temperature_c,
            language=request.language,
            limit=2,
        )
    except PlantDatasetUnavailableError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        ) from exc

    primary = recommendations[0]
    return CropSuggestionResponse(
        crop=str(primary["name"]),
        confidence_percent=float(primary["match_score"]),
        recommendations=[
            {
                "crop": recommendation["name"],
                "crop_key": recommendation["name_en"],
                "suitability_percent": recommendation["match_score"],
                "market_price_mmk_per_kg": recommendation[
                    "market_price_mmk_per_kg"
                ],
                "yield_per_acre_kg": recommendation["yield_per_acre_kg"],
                "description": recommendation["description"],
            }
            for recommendation in recommendations
        ],
    )


@router.post(
    "/plant-suggestions",
    response_model=PlantSuggestionResponse,
    summary="Recommend plants from the plants dataset",
)
def plant_suggestions(request: PlantSuggestionRequest) -> PlantSuggestionResponse:
    try:
        recommendations = recommend_plants(
            request.soil_ph,
            request.rainfall_mm,
            request.temperature_c,
            request.field_area_acres,
            language=request.language,
        )
    except PlantDatasetUnavailableError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        ) from exc
    return PlantSuggestionResponse(recommendations=recommendations)
