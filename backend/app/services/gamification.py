from sqlalchemy.orm import Session
from app.core.config import get_settings
from app.models.entities import Gamification, User, WaterUsage


BADGE_RULES = [(1, "First Log"), (3, "3 Day Streak"), (7, "Week Warrior"), (14, "Eco Champion"), (24, "Saver of the Month")]


def update_gamification(db: Session, user: User) -> Gamification:
    threshold = get_settings().daily_usage_threshold
    records = db.query(WaterUsage).filter(WaterUsage.user_id == user.id).order_by(WaterUsage.date.desc()).all()
    gamification = user.gamification or Gamification(user_id=user.id)
    if not user.gamification:
        db.add(gamification)

    streak = 0
    for record in records:
        if record.usage_liters <= threshold:
            streak += 1
        else:
            break

    under = len([record for record in records if record.usage_liters <= threshold])
    score = round((under / len(records)) * 100, 1) if records else 0
    badges = [name for days, name in BADGE_RULES if streak >= days]
    gamification.streak_count = streak
    gamification.conservation_score = score
    gamification.badges = ",".join(badges)
    db.commit()
    db.refresh(gamification)
    return gamification
