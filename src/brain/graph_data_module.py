from torch_geometric.data import Data
from torch_geometric.loader import NeighborLoader
import torch


class GraphDataModule:
    def __init__(self, data: Data, num_neighbors: list, batch_size: int = 32):
        self.data = data
        self.batch_size = batch_size
        self.num_neighbors = num_neighbors

    def get_neighbor_batch(self) -> NeighborLoader:
        return NeighborLoader(
            self.data,
            num_neighbors=self.num_neighbors,
            batch_size=self.batch_size,
            input_nodes=self.data.train_mask,
            shuffle=True
        )

    def split_index_data(self, ratio_validation: float = 0.2, ratio_test: float = 0.1
                   ) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
        num_nodes = self.data.num_nodes
        indices = torch.randperm(num_nodes)
        split_idx = int(num_nodes * (1 - (ratio_validation + ratio_test)))
        split_test = int(num_nodes * (1 - ratio_test))
        train_indices = indices[:split_idx]
        val_indices = indices[split_idx:split_test]
        test_indices = indices[split_test:]

        return train_indices, val_indices, test_indices