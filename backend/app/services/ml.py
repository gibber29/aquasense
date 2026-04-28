from datetime import timedelta
import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest, RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeRegressor
from sqlalchemy.orm import Session
from app.models.entities import Anomaly, WaterUsage
from app.services.alerts import create_alert


def _frame(records: list[WaterUsage]) -> pd.DataFrame:
    rows = [
        {
            "id": record.id,
            "date": record.date,
            "usage_liters": record.usage_liters,
            "temperature": record.temperature,
            "rainfall": record.rainfall,
            "day": record.date.toordinal(),
            "weekday": record.date.weekday(),
        }
        for record in records
    ]
    return pd.DataFrame(rows)


def train_and_evaluate(records: list[WaterUsage]) -> list[dict]:
    df = _frame(records)
    if len(df) < 4:
        return [
            {"model": "Linear Regression", "r2_score": 0.0, "rmse": 0.0},
            {"model": "Decision Tree", "r2_score": 0.0, "rmse": 0.0},
            {"model": "Random Forest", "r2_score": 0.0, "rmse": 0.0},
        ]
    features = df[["day", "weekday", "temperature", "rainfall"]]
    target = df["usage_liters"]
    x_train, x_test, y_train, y_test = train_test_split(features, target, test_size=0.3, random_state=42)
    models = {
        "Linear Regression": LinearRegression(),
        "Decision Tree": DecisionTreeRegressor(max_depth=5, random_state=42),
        "Random Forest": RandomForestRegressor(n_estimators=80, random_state=42),
    }
    metrics = []
    for name, model in models.items():
        model.fit(x_train, y_train)
        predicted = model.predict(x_test)
        metrics.append(
            {
                "model": name,
                "r2_score": round(float(r2_score(y_test, predicted)), 3) if len(y_test) > 1 else 0,
                "rmse": round(float(np.sqrt(mean_squared_error(y_test, predicted))), 2),
            }
        )
    return metrics


def predict_next_7_days(records: list[WaterUsage]) -> list[dict]:
    if not records:
        return []
    df = _frame(records)
    last_day = max(record.date for record in records)
    avg_temp = float(df["temperature"].mean() or 28)
    avg_rain = float(df["rainfall"].mean() or 0)
    future_dates = [last_day + timedelta(days=i) for i in range(1, 8)]
    future = pd.DataFrame(
        {
            "day": [day.toordinal() for day in future_dates],
            "weekday": [day.weekday() for day in future_dates],
            "temperature": [avg_temp] * 7,
            "rainfall": [avg_rain] * 7,
        }
    )
    if len(df) < 4:
        prediction = [round(float(df["usage_liters"].mean()), 1)] * 7
    else:
        model = RandomForestRegressor(n_estimators=120, random_state=42)
        model.fit(df[["day", "weekday", "temperature", "rainfall"]], df["usage_liters"])
        prediction = [round(float(value), 1) for value in model.predict(future)]
    return [{"date": day.isoformat(), "predicted_usage": value} for day, value in zip(future_dates, prediction)]


def detect_and_store_anomalies(db: Session, user_id: int) -> list[Anomaly]:
    records = db.query(WaterUsage).filter(WaterUsage.user_id == user_id).order_by(WaterUsage.date).all()
    if len(records) < 3:
        return []
    db.query(Anomaly).filter(Anomaly.user_id == user_id).delete()
    df = _frame(records)
    mean = df["usage_liters"].mean()
    std = df["usage_liters"].std() or 0
    created: list[Anomaly] = []

    for record in records:
        if std and record.usage_liters > mean + 2 * std:
            severity = round(float((record.usage_liters - mean) / std), 2)
            created.append(Anomaly(user_id=user_id, date=record.date, usage=record.usage_liters, anomaly_type="zscore", severity_score=severity))

    if len(records) >= 6:
        features = df[["usage_liters", "temperature", "rainfall"]]
        labels = IsolationForest(contamination=0.15, random_state=42).fit_predict(features)
        for record, label in zip(records, labels):
            if label == -1 and not any(item.date == record.date and item.anomaly_type == "isolation_forest" for item in created):
                severity = round(float(abs(record.usage_liters - mean) / (std or 1)), 2)
                created.append(Anomaly(user_id=user_id, date=record.date, usage=record.usage_liters, anomaly_type="isolation_forest", severity_score=severity))

    for anomaly in created:
        db.add(anomaly)
    db.commit()
    for anomaly in created:
        create_alert(db, user_id, f"{anomaly.anomaly_type} anomaly detected on {anomaly.date.isoformat()} at {anomaly.usage:.0f}L.")
    return created
