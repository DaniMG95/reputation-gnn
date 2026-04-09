from fastapi import FastAPI
from app.api import api_router
from common.db.connection import init_db_connection
from contextlib import asynccontextmanager
from app.api.depends import get_person_service, connector_redis, repository_people_neo4j, get_predict_service
from brain.predictor import ModelPredictor
from brain.architectures.factory import ModelFactory
from app.config import settings
from app.api.exceptions.custom_exceptions import AppBaseException
from app.api.exceptions.handler import app_exception_handler, global_exception_handler
from common.logger import Logger



def setup_exception_handlers(app: FastAPI):
    app.add_exception_handler(AppBaseException, app_exception_handler)
    app.add_exception_handler(Exception, global_exception_handler)


@asynccontextmanager
async def lifespan(app: FastAPI):
    Logger.setup_logging()
    logger = Logger(name="api")
    logger.info("Starting API application")
    init_db_connection()
    redis_connector = connector_redis()
    repository_people = repository_people_neo4j()
    app.state.redis = redis_connector
    app.state.repository_people_redis = repository_people
    logger.info(f"Loading model {settings.model_name} in the path {settings.model_path}")
    model = ModelFactory.create_model(model_name=settings.model_name, hidden_channels=settings.hidden_channels,
                                      in_channels=settings.num_features, out_channels=settings.out_channels)
    app.state.model = ModelPredictor(model=model, model_path=settings.model_path)
    app.state.person_service = get_person_service(con_redis=redis_connector, repository_people=repository_people)
    app.state.predict_service = get_predict_service(con_redis=redis_connector, repository_people=repository_people,
                                                    model=app.state.model)
    yield
    logger.info("Shutting down API application")
    redis_connector.close()


app = FastAPI(lifespan=lifespan)
app.include_router(api_router)
setup_exception_handlers(app=app)



if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)



