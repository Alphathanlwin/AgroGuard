from functools import lru_cache
from math import exp
from pathlib import Path

import pandas as pd

DATA_PATH = Path(__file__).resolve().parents[1] / "data" / "plants.csv"
MYANMAR_DATA_PATH = Path(__file__).resolve().parents[1] / "data" / "plants_mm.csv"
TOWNSHIP_DATA_PATH = (
    Path(__file__).resolve().parents[1] / "data" / "township_agricultural_data.csv"
)
_CROP_NAMES_MY = {
    "Rice": "စပါး",
    "Wheat": "ဂျုံ",
    "Corn": "ပြောင်း",
    "Beans": "ပဲ",
    "Sesame": "နှမ်း",
}


class PlantDatasetUnavailableError(RuntimeError):
    """Raised when the plants dataset cannot be read."""


@lru_cache(maxsize=1)
def _load_plants() -> pd.DataFrame:
    if not DATA_PATH.is_file():
        raise PlantDatasetUnavailableError(f"Plant dataset is missing: {DATA_PATH}")
    try:
        plants = pd.read_csv(DATA_PATH)
        plants["lowest_temp"] = pd.to_numeric(plants["lowest_temp"], errors="coerce")
        plants["highest_temp"] = pd.to_numeric(plants["highest_temp"], errors="coerce")
        plants["min_area_square_feet"] = pd.to_numeric(
            plants["min_area_square_feet"], errors="coerce"
        ).fillna(1)
        return plants.dropna(subset=["plant_name", "lowest_temp", "highest_temp"])
    except Exception as exc:
        raise PlantDatasetUnavailableError("The plants dataset is invalid.") from exc


def recommend_plants(
    soil_ph: float,
    rainfall_mm: float,
    temperature_c: float,
    field_area_acres: float = 1,
    limit: int = 3,
    language: str = "en",
    crop_only: bool = False,
) -> list[dict[str, object]]:
    plants = _load_plants().copy()
    if crop_only:
        agricultural_uses = (
            "culinary|food|fruit|salad|spice|medicinal|juice|dessert|"
            "pickle|edible|cooking"
        )
        plants = plants[
            plants["plant_group"]
            .astype(str)
            .str.casefold()
            .isin({"vegetable", "fruit"})
            & plants["Uses"]
            .astype(str)
            .str.contains(agricultural_uses, case=False, regex=True)
            & ~plants["plant_name"]
            .astype(str)
            .str.contains("tree|wood", case=False, regex=True)
        ].copy()
    midpoint = (plants["lowest_temp"] + plants["highest_temp"]) / 2
    half_range = ((plants["highest_temp"] - plants["lowest_temp"]) / 2).clip(lower=1)
    temperature_difference = (midpoint - temperature_c).abs()
    temperature_score = 100 - (temperature_difference / half_range * 50)
    outside_range = temperature_difference > half_range
    temperature_score.loc[outside_range] = (
        50 - ((temperature_difference.loc[outside_range] - half_range.loc[outside_range]) * 15)
    )
    ph_penalty = abs(6.5 - soil_ph) * 8
    water_need = pd.to_numeric(
        plants["water_necessity (1Lcup/day)"], errors="coerce"
    ).fillna(1)
    water_penalty = ((water_need > 2) & (rainfall_mm < 20)).astype(int) * 10
    plants["match_score"] = (
        temperature_score - ph_penalty - water_penalty
    ).clip(15, 98)

    viable = plants[
        (temperature_c >= plants["lowest_temp"] - 2)
        & (temperature_c <= plants["highest_temp"] + 2)
    ]
    if viable.empty:
        viable = plants

    ranked = (
        viable.sort_values("match_score", ascending=False)
        .drop_duplicates("plant_name")
    )
    best = ranked.head(limit)
    localized: dict[object, tuple[str, str]] = {}
    if language == "my":
        try:
            myanmar = pd.read_csv(MYANMAR_DATA_PATH)
            localized = {
                row["plant_id"]: (
                    str(row["plant_name"]).strip(),
                    str(row.get("description", "")).strip(),
                )
                for _, row in myanmar.drop_duplicates("plant_id").iterrows()
            }
        except (OSError, ValueError, KeyError):
            localized = {}

    results: list[dict[str, object]] = []
    for _, plant in best.iterrows():
        minimum_area = max(float(plant["min_area_square_feet"]), 1)
        localized_name, localized_description = localized.get(
            plant.get("plant_id"),
            (
                str(plant["plant_name"]).strip(),
                str(plant.get("description", "")).strip(),
            ),
        )
        results.append(
            {
                "name": localized_name,
                "name_en": str(plant["plant_name"]).strip(),
                "match_score": round(float(plant["match_score"]), 1),
                "estimated_capacity": int(field_area_acres * 43_560 * 0.8 / minimum_area),
                "description": localized_description,
                "market_price_mmk_per_kg": str(
                    plant.get("Current_Market_Price_MMK_per_kg", "")
                ).strip(),
            }
        )
    return results


