from fastapi import APIRouter
from app.api.v1.routers.person import api_router as person_router
from app.api.v1.routers.predict import api_router as predict_router

api_router = APIRouter()
api_router.include_router(person_router)
api_router.include_router(predict_router)