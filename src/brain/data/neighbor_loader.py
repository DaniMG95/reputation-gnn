from torch_geometric.data import Data
from torch_geometric.loader import NeighborLoader
from common.graph_builder import GraphBuilder


class NeighborDataLoader:
    def __init__(self, num_neighbors: list, batch_size: int = 32):
        self.batch_size = batch_size
        self.num_neighbors = num_neighbors

    def get_neighbor_batch(self, data: Data) -> NeighborLoader:
        mask = GraphBuilder.get_mask(data=data)
        return NeighborLoader(
            data,
            num_neighbors=self.num_neighbors,
            batch_size=self.batch_size,
            input_nodes=mask,
            shuffle=True
        )
