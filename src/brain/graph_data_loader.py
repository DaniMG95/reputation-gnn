from common.db.interfaces import RepositoryPeopleInterface
from torch_geometric.data import Data
from common.GraphBuilder import GraphBuilder


class GraphDataLoader:

    def __init__(self, repository_people: RepositoryPeopleInterface):
        self.repository_people = repository_people
        self.graph = None

    def create_graph(self, p_validation: float = None) -> Data:
        persons = self.repository_people.get_all_persons()
        graph = GraphBuilder.create_graph(persons=persons, p_validation=p_validation)
        return graph

    def create_subgraph_by_persons(self, names: list[str], hops: int = 1, mask_predict: bool = False) -> Data:
        persons = self.repository_people.get_neighborhoods(names=names, hops=hops)
        if mask_predict:
            graph = GraphBuilder.create_graph(persons=persons, predict_persons=names)
        else:
            graph = GraphBuilder.create_graph(persons=persons)
        return graph





