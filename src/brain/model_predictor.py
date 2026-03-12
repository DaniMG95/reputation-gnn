import torch
from brain.models.interfaces import ModelBotDetectorInterface
from common.schemas.person import TypePerson
from torch_geometric.data import Data

class ModelPredictor:
    def __init__(self, model: ModelBotDetectorInterface, model_path: str):
        self.model = model
        self.model.load_state_dict(torch.load(model_path))
        self.model.eval()

    def predict(self, new_data: Data) -> list[tuple[TypePerson, float]]:
        with torch.no_grad():
            logits = self.model(new_data)
            probs = torch.exp(logits)
            target_logits = logits[new_data.predict_mask]
            target_probs = probs[new_data.predict_mask]

            predictions = target_logits.argmax(dim=1)

            results = []
            for i in range(len(predictions)):
                pred_idx = predictions[i].item()
                confidence = target_probs[i][pred_idx].item()
                label = TypePerson.BOT if pred_idx == 0 else TypePerson.PERSON
                results.append((label, confidence))

            return results