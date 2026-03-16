from brain.models.interfaces import ModelBotDetectorInterface
from torch_geometric.data import Data
import torch.nn.functional as F
import torch
from tqdm import tqdm


class ModelTrainer:

    def __init__(self, data: Data, model: ModelBotDetectorInterface, epochs: int = 200,
                 lr: float = 0.01):
        self.data = data
        self.model = model
        self.epochs = epochs
        self.lr = lr
        self.optimizer = torch.optim.Adam(self.model.parameters(), lr=self.lr, weight_decay=5e-4)

    def train(self):
        self.model.train()
        pbar = tqdm(range(self.epochs), desc="Training Model")

        for epoch in range(self.epochs):
            self.optimizer.zero_grad()

            prediction = self.model(self.data)

            if hasattr(self.data, 'train_mask'):
                out = prediction[self.data.train_mask]
                target = self.data.y[self.data.train_mask]
            else:
                target = self.data.y
                out = prediction

            weights = torch.tensor([1.0, 2.5])
            loss = F.nll_loss(out, target, weight=weights)

            loss.backward()
            self.optimizer.step()

            if epoch % 20 == 0:
                if hasattr(self.data, 'validation_mask'):
                    out = prediction[self.data.validation_mask]
                    target = self.data.y[self.data.validation_mask]
                else:
                    target = self.data.y
                    out = prediction
                acc = self.calculate_accuracy(out, target)
                pbar.update(1)
                pbar.set_postfix({'loss': f'{loss:.4f}', 'acc': f'{acc:.4f}'})

    def calculate_accuracy(self, out, labels):
        pred = out.argmax(dim=1)
        correct = (pred == labels).sum()
        return int(correct) / int(self.data.num_nodes)

    def save_model(self, path: str):
        torch.save(self.model.state_dict(), path)