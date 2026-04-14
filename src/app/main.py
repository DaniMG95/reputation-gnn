from fastapi import FastAPI
from app.api import api_router
from core.persistence.neo4j.connection import init_db_connection
from contextlib import asynccontextmanager
from app.api.depends import get_person_service, connector_redis, repository_people_neo4j, get_predict_service
from core.ml.inference.predictor import ModelPredictor
from app.config import settings
from app.api.exceptions.custom_exceptions import AppBaseException
from app.api.exceptions.handler import app_exception_handler, global_exception_handler
from core.observability.logger import Logger



def setup_exception_handlers(app: FastAPI):
    app.add_exception_handler(AppBaseException, app_exception_handler)
    app.add_exception_handler(Exception, global_exception_handler)


@asynccontextmanager
async def lifespan(app: FastAPI):
    Logger.setup_logging(app_name=settings.app_logger.app_name)
    logger = Logger(name="api")
    logger.info("Starting API application")
    init_db_connection(url=settings.neo4j.uri_neo4j)
    redis_connector = connector_redis()
    repository_people = repository_people_neo4j()
    app.state.redis = redis_connector
    app.state.repository_people_redis = repository_people
    logger.info(f"Loading model in the path {settings.model_path}")
    app.state.model = ModelPredictor.from_artifact_dir(artifact_dir=settings.model_path)
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



