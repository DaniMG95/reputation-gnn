from abc import ABC, abstractmethod
from common.schemas.person import PersonSchema


class RepositoryPeopleInterface(ABC):

    @abstractmethod
    def delete_all(self):
        pass

    @abstractmethod
    def create_person(self, person: PersonSchema):
        pass

    @abstractmethod
    def create_relationships(self, person: PersonSchema, followers: list[PersonSchema] = None,
                             following: list[PersonSchema] = None):
        pass

    @abstractmethod
    def get_person(self, name: str) -> PersonSchema:
        pass

    @abstractmethod
    def get_persons_by_type(self, user_type: str) -> list[PersonSchema]:
        pass

    @abstractmethod
    def get_all_persons(self) -> list[PersonSchema]:
        pass

    @abstractmethod
    def update_person(self, person: PersonSchema):
        pass

    @abstractmethod
    def get_persons_by_names(self, names: list[str]) -> list[PersonSchema]:
        pass