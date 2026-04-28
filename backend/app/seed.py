from datetime import date, timedelta
import random
from app.core.database import SessionLocal
from app.core.security import hash_password
from app.models.entities import Gamification, User, WaterUsage
from app.services.gamification import update_gamification
from app.services.ml import detect_and_store_anomalies
from app.services.weather import detect_season


def seed_demo_data() -> None:
    db = SessionLocal()
    try:
        if db.query(User).filter(User.email == "demo@aquasense.local").first():
            return
        user = User(name="Demo User", email="demo@aquasense.local", password_hash=hash_password("password123"), role="user", city="Delhi")
        admin = User(name="Admin", email="admin@aquasense.local", password_hash=hash_password("admin123"), role="admin", city="Delhi")
        db.add_all([user, admin])
        db.commit()
        db.refresh(user)
        db.add(Gamification(user_id=user.id))
        today = date.today()
        for index in range(70):
            day = today - timedelta(days=69 - index)
            temp = 25 + random.random() * 10
            rain = 0 if random.random() > 0.2 else random.random() * 12
            usage = 360 + random.random() * 120 + (85 if temp > 31 else 0)
            if index in (18, 45, 62):
                usage += 260
            db.add(WaterUsage(user_id=user.id, date=day, usage_liters=round(usage, 1), season=detect_season(day, temp, rain), time_of_day="morning", temperature=round(temp, 1), rainfall=round(rain, 1)))
        db.commit()
        update_gamification(db, user)
        detect_and_store_anomalies(db, user.id)
    finally:
        db.close()
