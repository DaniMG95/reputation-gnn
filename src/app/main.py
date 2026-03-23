from fastapi import FastAPI
from app.api import api_router
from common.db.connection import init_db_connection
from contextlib import asynccontextmanager
from app.api.depends import get_person_service, connector_redis, repository_people_neo4j
from brain.model_predictor import ModelPredictor
from brain.models.model_factory import ModelFactory
from app.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db_connection()
    redis_connector = connector_redis()
    repository_people = repository_people_neo4j()
    app.state.redis = redis_connector
    app.state.repository_people_redis = repository_people
    app.state.person_service = get_person_service(con_redis=redis_connector, repository_people=repository_people)
    model = ModelFactory.create_model(model_name=settings.model_name, hidden_channels=settings.hidden_channels,
                                      in_channels=settings.num_features, out_channels=settings.out_channels)
    app.state.model = ModelPredictor(model=model, model_path=settings.model_path)
    yield
    redis_connector.close()


app = FastAPI(lifespan=lifespan)
app.include_router(api_router)



if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)



