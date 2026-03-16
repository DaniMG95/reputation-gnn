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

    @staticmethod
    def _get_attributes_by_person(person: PersonSchema) -> list[float]:
        return [person.n_followers, person.n_following, person.posts, person.verified]

    def _create_graph_by_persons(self, persons: list[PersonSchema], validation: bool) -> Data:
        node_mapping = self._create_node_mapping(persons=persons)

        attributes_list = []
        type_person_list = []
        edge_sources = []
        edge_targets = []
        for person in persons:
            source_idx = node_mapping[person.name]
            attributes_list.append(self._get_attributes_by_person(person=person))
            type_person_list.append(0 if person.user_type == TypePerson.BOT else 1)
            for follow in person.following:
                if follow.name in node_mapping:
                    edge_sources.append(source_idx)
                    edge_targets.append(node_mapping[follow.name])

        x = torch.tensor(attributes_list, dtype=torch.float)
        x_min = x.min(dim=0, keepdim=True)[0]
        x_max = x.max(dim=0, keepdim=True)[0]
        x = (x - x_min) / (x_max - x_min + 1e-6)
        y = torch.tensor(type_person_list, dtype=torch.long)
        edge_index = torch.tensor([edge_sources, edge_targets], dtype=torch.long)

        num_nodes = x.size(0)
        indices = torch.randperm(num_nodes)

        data = Data(x=x, edge_index=edge_index, y=y)

        if validation:
            train_mask = torch.zeros(num_nodes, dtype=torch.bool)
            validation_mask = torch.zeros(num_nodes, dtype=torch.bool)

            train_mask[indices[:int(num_nodes * 0.8)]] = True
            validation_mask[indices[int(num_nodes * 0.8):]] = True

            data.train_mask = train_mask
            data.validation_mask = validation_mask

        return data

    def create_graph(self) -> Data:
        persons = self.repository_people.get_all_persons()
        return self._create_graph_by_persons(persons=persons, validation=True)

    def create_subgraph_by_persons(self, names: list[str], hops: int = 1, predict: bool = True) -> Data:
        persons = self.repository_people.get_neighborhoods(names=names, hops=hops)
        data = self._create_graph_by_persons(persons=persons, validation=False)
        if predict:
            data.predict_mask = torch.tensor([person.name in names for person in persons])
        return data





