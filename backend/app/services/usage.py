from datetime import date, timedelta
from sqlalchemy.orm import Session
from app.models.entities import User, WaterUsage
from app.schemas.dto import UsageCreate
from app.services.alerts import evaluate_threshold_alert
from app.services.gamification import update_gamification
from app.services.weather import detect_season, fetch_weather


def log_usage(db: Session, user: User, payload: UsageCreate) -> WaterUsage:
    weather = fetch_weather(user.city, payload.date)
    temperature = payload.temperature if payload.temperature is not None else weather["temperature"]
    rainfall = payload.rainfall if payload.rainfall is not None else weather["rainfall"]
    record = WaterUsage(
        user_id=user.id,
        date=payload.date,
        usage_liters=payload.usage_liters,
        season=detect_season(payload.date, temperature, rainfall),
        time_of_day=payload.time_of_day,
        temperature=temperature,
        rainfall=rainfall,
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    evaluate_threshold_alert(db, record)
    update_gamification(db, user)
    return record


def filter_usage(db: Session, user_id: int, period: str = "month") -> list[WaterUsage]:
    query = db.query(WaterUsage).filter(WaterUsage.user_id == user_id)
    today = date.today()
    if period == "week":
        query = query.filter(WaterUsage.date >= today - timedelta(days=7))
    elif period == "year":
        query = query.filter(WaterUsage.date >= today - timedelta(days=365))
    else:
        query = query.filter(WaterUsage.date >= today - timedelta(days=31))
    return query.order_by(WaterUsage.date.desc()).all()
