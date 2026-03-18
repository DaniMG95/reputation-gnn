from fastapi import Depends
from app.config import settings
from app.connectors.redis_conector import RedisConnector
from app.service.person_service import PersonService
from neomodel import db

def connector_redis():
    return RedisConnector(host=settings.host_redis, port=settings.port_redis, db=settings.db_redis)

def get_person_service(con_redis: RedisConnector = Depends(connector_redis)) -> PersonService:
    from app.service.person_service import PersonService
    from app.repository.repository_people_redis import PersonRepositoryRedis
    from common.db.repository_people_neo4j import RepositoryPeopleNeo4j
    return PersonService(
        person_repository_cache=PersonRepositoryRedis(redis_client=con_redis),
        person_repository_db=RepositoryPeopleNeo4j(db=db)
    )