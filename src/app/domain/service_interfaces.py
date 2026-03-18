from abc import ABC, abstractmethod
from common.schemas.person import PersonSchema, TypePerson, PersonPredict

class PersonServiceInterface(ABC):
    @abstractmethod
    def get_person(self, person_name: str) -> PersonSchema:
        pass

    @abstractmethod
    def save_person(self, person: PersonSchema):
        pass

    @abstractmethod
    def delete_person(self, person_name: str):
        pass

    @abstractmethod
    def update_person(self, person: PersonSchema) -> PersonSchema:
        pass

    @abstractmethod
    def list_people(self) -> list[PersonSchema]:
        pass

    @abstractmethod
    def predict_type_person(self, person: PersonSchema, followers_db: list[str], following_db: list[str],
                            hops: int = 0) -> PersonPredict:
        pass

