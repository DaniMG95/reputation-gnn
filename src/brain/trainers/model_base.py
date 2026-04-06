from brain.architectures.interfaces import ModelBotDetectorInterface
import torch
from torch_geometric.data import Data
from common.graph_builder import GraphBuilder


class ModelBase:

    def __init__(self, model: ModelBotDetectorInterface):
        self.model = model

    @staticmethod
    def calculate_accuracy(out, labels):
        pred = out.argmax(dim=1)
        correct = (pred == labels).sum().item()
        return correct / int(labels.size(0))

    @torch.no_grad()
    def eval_predict(self, data: Data) -> float:
        self.model.eval()
        mask = GraphBuilder.get_mask(data=data)

        prediction = self.model(data)
        target = data.y[mask]
        out = prediction[mask]
        acc = self.calculate_accuracy(out=out, labels=target)

        return acc
