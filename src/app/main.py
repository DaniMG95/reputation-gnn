from fastapi import FastAPI
from app.api import api_router
from common.db.connection import init_db_connection
from contextlib import asynccontextmanager
from app.api.depends import get_person_service, connector_redis, repository_people_neo4j


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db_connection()
    redis_connector = connector_redis()
    repository_people = repository_people_neo4j()
    app.state.redis = redis_connector
    app.state.repository_people_redis = repository_people
    app.state.person_service = get_person_service(con_redis=redis_connector, repository_people=repository_people)
    yield
    redis_connector.close()


app = FastAPI(lifespan=lifespan)
app.include_router(api_router)



if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)



