from datetime import date
import requests
from app.core.config import get_settings


def detect_season(day: date, temperature: float = 0, rainfall: float = 0) -> str:
    month = day.month
    if rainfall > 8:
        return "monsoon"
    if month in (3, 4, 5, 6) or temperature >= 32:
        return "summer"
    if month in (11, 12, 1, 2) or temperature <= 16:
        return "winter"
    return "post-monsoon"


def fetch_weather(city: str, day: date) -> dict:
    settings = get_settings()
    if not settings.openweather_api_key:
        return {"temperature": 28.0, "rainfall": 0.0, "season": detect_season(day, 28, 0)}

    url = "https://api.openweathermap.org/data/2.5/weather"
    response = requests.get(
        url,
        params={"q": city, "appid": settings.openweather_api_key, "units": "metric"},
        timeout=8,
    )
    response.raise_for_status()
    payload = response.json()
    temperature = float(payload.get("main", {}).get("temp", 28))
    rainfall = float(payload.get("rain", {}).get("1h", 0) or payload.get("rain", {}).get("3h", 0) or 0)
    return {"temperature": temperature, "rainfall": rainfall, "season": detect_season(day, temperature, rainfall)}
