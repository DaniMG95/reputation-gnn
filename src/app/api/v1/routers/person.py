from fastapi import APIRouter

api_router = APIRouter(prefix="/person", tags=["person"])


@api_router.get("/")
async def read_persons():
    return {"message": "List of persons"}

