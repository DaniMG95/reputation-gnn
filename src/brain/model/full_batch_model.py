from brain.model.model_interface import ModelInterface
from torch_geometric.data import Data
from tqdm import tqdm


class FullBatchModel(ModelInterface):

    def train(self, train_data: Data, validation_data: Data = None):

        pbar = tqdm(range(self.epochs), desc="Training Model")
        acc = None
        for epoch in range(self.epochs):
            loss = self.train_epoch(data=train_data)

            if validation_data is not None and epoch % 20 == 0:
                acc = self.eval_predict(data=validation_data)
            pbar.update(1)
            pbar.set_postfix({'loss': f'{loss:.4f}', 'acc_val': f'{acc:.4f}' if acc is not None else 'N/A'})

