from brain.trainers.interface import ModelTrainInterface
from torch_geometric.loader import NeighborLoader
import torch
from tqdm import tqdm


class Sampling(ModelTrainInterface):

    def train(self, train_data: NeighborLoader, validation_data: NeighborLoader = None):

        pbar = tqdm(range(self.epochs), desc="Training Model")
        val_loss = None
        for epoch in range(self.epochs):
            total_loss = 0
            for batch in train_data:
                loss = self.train_epoch(data=batch)
                total_loss += loss.item()
            avg_loss = total_loss / len(train_data)

            if validation_data is not None and epoch % 20 == 0:
                val_loss = self.val_loss_sampling(loader=validation_data)
                self.early_stopping(val_loss=val_loss, model=self.model)
                if self.early_stopping.early_stop:
                    self.early_stopping.restore_best_weights(self.model)
                    break
            pbar.update(1)
            pbar.set_postfix({'loss': f'{avg_loss:.4f}', 'acc_val': f'{val_loss:.4f}' if val_loss is not None else 'N/A'})


    @torch.no_grad()
    def val_loss_sampling(self, loader: NeighborLoader) -> float:
        total_loss = 0

        for batch in loader:
            total_loss += self.calculate_val_loss(data=batch)

        return total_loss / len(loader)