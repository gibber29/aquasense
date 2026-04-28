from sqlalchemy.orm import Session
from app.core.config import get_settings
from app.models.entities import Alert, WaterUsage


def create_alert(db: Session, user_id: int, message: str) -> Alert:
    alert = Alert(user_id=user_id, message=message)
    db.add(alert)
    db.commit()
    db.refresh(alert)
    return alert


def evaluate_threshold_alert(db: Session, usage: WaterUsage) -> None:
    threshold = get_settings().daily_usage_threshold
    if usage.usage_liters > threshold:
        create_alert(
            db,
            usage.user_id,
            f"Usage of {usage.usage_liters:.0f}L on {usage.date.isoformat()} exceeded the {threshold:.0f}L threshold.",
        )


def water_saving_tips(usage: float, season: str, has_anomaly: bool) -> list[str]:
    tips: list[str] = []
    if usage > get_settings().daily_usage_threshold:
        tips.append("Reduce shower duration, batch laundry, and check continuous-flow fixtures.")
    if season == "summer":
        tips.append("Water plants before sunrise and reuse rinse water where practical.")
    if has_anomaly:
        tips.append("Inspect taps, toilet tanks, and outdoor lines for leaks today.")
    if not tips:
        tips.append("Great pace. Keep logging daily to protect your conservation streak.")
    return tips
