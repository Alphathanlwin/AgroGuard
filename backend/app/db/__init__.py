"""Database package."""

from app.db.models import (  # noqa: F401 — register models with Base.metadata
    Alert,
    Assessment,
    CropProfile,
    CropRequirement,
    Field,
    FieldContextSnapshot,
    GrowthEvent,
    GrowthSimulation,
    HealthUpdate,
    NDVIMeasurement,
    Notification,
    Region,
    SensorDevice,
    SensorObservation,
)

