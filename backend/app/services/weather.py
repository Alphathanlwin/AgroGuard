from httpx import AsyncClient

from app.core.config import get_settings

_PCODE_DATA: list[tuple[str, str, str, float, float]] = [
    ("MMR001", "Sagaing Region", "စစ်ကိုင်းတိုင်းဒေသကြီး", 21.88, 95.98),
    ("MMR002", "Bago Region", "ပဲခူးတိုင်းဒေသကြီး", 17.34, 96.48),
    ("MMR003", "Magway Region", "မကွေးတိုင်းဒေသကြီး", 20.15, 94.92),
    ("MMR004", "Mandalay Region", "မန္တလေးတိုင်းဒေသကြီး", 21.98, 96.09),
    ("MMR005", "Tanintharyi Region", "တနင်္သာရီတိုင်းဒေသကြီး", 13.04, 98.56),
    ("MMR006", "Ayeyarwady Region", "ဧရာဝတီတိုင်းဒေသကြီး", 16.77, 94.73),
    ("MMR007", "Kachin State", "ကချင်ပြည်နယ်", 25.57, 97.31),
    ("MMR008", "Kayah State", "ကယားပြည်နယ်", 19.23, 97.26),
    ("MMR009", "Kayin State", "ကရင်ပြည်နယ်", 17.25, 97.80),
    ("MMR010", "Chin State", "ချင်းပြည်နယ်", 22.01, 93.58),
    ("MMR011", "Mon State", "မွန်ပြည်နယ်", 16.32, 97.65),
    ("MMR012", "Rakhine State", "ရခိုင်ပြည်နယ်", 19.74, 93.98),
    ("MMR013", "Shan State (North)", "ရှမ်းပြည်နယ် (မြောက်ပိုင်း)", 22.43, 97.69),
    ("MMR014", "Yangon Region", "ရန်ကုန်တိုင်းဒေသကြီး", 16.87, 96.19),
    ("MMR015", "Nay Pyi Taw", "နေပြည်တော်", 19.75, 96.13),
    ("MMR016", "Shan State (South)", "ရှမ်းပြည်နယ် (တောင်ပိုင်း)", 20.79, 97.04),
    ("MMR017", "Shan State (East)", "ရှမ်းပြည်နယ် (အရှေ့ပိုင်း)", 21.38, 99.61),
    ("MMR018", "Bago Region (East)", "ပဲခူးတိုင်းဒေသကြီး (အရှေ့ပိုင်း)", 17.34, 96.48),
]

PCODE_MAP: dict[str, dict] = {}
for pcode, name_en, name_my, lat, lon in _PCODE_DATA:
    PCODE_MAP[pcode] = {"name_en": name_en, "name_my": name_my, "lat": lat, "lon": lon}

SOIL_PH_MAP = {
    "MMR001": 6.8, "MMR002": 6.2, "MMR003": 7.1, "MMR004": 7.3,
    "MMR005": 5.5, "MMR006": 5.8, "MMR007": 6.5, "MMR008": 6.0,
    "MMR009": 5.7, "MMR010": 6.3, "MMR011": 5.9, "MMR012": 6.6,
    "MMR013": 6.4, "MMR014": 6.2, "MMR015": 6.9, "MMR016": 6.4,
    "MMR017": 6.1, "MMR018": 6.2,
}

HUMIDITY_MAP = {
    "MMR001": 65, "MMR002": 75, "MMR003": 55, "MMR004": 50,
    "MMR005": 80, "MMR006": 82, "MMR007": 70, "MMR008": 68,
    "MMR009": 78, "MMR010": 72, "MMR011": 76, "MMR012": 74,
    "MMR013": 65, "MMR014": 78, "MMR015": 60, "MMR016": 65,
    "MMR017": 62, "MMR018": 75,
}


def _get_ow_api_key() -> str | None:
    settings = get_settings()
    return settings.openweather_api_key.get_secret_value() if settings.openweather_api_key else None


async def _fetch_openweather(lat: float, lon: float) -> dict | None:
    api_key = _get_ow_api_key()
    if not api_key:
        return None

    settings = get_settings()
    base = settings.openweather_base_url.rstrip("/")
    url = f"{base}/data/2.5/weather?lat={lat}&lon={lon}&appid={api_key}&units=metric"
    async with AsyncClient(timeout=10) as client:
        response = await client.get(url)
        if response.status_code == 200:
            return response.json()
    return None


def _find_nearest_region(lat: float, lon: float) -> tuple[str, dict]:
    import math

    best_pcode = "MMR014"
    best_dist = float("inf")
    for pcode, info in PCODE_MAP.items():
        dlat = info["lat"] - lat
        dlon = info["lon"] - lon
        dist = math.sqrt(dlat * dlat + dlon * dlon)
        if dist < best_dist:
            best_dist = dist
            best_pcode = pcode
    return best_pcode, PCODE_MAP[best_pcode]


def _estimate_soil_pH(lat: float, lon: float) -> float:
    pcode, _ = _find_nearest_region(lat, lon)
    return SOIL_PH_MAP.get(pcode, 6.5)


