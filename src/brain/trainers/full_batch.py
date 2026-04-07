from brain.trainers.interface import ModelTrainInterface
from torch_geometric.data import Data
from tqdm import tqdm


class FullBatch(ModelTrainInterface):

    def train(self, train_data: Data, validation_data: Data = None):

        pbar = tqdm(range(self.epochs), desc="Training Model")
        val_loss = None
        for epoch in range(self.epochs):
            loss = self.train_epoch(data=train_data)

            if validation_data is not None and epoch % 20 == 0:
                val_loss = self.calculate_val_loss(data=validation_data)
                self.early_stopping(val_loss=val_loss, model=self.model)
                if self.early_stopping.early_stop:
                    self.early_stopping.restore_best_weights(self.model)
                    break
            pbar.update(1)
            pbar.set_postfix({'loss': f'{loss:.4f}', 'loss_val': f'{val_loss:.4f}' if loss is not None else 'N/A'})


