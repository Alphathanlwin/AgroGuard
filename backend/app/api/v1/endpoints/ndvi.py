from fastapi import APIRouter, HTTPException, status

from app.schemas.ndvi import NDVIResponse
from app.services.agriculture_data import AgricultureDatasetError, ndvi_series

router = APIRouter(tags=["ndvi"])


@router.get(
    "/ndvi/{pcode}",
    response_model=NDVIResponse,
    status_code=status.HTTP_200_OK,
    summary="Get NDVI data for a region",
)
def get_ndvi_data(pcode: str) -> NDVIResponse:
    try:
        data = ndvi_series(pcode)
    except AgricultureDatasetError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        ) from exc
    if not data["labels"]:
        raise HTTPException(status_code=404, detail=f"No NDVI data found for region {pcode}")
    return NDVIResponse(**data)
