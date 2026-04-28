from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import router
from app.core.config import get_settings
from app.core.database import Base, engine
from app.models import entities  # noqa: F401
from app.worker import start_background_worker


settings = get_settings()
app = FastAPI(title="Smart Water Monitoring & Conservation Platform", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(router)


@app.on_event("startup")
def startup() -> None:
    Base.metadata.create_all(bind=engine)
    start_background_worker()


@app.get("/")
def root():
    return {"name": "AquaSense", "docs": "/docs"}
