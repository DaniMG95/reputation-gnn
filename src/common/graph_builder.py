from torch_geometric.sampler.neighbor_sampler import node_sample

from common.schemas.person import PersonSchema
from common.schemas.person import TypePerson
import torch
from torch_geometric.data import Data

class GraphBuilder:

    @staticmethod
    def _create_node_mapping(persons: list[PersonSchema]) -> dict[str, int]:
        idx = 0
        node_mapping = {}
        for person in persons:
            persons_mapping = [person] + person.following + person.followers
            for person_mapping in persons_mapping:
                if person_mapping.name not in node_mapping:
                    node_mapping[person_mapping.name] = idx
                    idx += 1
        return node_mapping

    @staticmethod
    def _create_attributes_list(persons: list[PersonSchema]) -> list[list[float]]:
        attributes_list = []
        persons_set = set()
        for person in persons:
            persons_attributes = [person] + person.following + person.followers
            for person_attribute in persons_attributes:
                if person_attribute.name not in persons_set:
                    persons_set.add(person_attribute.name)
                    attributes_list.append(person_attribute.attributes)
        return attributes_list

    @staticmethod
    def _add_validation_mask(data: Data, p_validation: float):
        train_mask = torch.zeros(data.num_nodes, dtype=torch.bool)
        validation_mask = torch.zeros(data.num_nodes, dtype=torch.bool)

        indices = torch.randperm(data.num_nodes)
        train_mask[indices[:int(data.num_nodes * (1-p_validation))]] = True
        validation_mask[indices[int(data.num_nodes * (1-p_validation)):]] = True

        data.train_mask = train_mask
        data.validation_mask = validation_mask

    @classmethod
    def create_graph(cls, persons: list[PersonSchema], p_validation: float = None, predict_persons: list[str] = None
                     ) -> Data:
        node_mapping = cls._create_node_mapping(persons=persons)
        attributes_list = cls._create_attributes_list(persons=persons)
        type_person_list = []
        edge_sources = []
        predict_mask = torch.zeros(len(attributes_list), dtype=torch.bool)
        edge_targets = []

        for person in persons:
            source_idx = node_mapping[person.name]
            type_person_list.append(0 if person.user_type == TypePerson.BOT else 1)
            if predict_persons is not None and person.name in predict_persons:
                predict_mask[source_idx] = True
            for follow in person.following:
                if follow.name in node_mapping:
                    edge_sources.append(source_idx)
                    edge_targets.append(node_mapping[follow.name])
            for follow in person.followers:
                if follow.name in node_mapping:
                    edge_sources.append(node_mapping[follow.name])
                    edge_targets.append(source_idx)


        x = torch.tensor(attributes_list, dtype=torch.float)
        x_min = x.min(dim=0, keepdim=True)[0]
        x_max = x.max(dim=0, keepdim=True)[0]
        x = (x - x_min) / (x_max - x_min + 1e-6)
        y = torch.tensor(type_person_list, dtype=torch.long)
        edge_index = torch.tensor([edge_sources, edge_targets], dtype=torch.long)

        data = Data(x=x, edge_index=edge_index, y=y)
        if p_validation is not None:
            cls._add_validation_mask(data=data, p_validation=p_validation)

        if predict_persons is not None:
            data.predict_mask = predict_mask

        return data