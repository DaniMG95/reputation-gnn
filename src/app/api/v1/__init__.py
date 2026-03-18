from fastapi import APIRouter
from app.api.v1.routers import api_router as v1_api_router

api_router = APIRouter(prefix="/v1", tags=["v1"])
api_router.include_router(v1_api_router)


