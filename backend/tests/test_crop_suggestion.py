from unittest.mock import patch

import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app


@pytest.mark.asyncio
async def test_crop_suggestion() -> None:
    transport = ASGITransport(app=app)
    with patch(
        "app.api.v1.endpoints.crop_suggestion.recommend_crops",
        return_value=[
            {
                "name": "Rice",
                "name_en": "Rice",
                "match_score": 94.5,
                "market_price_mmk_per_kg": 1500,
                "yield_per_acre_kg": 2000,
                "description": "Rice description",
            },
            {
                "name": "Corn",
                "name_en": "Corn",
                "match_score": 88.0,
                "market_price_mmk_per_kg": 1000,
                "yield_per_acre_kg": 1800,
                "description": "Corn description",
            },
        ],
    ):
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.post(
                "/api/v1/crop-suggestion",
                json={
                    "soil_pH": 6.5,
                    "rainfall_mm": 450,
                    "temperature_c": 28,
                },
            )

    assert response.status_code == 200
    assert response.json() == {
        "crop": "Rice",
        "confidencePercent": 94.5,
        "recommendations": [
            {
                "crop": "Rice",
                "cropKey": "Rice",
                "suitabilityPercent": 94.5,
                "marketPriceMmkPerKg": 1500.0,
                "yieldPerAcreKg": 2000.0,
                "description": "Rice description",
            },
            {
                "crop": "Corn",
                "cropKey": "Corn",
                "suitabilityPercent": 88.0,
                "marketPriceMmkPerKg": 1000.0,
                "yieldPerAcreKg": 1800.0,
                "description": "Corn description",
            },
        ],
    }


@pytest.mark.asyncio
async def test_plant_suggestions_from_dataset() -> None:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/api/v1/plant-suggestions",
            json={
                "soil_pH": 6.5,
                "rainfall_mm": 100,
                "temperature_c": 28,
                "field_area_acres": 1,
            },
        )

    assert response.status_code == 200
    recommendations = response.json()["recommendations"]
    assert len(recommendations) == 3
    assert all(item["name"] for item in recommendations)
