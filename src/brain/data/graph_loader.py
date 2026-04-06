from common.db.interfaces import RepositoryPeopleInterface
from torch_geometric.data import Data
from common.graph_builder import GraphBuilder
import random
from common.logger import Logger


class GraphDataLoader:


    def __init__(self, repository_people: RepositoryPeopleInterface):
        self.repository_people = repository_people
        self.logger = Logger(name="brain.main_train")

    def create_graph(self) -> Data:
        persons = self.repository_people.get_all_persons()
        graph = GraphBuilder.create_graph(persons=persons)
        return graph

    def create_subgraph_by_persons(self, names: list[str], mask_predict: bool = False, normalise: bool = False
                                   ) -> Data:
        persons = self.repository_people.get_neighborhoods(names=names)
        if mask_predict:
            graph = GraphBuilder.create_graph(persons=persons, mask_persons=names, normalise=normalise)
        else:
            graph = GraphBuilder.create_graph(persons=persons, normalise=normalise)
        return graph

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

        graph_training = self.create_subgraph_by_persons(names=training_persons, normalise=True)
        graph_validation = self.create_subgraph_by_persons(names=validation_persons, normalise=True)
        graph_test = self.create_subgraph_by_persons(names=test_persons, normalise=True)

        return graph_training, graph_validation, graph_test




