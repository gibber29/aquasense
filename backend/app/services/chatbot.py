from openai import OpenAI
from sqlalchemy.orm import Session
from app.core.config import get_settings
from app.models.entities import Anomaly, User, WaterUsage
from app.services.alerts import water_saving_tips
from app.services.ml import predict_next_7_days


def aquabot_answer(db: Session, user: User, message: str) -> dict:
    records = db.query(WaterUsage).filter(WaterUsage.user_id == user.id).order_by(WaterUsage.date.desc()).limit(14).all()
    anomalies = db.query(Anomaly).filter(Anomaly.user_id == user.id).order_by(Anomaly.date.desc()).limit(5).all()
    predictions = predict_next_7_days(list(reversed(records)))
    latest = records[0] if records else None
    context = {
        "recent_usage": [{"date": r.date.isoformat(), "usage": r.usage_liters, "season": r.season, "temperature": r.temperature, "rainfall": r.rainfall} for r in records],
        "anomalies": [{"date": a.date.isoformat(), "type": a.anomaly_type, "severity": a.severity_score} for a in anomalies],
        "predictions": predictions,
    }
    fallback = "I do not have enough usage data yet. Log a few days and I can explain trends, forecasts, and anomalies."
    if latest:
        tips = water_saving_tips(latest.usage_liters, latest.season, bool(anomalies))
        fallback = f"Your latest reading was {latest.usage_liters:.0f}L in {latest.season}. " + " ".join(tips)

    settings = get_settings()
    if not settings.openai_api_key:
        return {"answer": fallback, "context": context}

    client = OpenAI(api_key=settings.openai_api_key)
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are AquaBot, a concise water conservation analyst. Use only the provided user context."},
            {"role": "user", "content": f"Context: {context}\nQuestion: {message}"},
        ],
        temperature=0.2,
    )
    return {"answer": response.choices[0].message.content, "context": context}
