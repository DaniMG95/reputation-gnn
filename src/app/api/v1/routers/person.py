from fastapi import APIRouter, Request, HTTPException
from app.schemas.person import PersonResponse
from app.service.person_service import PersonService

api_router = APIRouter(prefix="/person", tags=["person"])


@api_router.get("/{name}", response_model=PersonResponse)
async def get_person(name: str, request: Request):
    person_service: PersonService = request.app.state.person_service
    try:
        person = person_service.get_person(person_name=name)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    return person
