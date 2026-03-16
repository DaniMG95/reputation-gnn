import torch
from brain.models.interfaces import ModelBotDetectorInterface
from common.schemas.person import TypePerson, PersonPredict
from torch_geometric.data import Data

class ModelPredictor:
    def __init__(self, model: ModelBotDetectorInterface, model_path: str):
        self.model = model
        self.model.load_state_dict(torch.load(model_path))
        self.model.eval()

    def predict(self, new_data: Data, names: list[str]) -> list[PersonPredict]:
        with torch.no_grad():
            logits = self.model(new_data)
            probs = torch.exp(logits)
            if hasattr(new_data, 'predict_mask'):
                logits = logits[new_data.predict_mask]
                probs = probs[new_data.predict_mask]

            predictions = logits.argmax(dim=1)

            if len(predictions) != len(names):
                raise ValueError(f"Number of predictions ({len(predictions)}) does not match number of "
                                 f"names ({len(names)})")
            results = []
            for i in range(len(predictions)):
                pred_idx = predictions[i].item()
                confidence = probs[i][pred_idx].item()
                label = TypePerson.BOT if pred_idx == 0 else TypePerson.PERSON
                results.append(PersonPredict(name=names[i], user_type=label, confidence=confidence))

            return results