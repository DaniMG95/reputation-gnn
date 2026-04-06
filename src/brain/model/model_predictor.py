from brain.models.interfaces import ModelBotDetectorInterface
from brain.model.model_base import ModelBase
from common.schemas.person import TypePerson, PersonPredict
from torch_geometric.data import Data
from common.graph_builder import GraphBuilder
import torch


class ModelPredictor(ModelBase):

    def __init__(self, model: ModelBotDetectorInterface, model_path: str):
        super().__init__(model=model)
        self.model.load_state_dict(torch.load(model_path, map_location=torch.device('cpu')))
        self.model.eval()

    def load_model(self, path: str):
        self.model.load_state_dict(torch.load(path))


    @torch.no_grad()
    def predict(self, data: Data) -> list[PersonPredict]:
        self.model.eval()
        results = []
        mask = GraphBuilder.get_mask(data=data)
        names = GraphBuilder.get_names(data=data)
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
