from datetime import date, datetime
from pydantic import BaseModel, EmailStr


class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str
    city: str = "Delhi"


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: str
    name: str


class UsageCreate(BaseModel):
    date: date
    usage_liters: float
    time_of_day: str = "morning"
    temperature: float | None = None
    rainfall: float | None = None


class UsageOut(BaseModel):
    id: int
    date: date
    usage_liters: float
    season: str
    time_of_day: str
    temperature: float
    rainfall: float
    is_anomaly: bool = False

    class Config:
        from_attributes = True


class AnomalyOut(BaseModel):
    id: int
    date: date
    usage: float
    anomaly_type: str
    severity_score: float

    class Config:
        from_attributes = True


class AlertOut(BaseModel):
    id: int
    message: str
    created_at: datetime
    resolved: bool

    class Config:
        from_attributes = True


class CostRequest(BaseModel):
    cost_per_liter: float


class ChatRequest(BaseModel):
    message: str


class ModelMetric(BaseModel):
    model: str
    r2_score: float
    rmse: float