def _estimate_humidity(lat: float, lon: float) -> int:
    pcode, _ = _find_nearest_region(lat, lon)
    return HUMIDITY_MAP.get(pcode, 70)


def _generate_advisories(
    temp: float, rainfall: float, humidity: float,
) -> list[dict]:
    advisories = []

    if temp > 38:
        advisories.append({
            "severity": "warning",
            "icon": "🔥",
            "title_en": "Extreme Heat Alert",
            "title_my": "အပူလွန်ကဲသတိပေးချက်",
            "message_en": (
                "Temperatures are very high. Ensure adequate irrigation "
                "and consider shade for sensitive crops."
            ),
            "message_my": (
                "အပူချိန်အလွန်မြင့်မားနေပါသည်။ လုံလောက်သောရေသွင်းမှုသေချာစေပြီး "
                "ထိခိုက်လွယ်သောသီးနှံများအတွက် အရိပ်ပေးပါ။"
            ),
        })
    elif temp < 15:
        advisories.append({
            "severity": "info",
            "icon": "🥶",
            "title_en": "Cool Weather Advisory",
            "title_my": "အေးမြသောရာသီဥတုအကြံပြုချက်",
            "message_en": (
                "Cool conditions may slow crop growth. Consider cold-tolerant varieties."
            ),
            "message_my": (
                "အေးမြသောရာသီဥတုသည် သီးနှံကြီးထွားမှုကို နှေးကွေးစေနိုင်ပါသည်။ "
                "အအေးဒဏ်ခံနိုင်သောမျိုးများကို စဉ်းစားပါ။"
            ),
        })

    if rainfall > 200:
        advisories.append({
            "severity": "warning",
            "icon": "🌧️",
            "title_en": "Heavy Rainfall Warning",
            "title_my": "မိုးသည်းထန်စွာရွာသွန်းမှုသတိပေးချက်",
            "message_en": (
                "Very high rainfall detected. Ensure proper drainage to prevent waterlogging."
            ),
            "message_my": (
                "မိုးရေချိန်အလွန်များနေပါသည်။ ရေဝပ်ခြင်းကိုကာကွယ်ရန် "
                "ရေနုတ်မြောင်းကောင်းမွန်စွာထားပါ။"
            ),
        })
    elif rainfall < 20:
        advisories.append({
            "severity": "warning",
            "icon": "🏜️",
            "title_en": "Dry Conditions Alert",
            "title_my": "ခြောက်သွေ့မှုသတိပေးချက်",
            "message_en": (
                "Low rainfall detected. Increase irrigation frequency "
                "and consider drought-resistant crops."
            ),
            "message_my": (
                "မိုးရေချိန်နည်းပါးနေပါသည်။ ရေသွင်းနှုန်းတိုးမြှင့်ပြီး "
                "မိုးခေါင်ဒဏ်ခံနိုင်သော သီးနှံများကို စဉ်းစားပါ။"
            ),
        })

    if humidity > 80:
        advisories.append({
            "severity": "info",
            "icon": "💧",
            "title_en": "High Humidity Advisory",
            "title_my": "စိုထိုင်းဆများခြင်းအကြံပြုချက်",
            "message_en": (
                "High humidity increases risk of fungal diseases. Monitor crops closely."
            ),
            "message_my": (
                "စိုထိုင်းဆများခြင်းသည် မှိုရောဂါဖြစ်နိုင်ခြေကိုမြင့်စေပါသည်။ "
                "သီးနှံများကို အနီးကပ်စောင့်ကြည့်ပါ။"
            ),
        })

    if not advisories:
        advisories.append({
            "severity": "info",
            "icon": "✅",
            "title_en": "Favorable Conditions",
            "title_my": "သင့်တော်သောအခြေအနေများ",
            "message_en": "Current conditions are generally favorable for crop growth.",
            "message_my": (
                "လက်ရှိအခြေအနေများသည် သီးနှံစိုက်ပျိုးရန်အတွက် "
                "ယေဘုယျအားဖြင့် သင့်တော်ပါသည်။"
            ),
        })

    return advisories


async def get_location_weather(lat: float, lon: float, language: str) -> dict:
    pcode, region = _find_nearest_region(lat, lon)
    ow_data = await _fetch_openweather(lat, lon)

    if ow_data:
        temp = ow_data["main"]["temp"]
        humidity = ow_data["main"]["humidity"]
        rainfall = (
            ow_data.get("rain", {}).get("1h", 0)
            or ow_data.get("rain", {}).get("3h", 0)
            or 0
        )
        rainfall_7d = rainfall * 7
    else:
        temp = 28.0
        humidity = _estimate_humidity(lat, lon)
        rainfall_7d = 120

    soil_pH = _estimate_soil_pH(lat, lon)
    advisories = _generate_advisories(temp, rainfall_7d, humidity)

    return {
        "region": {
            "name_en": region["name_en"],
            "name_my": region["name_my"],
        },
        "current": {
            "temperature_c": round(temp, 1),
            "rainfall_7d_mm": round(rainfall_7d, 1),
            "humidity_pct": humidity,
            "soil_pH_estimate": soil_pH,
        },
        "advisories": advisories,
    }
