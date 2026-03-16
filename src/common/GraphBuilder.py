from common.schemas.person import PersonSchema
from common.schemas.person import TypePerson
import torch
from torch_geometric.data import Data

class GraphBuilder:

    @staticmethod
    def _create_node_mapping(persons: list[PersonSchema]) -> dict[str, int]:
        return {person.name: i for i, person in enumerate(persons)}

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

        attributes_list = []
        type_person_list = []
        edge_sources = []
        predict_mask = torch.zeros(len(persons), dtype=torch.bool)
        edge_targets = []

        for person in persons:
            source_idx = node_mapping[person.name]
            attributes_list.append(person.attributes)
            type_person_list.append(0 if person.user_type == TypePerson.BOT else 1)
            if predict_persons is not None and person.name in predict_persons:
                predict_mask[source_idx] = True
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

        data = Data(x=x, edge_index=edge_index, y=y)
        if p_validation is not None:
            cls._add_validation_mask(data=data, p_validation=p_validation)

        if predict_persons is not None:
            data.predict_mask = predict_mask

        return data