from app.config import settings
from app.connectors.redis_conector import RedisConnector
from app.service.person_service import PersonService
from common.db.interfaces import RepositoryPeopleInterface
from neomodel import db
from brain.predictor import ModelPredictor
from app.service.predict_service import PredictService
from app.repository.repository_people_redis import PersonRepositoryRedis

def connector_redis():
    return RedisConnector(host=settings.host_redis, port=settings.port_redis, db=settings.db_redis)

def repository_people_neo4j():
    from common.db.repository_people_neo4j import RepositoryPeopleNeo4j
    return RepositoryPeopleNeo4j(db=db)

def get_person_service(con_redis: RedisConnector, repository_people: RepositoryPeopleInterface) -> PersonService:
    return PersonService(
        person_repository_cache=PersonRepositoryRedis(redis_client=con_redis),
        person_repository_db=repository_people
    )

def get_predict_service(con_redis: RedisConnector, repository_people: RepositoryPeopleInterface,
                       model: ModelPredictor) -> PredictService:
    return PredictService(
        model=model,
        person_repository_cache=PersonRepositoryRedis(redis_client=con_redis),
        person_repository_db=repository_people
    )