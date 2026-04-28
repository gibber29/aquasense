import threading
import time
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models.entities import User, WaterUsage
from app.services.alerts import evaluate_threshold_alert
from app.services.ml import detect_and_store_anomalies


def run_hourly_checks(db: Session) -> None:
    for user in db.query(User).all():
        latest = db.query(WaterUsage).filter(WaterUsage.user_id == user.id).order_by(WaterUsage.date.desc()).first()
        if latest:
            evaluate_threshold_alert(db, latest)
            detect_and_store_anomalies(db, user.id)


def _loop() -> None:
    while True:
        db = SessionLocal()
        try:
            run_hourly_checks(db)
        finally:
            db.close()
        time.sleep(60 * 60)


def start_background_worker() -> None:
    thread = threading.Thread(target=_loop, daemon=True, name="aquasense-hourly-worker")
    thread.start()
