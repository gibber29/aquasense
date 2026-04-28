from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from sqlalchemy.orm import Session
from app.models.entities import Anomaly, User, WaterUsage
from app.services.ml import predict_next_7_days


def monthly_report(db: Session, user: User) -> bytes:
    records = db.query(WaterUsage).filter(WaterUsage.user_id == user.id).order_by(WaterUsage.date.desc()).limit(31).all()
    anomalies = db.query(Anomaly).filter(Anomaly.user_id == user.id).order_by(Anomaly.date.desc()).limit(10).all()
    predictions = predict_next_7_days(list(reversed(records)))
    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=letter)
    y = 760
    pdf.setFont("Helvetica-Bold", 18)
    pdf.drawString(72, y, "AquaSense Monthly Water Report")
    y -= 32
    pdf.setFont("Helvetica", 11)
    total = sum(record.usage_liters for record in records)
    average = total / len(records) if records else 0
    lines = [
        f"User: {user.name} ({user.city})",
        f"Monthly usage: {total:.0f} liters",
        f"Daily average: {average:.0f} liters",
        f"Anomalies detected: {len(anomalies)}",
        f"Badges: {user.gamification.badges if user.gamification else 'None'}",
        "",
        "7-day prediction:",
    ]
    lines += [f"{item['date']}: {item['predicted_usage']}L" for item in predictions]
    lines += ["", "Recent anomalies:"]
    lines += [f"{item.date.isoformat()} - {item.anomaly_type} ({item.severity_score})" for item in anomalies] or ["None"]
    for line in lines:
        pdf.drawString(72, y, line)
        y -= 18
        if y < 72:
            pdf.showPage()
            y = 760
    pdf.save()
    return buffer.getvalue()
