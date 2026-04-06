from abc import ABC, abstractmethod
from brain.models.interfaces import ModelBotDetectorInterface
import torch
from torch_geometric.data import Data
from common.schemas.person import TypePerson, PersonPredict



class ModelInterface(ABC):

    def __init__(self, model: ModelBotDetectorInterface, epochs: int = 200, lr: float = 0.01,
                 weights: list[float] = None):
        self.model = model
        self.epochs = epochs
        self.lr = lr
        self.optimizer = torch.optim.Adam(self.model.parameters(), lr=self.lr, weight_decay=5e-4)
        self.weights = torch.tensor([1.0, 2.5]) if weights is None else torch.tensor(weights)

    @abstractmethod
    def train(self, train_data: Data, validation_data: Data = None):
        pass

    def load_model(self, path: str):
        self.model.load_state_dict(torch.load(path))

    @staticmethod
    def calculate_accuracy(out, labels):
        pred = out.argmax(dim=1)
        correct = (pred == labels).sum().item()
        return correct / int(labels.size(0))

    def save_model(self, path: str):
        torch.save(self.model.state_dict(), path)

    @staticmethod
    def _get_mask(data: Data) -> torch.Tensor:
        return data.mask if hasattr(data, 'mask') else torch.ones(len(data.y), dtype=torch.bool)

    @staticmethod
    def _get_names(data: Data) -> list[str]:
        return data.names if hasattr(data, 'names') else [f'node_{i}' for i in range(len(data.y))]

    def train_epoch(self, data: Data):
        self.model.train()
        self.optimizer.zero_grad()
        mask = self._get_mask(data=data)

        prediction = self.model(data)
        target = data.y[mask]
        out = prediction[mask]

        loss = torch.nn.functional.nll_loss(out, target, weight=self.weights)
        loss.backward()
        self.optimizer.step()

        return loss

    @torch.no_grad()
    def predict(self, data: Data) -> list[PersonPredict]:
        self.model.eval()
        results = []
        mask = self._get_mask(data=data)
        names = self._get_names(data=data)
        target_names = [name for i, name in enumerate(names) if mask[i]]

        logits = self.model(data)[mask]
        probs = torch.exp(logits)
        predictions = logits.argmax(dim=1)

        for i in range(len(predictions)):
            pred_idx = predictions[i].item()
            confidence = probs[i][pred_idx].item()
            label = TypePerson.transform_to_user_type(user_type_int=pred_idx)
            results.append(PersonPredict(name=target_names[i], user_type=label, confidence=confidence))
        return results



    @torch.no_grad()
    def eval_predict(self, data: Data) -> float:
        self.model.eval()
        mask = self._get_mask(data=data)

        prediction = self.model(data)
        target = data.y[mask]
        out = prediction[mask]
        acc = self.calculate_accuracy(out=out, labels=target)

        return acc

