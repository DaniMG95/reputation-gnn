from abc import ABC, abstractmethod
from common.schemas.person import PersonSchema, PersonPredict


class PersonRepositoryCacheInterface(ABC):
    @abstractmethod
    def get_person(self, person_name: str) -> PersonSchema:
        pass

    @abstractmethod
    def save_person(self, person: PersonSchema, expired_time: int):
        pass

    @abstractmethod
    def delete_person(self, person_name: str):
        pass

    @abstractmethod
    def get_prediction(self, hash_person: str) -> PersonPredict:
        pass

    @abstractmethod
    def save_prediction(self, hash_person: str, person_predict: PersonPredict, expired_time: int):
        pass
