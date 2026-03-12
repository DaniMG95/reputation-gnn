from common.db.interfaces import RepositoryPeopleInterface
from common.schemas.person import TypePerson
import torch
from torch_geometric.data import Data
from common.schemas.person import PersonSchema


class GraphDataLoader:

    def __init__(self, repository_people: RepositoryPeopleInterface):
        self.repository_people = repository_people

    @staticmethod
    def _create_node_mapping(persons: list[PersonSchema]) -> dict[str, int]:
        return {person.name: i for i, person in enumerate(persons)}

    def _create_graph_by_persons(self, persons: list[PersonSchema]) -> Data:
        node_mapping = self._create_node_mapping(persons=persons)

        attributes_list = []
        type_person_list = []
        edge_sources = []
        edge_targets = []
        for person in persons:
            source_idx = node_mapping[person.name]
            attributes_list.append([person.n_followers, person.n_following, person.posts])
            type_person_list.append(1 if person.user_type == TypePerson.BOT else 0)
            for follow in person.following:
                if follow.name in node_mapping:
                    edge_sources.append(source_idx)
                    edge_targets.append(node_mapping[follow.name])

        x = torch.tensor(attributes_list, dtype=torch.float)
        y = torch.tensor(type_person_list, dtype=torch.long)
        edge_index = torch.tensor([edge_sources, edge_targets], dtype=torch.long)

        return Data(x=x, edge_index=edge_index, y=y)

    def create_graph(self) -> Data:
        persons = self.repository_people.get_all_persons()
        return self._create_graph_by_persons(persons=persons)

    def create_subgraph_by_persons(self, names: list[str], hops: int = 1, predict_mask: bool = True) -> Data:
        persons = self.repository_people.get_neighborhoods(names=names, hops=hops)
        data = self._create_graph_by_persons(persons=persons)
        if predict_mask:
            data.predict_mask = torch.tensor([person.name in names for person in persons])
        return data





