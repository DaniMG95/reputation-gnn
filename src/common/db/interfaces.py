from abc import ABC, abstractmethod
from common.schemas.person import PersonSchema, TypePerson


class RepositoryPeopleInterface(ABC):

    @property
    @abstractmethod
    def name(self) -> str:
        pass

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
    def update_relationships(self, person: PersonSchema, followers: list[str] = None,
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

    @abstractmethod
    def get_neighborhoods(self, names: list[str], limit: int = 50) -> list[PersonSchema]:
        pass

    @abstractmethod
    def get_random_nodes(self, n: int) -> list[PersonSchema]:
        pass

    @abstractmethod
    def ping(self) -> bool:
        pass

    @abstractmethod
    def get_persons_by_pagination(self, skip: int = 0, limit: int = 10, type_person: TypePerson = None
                                  ) -> list[PersonSchema]:
        pass

    @abstractmethod
    def count_persons(self) -> int:
        pass