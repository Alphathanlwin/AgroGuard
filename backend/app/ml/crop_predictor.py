from functools import lru_cache
from pathlib import Path

import joblib
import numpy as np
import pandas as pd

ARTIFACT_DIR = Path(__file__).resolve().parent / "artifacts"
MODEL_PATH = ARTIFACT_DIR / "crop_model.joblib"
LABEL_ENCODER_PATH = ARTIFACT_DIR / "label_encoder.joblib"
FEATURE_NAMES = ["soil_pH", "rainfall_mm", "temperature_c"]
TRAINING_DATA_PATH = (
    Path(__file__).resolve().parent / "training" / "data" / "township_agricultural_data.csv"
)


class CropModelUnavailableError(RuntimeError):
    """Raised when the crop model artifacts cannot be loaded."""


@lru_cache(maxsize=1)
def _load_artifacts():
    missing = [
        str(path)
        for path in (MODEL_PATH, LABEL_ENCODER_PATH)
        if not path.is_file()
    ]
    if missing:
        raise CropModelUnavailableError(
            f"Missing crop model artifact(s): {', '.join(missing)}"
        )

    try:
        return joblib.load(MODEL_PATH), joblib.load(LABEL_ENCODER_PATH)
    except Exception as exc:
        raise CropModelUnavailableError(
            "The crop model artifacts could not be loaded. "
            "Retrain them with this project's Python environment."
        ) from exc


def predict_crop(
    soil_ph: float,
    rainfall_mm: float,
    temperature_c: float,
) -> tuple[str, float]:
    model, label_encoder = _load_artifacts()
    features = pd.DataFrame(
        [[soil_ph, rainfall_mm, temperature_c]],
        columns=FEATURE_NAMES,
    )
    encoded_prediction = model.predict(features)
    crop = str(label_encoder.inverse_transform(encoded_prediction)[0])

    confidence = 1.0
    if hasattr(model, "predict_proba"):
        confidence = float(model.predict_proba(features)[0].max())

    return crop, round(confidence * 100, 1)


def predict_crops(
    soil_ph: float,
    rainfall_mm: float,
    temperature_c: float,
) -> list[tuple[str, float]]:
    _, label_encoder = _load_artifacts()
    try:
        training_data = pd.read_csv(TRAINING_DATA_PATH)
    except (OSError, ValueError) as exc:
        raise CropModelUnavailableError(
            f"Crop suitability data could not be loaded: {TRAINING_DATA_PATH}"
        ) from exc

    user_conditions = np.array([soil_ph, rainfall_mm, temperature_c], dtype=float)
    scales = training_data[FEATURE_NAMES].std().to_numpy()
    suitability: list[tuple[str, float]] = []

    for crop in label_encoder.classes_:
        crop_rows = training_data[training_data["best_crop"] == crop][FEATURE_NAMES]
        distances = np.linalg.norm(
            (crop_rows.to_numpy() - user_conditions) / scales,
            axis=1,
        )
        nearest_distance = float(np.sort(distances)[:10].mean())
        score = max(0, min(99, 99 * np.exp(-0.2 * nearest_distance)))
        suitability.append((str(crop), round(float(score), 1)))

    return sorted(suitability, key=lambda item: item[1], reverse=True)[:2]
