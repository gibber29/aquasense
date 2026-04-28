from datetime import date, datetime
from sqlalchemy import Boolean, Date, DateTime, Float, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(120))
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    role: Mapped[str] = mapped_column(String(20), default="user")
    city: Mapped[str] = mapped_column(String(120), default="Delhi")

    usages: Mapped[list["WaterUsage"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    anomalies: Mapped[list["Anomaly"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    alerts: Mapped[list["Alert"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    gamification: Mapped["Gamification"] = relationship(back_populates="user", cascade="all, delete-orphan", uselist=False)


class WaterUsage(Base):
    __tablename__ = "water_usage"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    date: Mapped[date] = mapped_column(Date, index=True)
    usage_liters: Mapped[float] = mapped_column(Float)
    season: Mapped[str] = mapped_column(String(40), default="unknown")
    time_of_day: Mapped[str] = mapped_column(String(40), default="morning")
    temperature: Mapped[float] = mapped_column(Float, default=0)
    rainfall: Mapped[float] = mapped_column(Float, default=0)

    user: Mapped[User] = relationship(back_populates="usages")


class Anomaly(Base):
    __tablename__ = "anomalies"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    date: Mapped[date] = mapped_column(Date, index=True)
    usage: Mapped[float] = mapped_column(Float)
    anomaly_type: Mapped[str] = mapped_column(String(50))
    severity_score: Mapped[float] = mapped_column(Float)

    user: Mapped[User] = relationship(back_populates="anomalies")


class Alert(Base):
    __tablename__ = "alerts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    message: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    resolved: Mapped[bool] = mapped_column(Boolean, default=False)

    user: Mapped[User] = relationship(back_populates="alerts")


class Gamification(Base):
    __tablename__ = "gamification"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), unique=True, index=True)
    streak_count: Mapped[int] = mapped_column(Integer, default=0)
    conservation_score: Mapped[float] = mapped_column(Float, default=0)
    badges: Mapped[str] = mapped_column(Text, default="")

    user: Mapped[User] = relationship(back_populates="gamification")
