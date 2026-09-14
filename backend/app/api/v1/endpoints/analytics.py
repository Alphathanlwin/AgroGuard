from fastapi import APIRouter, HTTPException, Query, status

from app.services.agriculture_data import (
    AgricultureDatasetError,
    crop_analysis,
    dashboard_data,
    dataset_summary,
    ndvi_rainfall_correlation,
    ndvi_regions,
    ndvi_series,
)

router = APIRouter(prefix="/analytics", tags=["analytics"])


def _run(operation):
    try:
        return operation()
    except AgricultureDatasetError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        ) from exc


@router.get("/dataset-summary")
def get_dataset_summary():
    return _run(dataset_summary)


@router.get("/dashboard-data")
def get_dashboard_data():
    return _run(dashboard_data)


@router.get("/crop-analysis")
def get_crop_analysis():
    return _run(crop_analysis)


@router.get("/ndvi-regions")
def get_ndvi_regions():
    return _run(ndvi_regions)


@router.get("/ndvi-data")
def get_ndvi_data(pcode: str | None = Query(default=None)):
    return _run(lambda: ndvi_series(pcode))


@router.get("/ndvi-rainfall-correlation")
def get_ndvi_rainfall_correlation():
    return _run(ndvi_rainfall_correlation)
