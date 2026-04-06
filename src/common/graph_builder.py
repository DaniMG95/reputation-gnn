from common.schemas.person import PersonSchema
import torch
from torch_geometric.data import Data
from dataclasses import dataclass


@dataclass
class Node:
    name: str
    idx: int
    attributes: list[float]


class GraphBuilder:

    @staticmethod
    def _create_node_mapping(persons: list[PersonSchema]) -> dict[str, Node]:
        idx = 0
        node_mapping = {}
        for person in persons:
            if person.name not in node_mapping:
                node = Node(name=person.name, idx=idx, attributes=person.attributes)
                node_mapping[person.name] = node
                idx += 1
        return node_mapping


    @classmethod
    def create_graph(cls, persons: list[PersonSchema], mask_persons: list[str] = None, normalise: bool = False) -> Data:
        node_mapping = cls._create_node_mapping(persons=persons)
        type_person_list = []
        edge_sources = []
        edge_targets = []
        mask = torch.zeros(len(node_mapping.keys()), dtype=torch.bool)
        attributes_list = []
        names = []

        for person in persons:
            node: Node = node_mapping[person.name]
            type_person_list.append(person.user_type_int)
            attributes_list.append(node.attributes)
            names.append(node.name)
            if mask_persons is not None and person.name in mask_persons:
                mask[node.idx] = True
            for follow in person.following:
                if follow.name in node_mapping:
                    edge_sources.append(node.idx)
                    edge_targets.append(node_mapping[follow.name].idx)
            for follow in person.followers:
                if follow.name in node_mapping:
                    edge_sources.append(node_mapping[follow.name].idx)
                    edge_targets.append(node.idx)

        x = torch.tensor(attributes_list, dtype=torch.float)
        y = torch.tensor(type_person_list, dtype=torch.long)
        edge_index = torch.tensor([edge_sources, edge_targets], dtype=torch.long)

        if normalise:
            x_min = x.min(dim=0, keepdim=True)[0]
            x_max = x.max(dim=0, keepdim=True)[0]
            x = (x - x_min) / (x_max - x_min + 1e-6)

        data = Data(x=x, edge_index=edge_index, y=y)
        data.names = names

        if mask_persons is not None:
            data.mask = mask

        return data

    @staticmethod
    def get_mask(data: Data) -> torch.Tensor:
        return data.mask if hasattr(data, 'mask') else torch.ones(len(data.y), dtype=torch.bool)

    @staticmethod
    def get_names(data: Data) -> list[str]:
        return data.names if hasattr(data, 'names') else [f'node_{i}' for i in range(len(data.y))]