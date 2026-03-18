from app.domain.repository_interfaces import PersonRepositoryCacheInterface
from app.connectors.redis_conector import RedisConnector
from common.schemas.person import PersonSchema, PersonPredict
from pydantic import TypeAdapter


class PersonRepositoryRedis(PersonRepositoryCacheInterface):
    PREFIX = "person:"
    PREFIX_PREDICTION = "prediction:"

    def __init__(self, redis_client: RedisConnector):
        self.redis_client = redis_client

    def get_person(self, person_name: str) -> PersonSchema | None:
        person_data = self.redis_client.get(f"{self.PREFIX}{person_name}")
        if person_data:
            return PersonSchema(**person_data)
        return None

    def save_person(self, person: PersonSchema, expired_time: int = 3600):
        adapter = TypeAdapter(PersonSchema)
        person_data = adapter.dump_json(person)
        key = f"{self.PREFIX}{person.name}"
        self.redis_client.set(key=key, value=person_data)
        self.redis_client.expire(key=key, time=expired_time)

    def delete_person(self, person_name: str):
        self.redis_client.delete(f"{self.PREFIX}{person_name}")

    def get_prediction(self, hash_person: str) -> PersonPredict | None:
        prediction_data = self.redis_client.get(f"{self.PREFIX_PREDICTION}{hash_person}")
        if prediction_data:
            return PersonPredict(**prediction_data)
        return None

    def save_prediction(self, person_predict: PersonPredict, hash_person: str, expired_time: int = 3600):
        adapter = TypeAdapter(PersonPredict)
        prediction_data = adapter.dump_json(person_predict)
        key = f"{self.PREFIX_PREDICTION}{hash_person}"
        self.redis_client.set(key=key, value=prediction_data)
        self.redis_client.expire(key=key, time=expired_time)