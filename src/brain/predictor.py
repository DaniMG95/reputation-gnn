from brain.architectures.interfaces import ModelBotDetectorInterface
from brain.trainers.model_base import ModelBase
from common.schemas.person import TypePerson, PersonPredict
from torch_geometric.data import Data
from common.graph_builder import GraphBuilder
import torch
from common.logger import Logger
import os


class ModelPredictor(ModelBase):

    def __init__(self, model: ModelBotDetectorInterface, model_path: str):
        super().__init__(model=model)
        self.logger = Logger("ModelPredictor")
        if os.path.exists(model_path):
            self.model.load_state_dict(torch.load(model_path))
            self.model.eval()
            self.is_available = True
        else:
            self.logger.warning(f"Model file not found at {model_path}. Predictor will not be available.")
            self.is_available = False

    def load_model(self, model: ModelBotDetectorInterface, model_path: str):
        self.logger.debug(f"Loading model from {model_path}")
        self.model = model
        self.reload_model_from_path(model_path=model_path)

    def reload_model_from_path(self, model_path: str):
        self.logger.debug(f"Reloading model from {model_path}")
        if os.path.exists(model_path):
            self.model.load_state_dict(torch.load(model_path))
            self.model.eval()
            self.is_available = True
            self.logger.info(f"Model reloaded successfully from {model_path}")
        else:
            self.logger.warning(f"Model file not found at {model_path}. Predictor will not be available.")
            self.is_available = False


    @torch.no_grad()
    def predict(self, data: Data, names: list[str]) -> list[PersonPredict]:
        self.logger.debug(f"Predicting persons whose names are {names}")
        results = []
        if self.model:
            self.model.eval()
            mask = GraphBuilder.get_mask(data=data)
            target_names = [name for i, name in enumerate(names) if mask[i]]

            logits = self.model(data)[mask]
            probs = torch.exp(logits)
            predictions = logits.argmax(dim=1)

            for i in range(len(predictions)):
                pred_idx = predictions[i].item()
                confidence = probs[i][pred_idx].item()
                label = TypePerson.transform_to_user_type(user_type_int=pred_idx)
                results.append(PersonPredict(name=target_names[i], user_type=label, confidence=confidence))
                self.logger.debug(f"Predicted {target_names[i]} as {label} with confidence {confidence:.4f}")
        return results

    def is_model_available(self) -> bool:
        return self.is_available