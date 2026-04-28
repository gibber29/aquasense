import csv
from io import StringIO
from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy import func
from sqlalchemy.orm import Session
from app.api.deps import admin_user, current_user
from app.core.database import get_db
from app.core.security import create_access_token, hash_password, verify_password
from app.models.entities import Alert, Anomaly, Gamification, User, WaterUsage
from app.schemas.dto import ChatRequest, CostRequest, LoginRequest, UsageCreate, UserCreate
from app.services.chatbot import aquabot_answer
from app.services.gamification import update_gamification
from app.services.ml import detect_and_store_anomalies, predict_next_7_days, train_and_evaluate
from app.services.report import monthly_report
from app.services.usage import filter_usage, log_usage


router = APIRouter()


@router.post("/register")
def register(payload: UserCreate, db: Session = Depends(get_db)):
    if db.query(User).filter(User.email == payload.email).first():
        raise HTTPException(status_code=409, detail="Email already registered")
    user = User(name=payload.name, email=payload.email, password_hash=hash_password(payload.password), city=payload.city)
    db.add(user)
    db.commit()
    db.refresh(user)
    db.add(Gamification(user_id=user.id, badges=""))
    db.commit()
    return {"message": "registered", "user_id": user.id}


@router.post("/login")
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email).first()
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    return {"access_token": create_access_token(user.email, user.role), "token_type": "bearer", "role": user.role, "name": user.name}


@router.post("/log-usage")
def create_usage(payload: UsageCreate, user: User = Depends(current_user), db: Session = Depends(get_db)):
    record = log_usage(db, user, payload)
    detect_and_store_anomalies(db, user.id)
    return {
        "id": record.id,
        "date": record.date,
        "usage_liters": record.usage_liters,
        "season": record.season,
        "time_of_day": record.time_of_day,
        "temperature": record.temperature,
        "rainfall": record.rainfall,
    }


@router.get("/usage-history")
def usage_history(period: str = "month", page: int = 1, size: int = 20, user: User = Depends(current_user), db: Session = Depends(get_db)):
    records = filter_usage(db, user.id, period)
    anomaly_dates = {item.date for item in db.query(Anomaly).filter(Anomaly.user_id == user.id).all()}
    start = max(page - 1, 0) * size
    items = records[start : start + size]
    return {
        "items": [
            {
                "id": record.id,
                "date": record.date.isoformat(),
                "usage_liters": record.usage_liters,
                "season": record.season,
                "time_of_day": record.time_of_day,
                "temperature": record.temperature,
                "rainfall": record.rainfall,
                "is_anomaly": record.date in anomaly_dates,
            }
            for record in items
        ],
        "total": len(records),
        "page": page,
        "size": size,
    }


@router.get("/dashboard")
def dashboard(user: User = Depends(current_user), db: Session = Depends(get_db)):
    records = db.query(WaterUsage).filter(WaterUsage.user_id == user.id).order_by(WaterUsage.date).all()
    anomalies = db.query(Anomaly).filter(Anomaly.user_id == user.id).order_by(Anomaly.date.desc()).all()
    alerts = db.query(Alert).filter(Alert.user_id == user.id, Alert.resolved.is_(False)).order_by(Alert.created_at.desc()).all()
    gamification = update_gamification(db, user)
    today = records[-1].usage_liters if records else 0
    weekly = records[-7:]
    monthly = records[-31:]
    return {
        "summary": {
            "today_usage": round(today, 1),
            "weekly_average": round(sum(r.usage_liters for r in weekly) / len(weekly), 1) if weekly else 0,
            "monthly_total": round(sum(r.usage_liters for r in monthly), 1),
            "active_alerts": len(alerts),
        },
        "weekly": [{"date": r.date.isoformat(), "usage": r.usage_liters, "is_anomaly": any(a.date == r.date for a in anomalies)} for r in weekly],
        "history": [{"date": r.date.isoformat(), "usage": r.usage_liters} for r in records[-60:]],
        "predictions": predict_next_7_days(records),
        "anomalies": [{"date": a.date.isoformat(), "usage": a.usage, "type": a.anomaly_type, "severity": a.severity_score} for a in anomalies[:5]],
        "alerts": [{"id": a.id, "message": a.message, "created_at": a.created_at.isoformat(), "resolved": a.resolved} for a in alerts[:5]],
        "gamification": {"streak_count": gamification.streak_count, "conservation_score": gamification.conservation_score, "badges": [b for b in gamification.badges.split(",") if b]},
    }


