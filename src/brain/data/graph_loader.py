from core.persistence.interfaces.repository_interfaces import RepositoryPeopleInterface
from torch_geometric.data import Data
from core.graph.builders.graph_builder import GraphBuilder
import random
from core.observability.logger import Logger
from brain.trainers.factory import TypeModelTrainer
from brain.data.neighbor_loader import NeighborDataLoader
from torch_geometric.loader import NeighborLoader
from brain.config import settings


class GraphDataLoader:


    def __init__(self, repository_people: RepositoryPeopleInterface):
        self.repository_people = repository_people
        self.logger = Logger(name="brain.main_train")

    def create_graph(self) -> tuple[Data, list[str]]:
        persons = self.repository_people.get_all_persons()
        graph, names = GraphBuilder.create_graph(persons=persons)
        return graph, names

    def create_subgraph_by_persons(self, names: list[str], mask_predict: bool = False, normalise: bool = False
                                   ) -> tuple[Data, list[str]]:
        persons = self.repository_people.get_neighborhoods(names=names)
        if mask_predict:
            graph, names = GraphBuilder.create_graph(persons=persons, mask_persons=names, normalise=normalise)
        else:
            graph, names = GraphBuilder.create_graph(persons=persons, normalise=normalise)
        return graph, names

    def split_graph_train_val_test(self, ratio_validation: float = 0.2, ratio_test: float = 0.1) -> tuple[Data, Data, Data]:
        persons = self.repository_people.get_all_labeled_names()

        random.shuffle(persons)
        training_index = int(len(persons) * (1 - (ratio_validation + ratio_test)))
        test_index = int(len(persons) * (1 - ratio_test))
        training_persons = persons[:training_index]
        validation_persons = persons[training_index:test_index]
        test_persons = persons[test_index:]

        self.logger.info(f"Total persons: {len(persons)}")
        self.logger.info(f"Training persons: {len(training_persons)}")
        self.logger.info(f"Validation persons: {len(validation_persons)}")
        self.logger.info(f"Test persons: {len(test_persons)}")

        graph_training, _ = self.create_subgraph_by_persons(names=training_persons, normalise=True)
        graph_validation, _ = self.create_subgraph_by_persons(names=validation_persons, normalise=True)
        graph_test, _ = self.create_subgraph_by_persons(names=test_persons, normalise=True)

        return graph_training, graph_validation, graph_test

    @staticmethod
    def prepare_data_for_strategy(data: Data, strategy: TypeModelTrainer) -> Data | NeighborLoader:
        if strategy == TypeModelTrainer.FULL:
            return data
        elif strategy == TypeModelTrainer.SAMPLING:
            neighbor_loader = NeighborDataLoader(num_neighbors=settings.num_neighbors, batch_size=settings.batch_size)
            return neighbor_loader.get_neighbor_batch(data=data)
        else:
            raise ValueError(f"Unknown strategy: {strategy}")


