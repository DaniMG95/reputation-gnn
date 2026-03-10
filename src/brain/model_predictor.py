import torch
from brain.models.interfaces import ModelBotDetectorInterface
from common.schemas.person import TypePerson
from torch_geometric.data import Data

class ModelPredictor:
    def __init__(self, model: ModelBotDetectorInterface, model_path: str):
        self.model = model
        self.model.load_state_dict(torch.load(model_path))
        self.model.eval()

    def predict(self, new_data: Data) -> tuple[TypePerson, float]:
        with torch.no_grad():
            logits = self.model(new_data)
            probs = torch.exp(logits)
            prediction = logits.argmax(dim=1)
            if prediction.item() == 0:
                return TypePerson.BOT, probs[0][0].item()
            else:
                return TypePerson.PERSON, probs[0][1].item()