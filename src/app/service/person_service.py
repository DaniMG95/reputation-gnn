from app.domain.service_interfaces import PersonServiceInterface
from app.domain.repository_interfaces import PersonRepositoryCacheInterface
from common.db.interfaces import RepositoryPeopleInterface
from common.schemas.person import PersonSchema, PersonPredict, TypePerson, PersonBase
from common.graph_builder import GraphBuilder
from brain.models.model_factory import ModelFactory
from brain.model_predictor import ModelPredictor
import json
import hashlib
from app.config import settings


class PersonService(PersonServiceInterface):
    def __init__(self, person_repository_cache: PersonRepositoryCacheInterface,
                 person_repository_db: RepositoryPeopleInterface):
        self.person_repository_cache = person_repository_cache
        self.person_repository_db = person_repository_db

    def get_person(self, person_name: str):
        person = self.person_repository_cache.get_person(person_name=person_name)
        if not person:
            person = self.person_repository_db.get_person(name=person_name)
            if person:
                self.person_repository_cache.save_person(person=person, expired_time=3600)
            else:
                return None
        return person

    def save_person(self, person: PersonSchema, followers_db: list[str] = None, following_db: list[str] = None):
        person_db = self.get_person(person_name=person.name)
        if person_db:
            raise ValueError(f"Person with name '{person.name}' already exists.")
        self.person_repository_db.create_person(person)
        self.person_repository_db.create_relationships(person=person, followers=followers_db,
                                                       following=following_db)

    def delete_person(self, person_name: str):
        person = self.get_person(person_name=person_name)
        if not person:
            raise ValueError(f"Person with name '{person_name}' not found.")
        self.person_repository_db.delete_person(name=person_name)
        self.person_repository_cache.delete_person(person_name=person_name)

    def update_person(self, person: PersonSchema, followers_db: list[str] = None, following_db: list[str] = None):
        person_db = self.get_person(person_name=person.name)
        if not person_db:
            raise ValueError(f"Person with name '{person.name}' not found.")
        self.person_repository_db.update_person(person=person)
        self.person_repository_db.update_relationships(person=person, followers=followers_db, following=following_db)
        self.person_repository_cache.delete_person(person_name=person.name)

    def list_people(self, offset: int = 0, limit: int = 20, type_person: TypePerson = None) -> list[PersonSchema]:
        if offset < 0 or limit <= 0:
            raise ValueError("Offset must be non-negative and limit must be positive.")
        if limit > 100:
            raise ValueError("Limit must not exceed 100.")
        return self.person_repository_db.get_persons_by_pagination(skip=offset, limit=limit, type_person=type_person)

    def count_people(self) -> int:
        return self.person_repository_db.count_persons()

    @staticmethod
    def __generate_hash_person(person: PersonSchema) -> str:
        relevant_data = {
            "attr": person.attributes,
            "following": sorted([(p.name, p.attributes) for p in person.following]),
            "followers": sorted([(p.name, p.attributes) for p in person.followers])
        }
        data_string = json.dumps(relevant_data, sort_keys=True)
        return hashlib.sha256(data_string.encode()).hexdigest()

    def predict_type_person(self, person: PersonSchema, followers_db: list[str], following_db: list[str]
                            ) -> PersonPredict:
        followers  = []
        following = []
        if followers_db:
            followers = self.person_repository_db.get_neighborhoods(names=followers_db, limit=2)
            person.followers += [PersonBase.from_schema(person_schema=follower) for follower in followers]
        if following_db:
            following = self.person_repository_db.get_neighborhoods(names=following_db, limit=2)
            person.following += [PersonBase.from_schema(person_schema=follow) for follow in following]
        hash_person = self.__generate_hash_person(person=person)
        person_predict = self.person_repository_cache.get_prediction(hash_person=hash_person)
        if person_predict:
                return person_predict
        graph = GraphBuilder.create_graph(persons=[person] + followers + following,
                                          predict_persons=[person.name])
        bot_model = ModelFactory.create_model(model_name=settings.model_name, in_channels=graph.num_features,
                                              out_channels=settings.out_channels,
                                              hidden_channels = settings.hidden_channels)
        model_preditor = ModelPredictor(model=bot_model, model_path=settings.model_path)
        prediction = model_preditor.predict(new_data=graph, names=[person.name])[0]
        self.person_repository_cache.save_prediction(person_predict=prediction, hash_person=hash_person,
                                                     expired_time=3600)
        return prediction

