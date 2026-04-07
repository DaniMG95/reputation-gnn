from brain.trainers.interface import ModelTrainInterface
from torch_geometric.loader import NeighborLoader
from common.graph_builder import GraphBuilder
import torch
from tqdm import tqdm


class Sampling(ModelTrainInterface):

    def train(self, train_data: NeighborLoader, validation_data: NeighborLoader = None):

        pbar = tqdm(range(self.epochs), desc="Training Model")
        acc = None
        for epoch in range(self.epochs):
            total_loss = 0
            for batch in train_data:
                loss = self.train_epoch(data=batch)
                total_loss += loss.item()
            avg_loss = total_loss / len(train_data)

            if validation_data is not None and epoch % 20 == 0:
                acc = self.eval_predict_sampling(loader=validation_data)
            pbar.update(1)
            pbar.set_postfix({'loss': f'{avg_loss:.4f}', 'acc_val': f'{acc:.4f}' if acc is not None else 'N/A'})

    @torch.no_grad()
    def eval_predict_sampling(self, loader: NeighborLoader) -> float:
        self.model.eval()
        total_correct = 0

        for batch in loader:
            prediction = self.model(batch)
            mask = GraphBuilder.get_mask(data=batch)
            target = batch.y[mask]
            out = prediction[mask]

            total_correct += self.calculate_accuracy(out=out, labels=target)

        return total_correct / len(loader)