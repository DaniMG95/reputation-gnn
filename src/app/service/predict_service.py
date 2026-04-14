from core.ml.inference.predictor import ModelPredictor
from app.domain.service_interfaces import PredictServiceInterface
from core.graph.builders.graph_builder import GraphBuilder
import json
import hashlib
from core.domain.entities.person import PersonWithRelations, Person
from core.domain.entities.prediction import PersonPredict
from app.mappers.person_mapper import PersonMapper
from core.graph.features.person_feature_extractor import PersonFeatureExtractor
from app.domain.repository_interfaces import PersonRepositoryCacheInterface
from core.persistence.interfaces.repository_interfaces import RepositoryPeopleInterface
from core.observability.logger import Logger
from app.api.exceptions.custom_exceptions import InvalidModelError


class PredictService(PredictServiceInterface):
    def __init__(self, model: ModelPredictor, person_repository_cache: PersonRepositoryCacheInterface,
                 person_repository_db: RepositoryPeopleInterface):
        self.model = model
        self.person_repository_cache = person_repository_cache
        self.person_repository_db = person_repository_db
        self.logger = Logger(self.__class__.__name__)

    @staticmethod
    def __generate_hash_person(person: PersonWithRelations) -> str:
        attributes = PersonFeatureExtractor.extract(person=person)
        relevant_data = {
            "attr": attributes,
            "following": sorted([(p.name, PersonFeatureExtractor.extract(person=p)) for p in person.following]),
            "followers": sorted([(p.name, PersonFeatureExtractor.extract(person=p)) for p in person.followers])
        }
        data_string = json.dumps(relevant_data, sort_keys=True)
        return hashlib.sha256(data_string.encode()).hexdigest()

    def predict_type_person(self, person: PersonWithRelations, followers_db: list[str],
                            following_db: list[str]) -> PersonPredict:
        if not self.model.is_model_available():
            self.logger.error("Model is not available for prediction.")
            raise InvalidModelError("Model is not available for prediction.")
        self.logger.debug(f"Predicting type of person with name: {person.name}")
        followers = []
        following = []
        if followers_db:
            followers = self.person_repository_db.get_neighborhoods(names=followers_db, limit=2)
            person.followers += [PersonMapper.schema_to_domain(person_schema=follower) for follower in followers]
        if following_db:
            following = self.person_repository_db.get_neighborhoods(names=following_db, limit=2)
            person.following += [PersonMapper.schema_to_domain(person_schema=follow) for follow in following]
        hash_person = self.__generate_hash_person(person=person)
        person_predict = self.person_repository_cache.get_prediction(hash_person=hash_person)
        if person_predict:
            return person_predict
        graph, names = GraphBuilder.create_graph(persons=[person] + followers + following, mask_persons=[person.name])
        prediction = self.model.predict(data=graph, names=names)[0]
        self.person_repository_cache.save_prediction(person_predict=prediction, hash_person=hash_person,
                                                     expired_time=3600)
        return prediction

    def change_model_path(self, model_path: str):
        self.logger.debug(f"Changing model to {model_path}")
        model = ModelPredictor.from_artifact_dir(artifact_dir=model_path)
        if not model.is_model_available():
            self.logger.error(f"Failed to load model from {model_path}")
            raise InvalidModelError(f"Failed to load model from {model_path}")
        self.model = model
        self.logger.info(f"Model changed successfully to {model_path}")
