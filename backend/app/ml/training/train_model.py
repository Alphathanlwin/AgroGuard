from pathlib import Path

import joblib
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder

TRAINING_DIR = Path(__file__).resolve().parent
DATA_PATH = TRAINING_DIR.parents[1] / "data" / "township_agricultural_data.csv"
ARTIFACT_DIR = TRAINING_DIR.parent / "artifacts"
FEATURE_NAMES = ["soil_pH", "rainfall_mm", "temperature_c"]


def train() -> None:
    data = pd.read_csv(DATA_PATH)
    encoder = LabelEncoder()
    labels = encoder.fit_transform(data["best_crop"])
    model = RandomForestClassifier(n_estimators=200, random_state=42)
    model.fit(data[FEATURE_NAMES], labels)

    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, ARTIFACT_DIR / "crop_model.joblib")
    joblib.dump(encoder, ARTIFACT_DIR / "label_encoder.joblib")


if __name__ == "__main__":
    train()
