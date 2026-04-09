from fastapi import APIRouter, Request
from app.schemas.person import PersonPredict, PredictRequestPerson, PersonSchema
from app.service.predict_service import PredictService
from app.schemas.predict import ChangeModelRequest
from common.logger import Logger

api_router = APIRouter(prefix="/predict", tags=["predict"])
logger = Logger("PredictAPI")

@api_router.post("", response_model=PersonPredict)
async def predict_person(request: Request, request_predict: PredictRequestPerson):
    logger.info(f"Received predict request for person: {request_predict.name}")
    predict_service: PredictService = request.app.state.predict_service
    person = PersonSchema(name=request_predict.name, user_type=request_predict.user_type, posts=request_predict.posts,
                          n_followers=request_predict.n_followers, n_following=request_predict.n_following,
                          verified=request_predict.verified, followers=request_predict.followers,
                          following=request_predict.following)
    predict = predict_service.predict_type_person(person=person, followers_db=request_predict.followers_db,
                                                  following_db=request_predict.following_db)
    logger.info(f"Predict result for person '{request_predict.name}': {predict.user_type}")
    return predict

@api_router.post("/change_model")
async def change_model(request: Request, request_change: ChangeModelRequest):
    model_path = request_change.model_path
    logger.info(f"Received request to change model to path: {model_path}")
    predict_service: PredictService = request.app.state.predict_service
    predict_service.change_model_path(model_path=model_path)
    logger.info(f"Model changed successfully to path: {model_path}")
    return {"message": f"Model changed successfully to path: {model_path}"}
