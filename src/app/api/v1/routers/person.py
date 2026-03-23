from fastapi import APIRouter, Request, HTTPException
from app.schemas.person import PersonResponse, PaginationPersonResponse
from app.service.person_service import PersonService

api_router = APIRouter(prefix="/person", tags=["person"])


@api_router.get("/", response_model=PaginationPersonResponse)
def list_people(request: Request, offset: int = 0, limit: int = 20):
    person_service: PersonService = request.app.state.person_service
    try:
        people = person_service.list_people(offset=offset, limit=limit)
        people_response = [PersonResponse.from_person_schema(person=person) for person in people]
        total = person_service.count_people()
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return PaginationPersonResponse(total=total, offset=offset, limit=limit, people=people_response)


@api_router.get("/{name}", response_model=PersonResponse)
async def get_person(name: str, request: Request):
    person_service: PersonService = request.app.state.person_service
    try:
        person = person_service.get_person(person_name=name)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    return person


@api_router.delete("/{name}")
async def delete_person(name: str, request: Request):
    person_service: PersonService = request.app.state.person_service
    try:
        person_service.delete_person(person_name=name)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    return {"detail": f"Person '{name}' deleted successfully"}