@router.post("/train-models")
def train_models(user: User = Depends(current_user), db: Session = Depends(get_db)):
    records = db.query(WaterUsage).filter(WaterUsage.user_id == user.id).order_by(WaterUsage.date).all()
    return train_and_evaluate(records)


@router.get("/model-metrics")
def model_metrics(user: User = Depends(current_user), db: Session = Depends(get_db)):
    records = db.query(WaterUsage).filter(WaterUsage.user_id == user.id).order_by(WaterUsage.date).all()
    return train_and_evaluate(records)


@router.get("/predict-7days")
def predictions(user: User = Depends(current_user), db: Session = Depends(get_db)):
    records = db.query(WaterUsage).filter(WaterUsage.user_id == user.id).order_by(WaterUsage.date).all()
    return predict_next_7_days(records)


@router.get("/anomalies")
def anomalies(user: User = Depends(current_user), db: Session = Depends(get_db)):
    return [
        {"id": item.id, "date": item.date.isoformat(), "usage": item.usage, "anomaly_type": item.anomaly_type, "severity_score": item.severity_score}
        for item in db.query(Anomaly).filter(Anomaly.user_id == user.id).order_by(Anomaly.date.desc()).all()
    ]


@router.get("/alerts")
def alerts(user: User = Depends(current_user), db: Session = Depends(get_db)):
    return [
        {"id": item.id, "message": item.message, "created_at": item.created_at.isoformat(), "resolved": item.resolved}
        for item in db.query(Alert).filter(Alert.user_id == user.id).order_by(Alert.created_at.desc()).all()
    ]


@router.post("/cost-estimator")
def cost_estimator(payload: CostRequest, user: User = Depends(current_user), db: Session = Depends(get_db)):
    records = db.query(WaterUsage).filter(WaterUsage.user_id == user.id).order_by(WaterUsage.date.desc()).limit(30).all()
    average = sum(r.usage_liters for r in records) / len(records) if records else 0
    daily = average * payload.cost_per_liter
    target = daily * 0.85
    return {"daily_cost": round(daily, 2), "monthly_projection": round(daily * 30, 2), "annual_projection": round(daily * 365, 2), "estimated_savings": round((daily - target) * 30, 2)}


@router.get("/report/monthly")
def report(user: User = Depends(current_user), db: Session = Depends(get_db)):
    return Response(monthly_report(db, user), media_type="application/pdf", headers={"Content-Disposition": "attachment; filename=aquasense-report.pdf"})


@router.post("/chatbot")
def chatbot(payload: ChatRequest, user: User = Depends(current_user), db: Session = Depends(get_db)):
    return aquabot_answer(db, user, payload.message)


@router.get("/admin/stats")
def admin_stats(_: User = Depends(admin_user), db: Session = Depends(get_db)):
    top = (
        db.query(User.name, func.sum(WaterUsage.usage_liters).label("total"))
        .join(WaterUsage, WaterUsage.user_id == User.id)
        .group_by(User.id)
        .order_by(func.sum(WaterUsage.usage_liters).desc())
        .limit(5)
        .all()
    )
    return {
        "total_users": db.query(User).count(),
        "total_water_usage": round(db.query(func.coalesce(func.sum(WaterUsage.usage_liters), 0)).scalar(), 1),
        "total_anomalies": db.query(Anomaly).count(),
        "top_consumers": [{"name": name, "total": round(total, 1)} for name, total in top],
        "alerts": [
            {"id": item.id, "message": item.message, "created_at": item.created_at.isoformat(), "resolved": item.resolved}
            for item in db.query(Alert).order_by(Alert.created_at.desc()).limit(50).all()
        ],
    }


@router.get("/admin/export-csv")
def export_csv(_: User = Depends(admin_user), db: Session = Depends(get_db)):
    buffer = StringIO()
    writer = csv.writer(buffer)
    writer.writerow(["user", "email", "city", "date", "usage_liters", "season", "temperature", "rainfall"])
    rows = db.query(User, WaterUsage).join(WaterUsage, WaterUsage.user_id == User.id).order_by(WaterUsage.date.desc()).all()
    for user, record in rows:
        writer.writerow([user.name, user.email, user.city, record.date, record.usage_liters, record.season, record.temperature, record.rainfall])
    return Response(buffer.getvalue(), media_type="text/csv", headers={"Content-Disposition": "attachment; filename=usage-export.csv"})
