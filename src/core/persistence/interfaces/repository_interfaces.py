from abc import ABC, abstractmethod
from core.domain.entities.person import PersonWithRelations
from core.domain.enums.type_person import TypePerson


class RepositoryPeopleInterface(ABC):

    @property
    @abstractmethod
    def name(self) -> str:
        pass

    @abstractmethod
    def delete_all(self):
        pass

    @abstractmethod
    def create_person(self, person: PersonWithRelations):
        pass

    @abstractmethod
    def create_relationships(self, person: PersonWithRelations, followers: list[str] = None,
                             following: list[str] = None):
        pass

    @abstractmethod
    def update_relationships(self, person: PersonWithRelations, followers: list[str] = None,
                             following: list[str] = None):
        pass

    @abstractmethod
    def get_person(self, name: str) -> PersonWithRelations:
        pass

    @abstractmethod
    def get_persons_by_type(self, user_type: TypePerson) -> list[PersonWithRelations]:
        pass

    @abstractmethod
    def get_all_persons(self) -> list[PersonWithRelations]:
        pass

    @abstractmethod
    def update_person(self, person: PersonWithRelations):
        pass

    @abstractmethod
    def delete_person(self, name: str):
        pass

    @abstractmethod
    def get_persons_by_names(self, names: list[str]) -> list[PersonWithRelations]:
        pass

    @abstractmethod
    def get_neighborhoods(self, names: list[str], limit: int = 50) -> list[PersonWithRelations]:
        pass

    @abstractmethod
    def get_random_nodes(self, n: int) -> list[PersonWithRelations]:
        pass

    @abstractmethod
    def ping(self) -> bool:
        pass

    @abstractmethod
    def get_persons_by_pagination(self, skip: int = 0, limit: int = 10, type_person: TypePerson = None
                                  ) -> list[PersonWithRelations]:
        pass

    @abstractmethod
    def count_persons(self) -> int:
        pass

    @abstractmethod
    def get_all_labeled_names(self) -> list[str]:
        pass