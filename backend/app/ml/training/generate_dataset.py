import random
from datetime import datetime, timedelta
from pathlib import Path

import numpy as np
import pandas as pd

DATA_PATH = (
    Path(__file__).resolve().parents[2] / "data" / "township_agricultural_data.csv"
)


def generate_township_data(output_path: Path = DATA_PATH, num_records: int = 2000) -> None:
    np.random.seed(42)
    random.seed(42)
    townships = [
        "Yangon", "Mandalay", "Bago", "Taungoo", "Magway",
        "Monywa", "Sagaing", "Naypyidaw", "Meiktila", "Pathein",
    ]
    crops = []
    start_date = datetime(2018, 1, 1)

    for _ in range(num_records):
        rainfall = round(random.uniform(10, 600), 1)
        soil_ph = round(random.uniform(5.0, 8.5), 1)
        temperature = round(random.uniform(20.0, 40.0), 1)
        if rainfall > 400 and soil_ph > 6:
            best_crop = "Rice"
        elif rainfall < 100:
            best_crop = "Sesame"
        elif temperature < 25:
            best_crop = "Wheat"
        elif 200 < rainfall < 400:
            best_crop = "Corn"
        else:
            best_crop = "Beans"
        crops.append({
            "township": random.choice(townships),
            "date": (start_date + timedelta(days=random.randint(0, 365 * 6))).date(),
            "soil_pH": soil_ph,
            "rainfall_mm": rainfall,
            "temperature_c": temperature,
            "local_grain_price": round(random.uniform(500, 2000)),
            "historic_yield_tons_per_ha": round(random.uniform(1, 8), 2),
            "best_crop": best_crop,
        })

    output_path.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(crops).to_csv(output_path, index=False)


if __name__ == "__main__":
    generate_township_data()