def recommend_crops(
    soil_ph: float,
    rainfall_mm: float,
    temperature_c: float,
    language: str = "en",
    limit: int = 2,
) -> list[dict[str, object]]:
    try:
        history = pd.read_csv(TOWNSHIP_DATA_PATH)
    except (OSError, ValueError) as exc:
        raise PlantDatasetUnavailableError(
            f"Township agriculture dataset is unavailable: {TOWNSHIP_DATA_PATH}"
        ) from exc

    recommendations = recommend_plants(
        soil_ph,
        rainfall_mm,
        temperature_c,
        limit=10,
        language=language,
        crop_only=True,
    )
    history["crop_key"] = history["best_crop"].astype(str).str.casefold()

    for recommendation in recommendations:
        crop_key = str(recommendation["name_en"]).casefold()
        crop_history = history[history["crop_key"] == crop_key]
        raw_plant_price = str(
            recommendation.get("market_price_mmk_per_kg", "")
        ).replace(",", "").strip()
        try:
            plant_price = round(float(raw_plant_price)) if raw_plant_price else 0
        except ValueError:
            plant_price = 0
        prices = (
            pd.to_numeric(crop_history["local_grain_price"], errors="coerce").dropna()
            if "local_grain_price" in crop_history
            else pd.Series(dtype=float)
        )
        yields = (
            pd.to_numeric(
                crop_history["historic_yield_tons_per_ha"],
                errors="coerce",
            ).dropna()
            if "historic_yield_tons_per_ha" in crop_history
            else pd.Series(dtype=float)
        )
        township_price = round(float(prices.mean())) if not prices.empty else 0
        recommendation["market_price_mmk_per_kg"] = plant_price or township_price
        township_yield = (
            round(float(yields.mean()) * 404.686, 1)
            if not yields.empty
            else 0
        )
        recommendation["yield_per_acre_kg"] = township_yield

    feature_names = ["soil_pH", "rainfall_mm", "temperature_c"]
    conditions = pd.Series(
        [soil_ph, rainfall_mm, temperature_c],
        index=feature_names,
    )
    scales = history[feature_names].std().replace(0, 1)
    history["distance"] = (
        ((history[feature_names] - conditions) / scales)
        .pow(2)
        .sum(axis=1)
        .pow(0.5)
    )
    township_candidates: list[dict[str, object]] = []
    existing_names = {
        str(recommendation["name_en"]).casefold()
        for recommendation in recommendations
    }
    for crop, group in history.groupby("best_crop"):
        crop_name = str(crop)
        if crop_name.casefold() in existing_names:
            continue
        nearest = group.nsmallest(20, "distance")
        suitability = max(
            0,
            min(98, 99 * exp(-0.2 * float(nearest["distance"].mean()))),
        )
        prices = pd.to_numeric(
            nearest["local_grain_price"],
            errors="coerce",
        ).dropna()
        yields = pd.to_numeric(
            nearest["historic_yield_tons_per_ha"],
            errors="coerce",
        ).dropna()
        township_candidates.append(
            {
                "name": (
                    _CROP_NAMES_MY.get(crop_name, crop_name)
                    if language == "my"
                    else crop_name
                ),
                "name_en": crop_name,
                "match_score": round(suitability, 1),
                "estimated_capacity": 0,
                "description": (
                    f"{crop_name} is supported by similar township soil "
                    "and climate records."
                ),
                "market_price_mmk_per_kg": (
                    round(float(prices.mean()))
                    if not prices.empty
                    else 0
                ),
                "yield_per_acre_kg": (
                    round(float(yields.mean()) * 404.686, 1)
                    if not yields.empty
                    else 0
                ),
            }
        )

    recommendations.extend(township_candidates)

    return sorted(
        recommendations,
        key=lambda recommendation: float(recommendation["match_score"]),
        reverse=True,
    )[:limit]
