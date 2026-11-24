from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.health import router as health_router
from app.core.config import Settings

settings = Settings()
app = FastAPI(title="Golf Performance API", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_methods=["GET"],
)
app.include_router(health_router, prefix="/api/v1")
