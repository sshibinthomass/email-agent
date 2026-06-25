from fastapi import APIRouter
from backend.app.api.routes import classify, health

api_router = APIRouter()

api_router.include_router(classify.router, tags=["Classification"])
api_router.include_router(health.router, tags=["System"])
