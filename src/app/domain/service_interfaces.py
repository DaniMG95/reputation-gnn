from abc import ABC, abstractmethod
from core.domain import PersonWithRelations, TypePerson, PersonPredict

class PersonServiceInterface(ABC):
    @abstractmethod
    def get_person(self, person_name: str) -> PersonWithRelations:
        pass

    @abstractmethod
    def save_person(self, person: PersonWithRelations):
        pass

    @abstractmethod
    def delete_person(self, person_name: str):
        pass

    @abstractmethod
    def update_person(self, person: PersonWithRelations) -> PersonWithRelations:
        pass

    @abstractmethod
    def list_people(self, offset: int = 0, limit: int = 20, type_person: TypePerson = None) -> list[PersonWithRelations]:
        pass


class PredictServiceInterface(ABC):

    @abstractmethod
    def predict_type_person(self, person: PersonWithRelations, followers_db: list[str], following_db: list[str]
                            ) -> PersonPredict:
        pass

