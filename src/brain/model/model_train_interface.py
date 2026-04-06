from abc import ABC, abstractmethod
from brain.models.interfaces import ModelBotDetectorInterface
from brain.model.model_base import ModelBase
import torch
from torch_geometric.data import Data
from common.graph_builder import GraphBuilder


class ModelTrainInterface(ABC, ModelBase):

    def __init__(self, model: ModelBotDetectorInterface, epochs: int = 200, lr: float = 0.01,
                 weights: list[float] = None):
        super().__init__(model=model)
        self.epochs = epochs
        self.lr = lr
        self.optimizer = torch.optim.Adam(self.model.parameters(), lr=self.lr, weight_decay=5e-4)
        self.weights = torch.tensor([1.0, 2.5]) if weights is None else torch.tensor(weights)

    @abstractmethod
    def train(self, train_data: Data, validation_data: Data = None):
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

        loss = torch.nn.functional.nll_loss(out, target, weight=self.weights)
        loss.backward()
        self.optimizer.step()

        return loss
