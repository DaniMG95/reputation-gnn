from abc import ABC, abstractmethod
from core.ml.models.interfaces import ModelInterface
import torch
from torch_geometric.data import Data
from core.graph.builders.graph_builder import GraphBuilder
from torch_geometric.loader import NeighborLoader
from brain.trainers.components.early_stopping import EarlyStopping


class ModelTrainInterface(ABC):

    def __init__(self, model: ModelInterface, epochs: int = 200, lr: float = 0.01,
                 weights: list[float] = None, early_stopping: EarlyStopping = None):
        self.model = model
        self.epochs = epochs
        self.lr = lr
        self.optimizer = torch.optim.Adam(self.model.parameters(), lr=self.lr, weight_decay=5e-4)
        weights = torch.tensor([1.0, 2.5]) if weights is None else torch.tensor(weights)
        self.early_stopping = early_stopping
        self.loss_function = torch.nn.NLLLoss(weight=weights)

    @abstractmethod
    def train(self, train_data: Data | NeighborLoader, validation_data: Data | NeighborLoader = None):
        pass

    @staticmethod
    def calculate_accuracy(out, labels):
        pred = out.argmax(dim=1)
        correct = (pred == labels).sum().item()
        return correct / int(labels.size(0))

    def save_model(self, path: str):
        torch.save(self.model.state_dict(), path)

    def train_epoch(self, data: Data):
        self.model.train()
        self.optimizer.zero_grad()
        mask = GraphBuilder.get_mask(data=data)

        prediction = self.model(data)
        target = data.y[mask]
        out = prediction[mask]

        loss = self.loss_function(out, target)
        loss.backward()
        self.optimizer.step()

        return loss

    def calculate_val_loss(self, data: Data):
        self.model.eval()
        mask = GraphBuilder.get_mask(data=data)

        prediction = self.model(data)
        target = data.y[mask]
        out = prediction[mask]

        loss = self.loss_function(out, target)

        return loss.item()
