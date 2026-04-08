from fastapi import APIRouter, Request
from app.schemas.person import PersonPredict, PredictRequestPerson, PersonSchema
from app.service.person_service import PersonService
from common.logger import Logger

api_router = APIRouter(prefix="/predict", tags=["predict"])
logger = Logger("PredictAPI")

@api_router.post("", response_model=PersonPredict)
async def predict_person(request: Request, request_predict: PredictRequestPerson):
    logger.info(f"Received predict request for person: {request_predict.name}")
    person_service: PersonService = request.app.state.person_service
    person = PersonSchema(name=request_predict.name, user_type=request_predict.user_type, posts=request_predict.posts,
                          n_followers=request_predict.n_followers, n_following=request_predict.n_following,
                          verified=request_predict.verified, followers=request_predict.followers,
                          following=request_predict.following)
    predict = person_service.predict_type_person(person=person, followers_db=request_predict.followers_db,
                                                 following_db=request_predict.following_db)
    logger.info(f"Predict result for person '{request_predict.name}': {predict.user_type}")
    return predict
