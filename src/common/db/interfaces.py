from abc import ABC, abstractmethod
from common.schemas.person import PersonSchema, TypePerson


class RepositoryPeopleInterface(ABC):

    @abstractmethod
    def delete_all(self):
        pass

    @abstractmethod
    def create_person(self, person: PersonSchema):
        pass

    @abstractmethod
    def create_relationships(self, person: PersonSchema, followers: list[str] = None,
                             following: list[str] = None):
        pass

    @abstractmethod
    def get_person(self, name: str) -> PersonSchema:
        pass

    @abstractmethod
    def get_persons_by_type(self, user_type: TypePerson) -> list[PersonSchema]:
        pass

    @abstractmethod
    def get_all_persons(self) -> list[PersonSchema]:
        pass

    @abstractmethod
    def update_person(self, person: PersonSchema):
        pass

    @abstractmethod
    def delete_person(self, name: str):
        pass

    @abstractmethod
    def get_persons_by_names(self, names: list[str]) -> list[PersonSchema]:
        pass

    def get_neighborhoods(self, names: list[str], hops: int = 1) -> list[PersonSchema]:
        pass

    def get_random_nodes(self, n: int) -> list[PersonSchema]:
        pass