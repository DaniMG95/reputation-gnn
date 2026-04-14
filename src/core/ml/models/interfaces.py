from abc import ABC, abstractmethod
from torch_geometric.data import Data
import torch


class ModelInterface(ABC, torch.nn.Module):
    @abstractmethod
    def forward(self, data: Data):
        pass