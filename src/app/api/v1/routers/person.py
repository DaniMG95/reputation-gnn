from fastapi import APIRouter, Request, HTTPException
from app.schemas.person import PersonResponse, PaginationPersonResponse, CreatePersonRequest, UpdatePersonRequest
from core.domain import PersonWithRelations, TypePerson
from app.service.person_service import PersonService
from core.observability.logger import Logger

api_router = APIRouter(prefix="/person", tags=["person"])
logger = Logger("PersonAPI")


@api_router.post("/", response_model=PersonResponse)
async def create_person(request: Request, person_request: CreatePersonRequest):
    logger.info(f"Received request to create person: {person_request.name}")
    person_service: PersonService = request.app.state.person_service
    person = PersonWithRelations(name=person_request.name, user_type=person_request.user_type, posts=person_request.posts,
                          n_followers=0, n_following=0, verified=person_request.verified)
    person_service.save_person(person=person, followers_db=person_request.followers,
                               following_db=person_request.following)
    person = person_service.get_person(person_name=person_request.name)
    return PersonResponse.from_person_schema(person=person)

@api_router.patch("/{name}", response_model=PersonResponse)
async def update_person(name: str, request: Request, person_request: UpdatePersonRequest):
    logger.info(f"Received request to update person: {name}")
    person_service: PersonService = request.app.state.person_service
    person = PersonWithRelations(name=name, user_type=person_request.user_type, posts=person_request.posts,
                          n_followers=0, n_following=0, verified=person_request.verified)
    try:
        person_service.update_person(person=person, followers_db=person_request.followers,
                                                      following_db=person_request.following)
        person = person_service.get_person(person_name=name)
        if not person:
            raise HTTPException(status_code=404, detail=f"Person with name '{name}' not found.")
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    return PersonResponse.from_person_schema(person=person)


@api_router.get("/", response_model=PaginationPersonResponse)
def list_people(request: Request, offset: int = 0, limit: int = 20, type_person: TypePerson = None):
    logger.info(f"Received request to list people with offset: {offset}, limit: {limit}, type_person: {type_person}")
    person_service: PersonService = request.app.state.person_service
    people = person_service.list_people(offset=offset, limit=limit, type_person=type_person)
    people_response = [PersonResponse.from_person_schema(person=person) for person in people]
    total = person_service.count_people()
    return PaginationPersonResponse(total=total, offset=offset, limit=limit, people=people_response)


@api_router.get("/{name}", response_model=PersonResponse)
async def get_person(name: str, request: Request):
    logger.info(f"Received request to get person with name: {name}")
    person_service: PersonService = request.app.state.person_service
    try:
        person = person_service.get_person(person_name=name)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    if not person:
        raise HTTPException(status_code=404, detail=f"Person with name '{name}' not found.")
    return person


@api_router.delete("/{name}")
async def delete_person(name: str, request: Request):
    logger.info(f"Received request to delete person with name: {name}")
    person_service: PersonService = request.app.state.person_service
    try:
        person_service.delete_person(person_name=name)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    return {"detail": f"Person '{name}' deleted successfully"}


