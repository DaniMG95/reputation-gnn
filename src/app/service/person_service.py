from app.domain.service_interfaces import PersonServiceInterface
from app.domain.repository_interfaces import PersonRepositoryCacheInterface
from common.db.interfaces import RepositoryPeopleInterface
from common.schemas.person import PersonSchema, TypePerson
from app.api.exceptions.custom_exceptions import PersonNotFoundError, PersonAlreadyExistsError, \
    InvalidPaginationParametersError
from common.logger import Logger


class PersonService(PersonServiceInterface):
    def __init__(self, person_repository_cache: PersonRepositoryCacheInterface,
                 person_repository_db: RepositoryPeopleInterface):
        self.person_repository_cache = person_repository_cache
        self.person_repository_db = person_repository_db
        self.logger = Logger(self.__class__.__name__)

    def get_person(self, person_name: str):
        self.logger.debug(f"Retrieving person with name: {person_name}")
        self.logger.debug(f"Attempting to retrieve person '{person_name}' from cache.")
        person = self.person_repository_cache.get_person(person_name=person_name)
        if not person:
            self.logger.debug(f"Person '{person_name}' not found in cache. Retrieving from database.")
            person = self.person_repository_db.get_person(name=person_name)
            if person:
                self.person_repository_cache.save_person(person=person, expired_time=3600)
            else:
                self.logger.debug(f"Person '{person_name}' not found in database.")
                return None
        return person

    def save_person(self, person: PersonSchema, followers_db: list[str] = None, following_db: list[str] = None):
        self.logger.debug(f"Saving person with name: {person.name}")
        person_db = self.get_person(person_name=person.name)
        if person_db:
            self.logger.debug(f"Person with name '{person.name}' already exists. Cannot save duplicate.")
            raise PersonAlreadyExistsError(name=person.name)
        self.person_repository_db.create_person(person)
        self.person_repository_db.create_relationships(person=person, followers=followers_db,
                                                       following=following_db)

    def delete_person(self, person_name: str):
        self.logger.debug(f"Deleting person with name: {person_name}")
        person = self.get_person(person_name=person_name)
        if not person:
            self.logger.debug(f"Person with name '{person_name}' not found. Cannot delete non-existent person.")
            raise PersonNotFoundError(name=person_name)
        self.person_repository_db.delete_person(name=person_name)
        self.person_repository_cache.delete_person(person_name=person_name)

    def update_person(self, person: PersonSchema, followers_db: list[str] = None, following_db: list[str] = None):
        self.logger.debug(f"Updating person with name: {person.name}")
        person_db = self.get_person(person_name=person.name)
        if not person_db:
            self.logger.debug(f"Person with name '{person.name}' not found. Cannot update non-existent person.")
            raise PersonNotFoundError(name=person.name)
        self.person_repository_db.update_person(person=person)
        self.person_repository_db.update_relationships(person=person, followers=followers_db, following=following_db)
        self.person_repository_cache.delete_person(person_name=person.name)

    def list_people(self, offset: int = 0, limit: int = 20, type_person: TypePerson = None) -> list[PersonSchema]:
        self.logger.debug(f"Listing people with offset: {offset}, limit: {limit}, type_person: {type_person}")
        if offset < 0 or limit <= 0:
            self.logger.debug(f"Invalid pagination parameters: offset={offset}, limit={limit}.")
            raise InvalidPaginationParametersError(message="Offset must be non-negative and limit must be positive.")
        if limit > 100:
            self.logger.debug(f"Limit parameter exceeds maximum allowed value: limit={limit}.")
            raise InvalidPaginationParametersError(message="Limit must not exceed 100.")
        return self.person_repository_db.get_persons_by_pagination(skip=offset, limit=limit, type_person=type_person)

    def count_people(self) -> int:
        self.logger.debug("Counting total number of people in the database.")
        return self.person_repository_db.count_persons()


