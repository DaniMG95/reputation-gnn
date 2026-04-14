from core.ml.models.interfaces import ModelInterface
from core.domain import PersonPredict
from core.ml.encoders.person_label_encoder import PersonLabelEncoder
from torch_geometric.data import Data
from core.graph.builders.graph_builder import GraphBuilder
import torch
from core.observability.logger import Logger
from core.ml.serialization.model_artifact import ModelArtifact, LoadedModelArtifact
from core.ml.models.factory import ModelFactory


class ModelPredictor:
    logger = Logger("ModelPredictor")

    def __init__(self, model: ModelInterface = None, is_available: bool = False):
        self.model = model
        if self.model is not None:
            self.model.eval()
        self.is_available = is_available

    @classmethod
    def from_artifact(cls, artifact: LoadedModelArtifact) -> "ModelPredictor":
        model = ModelFactory.create_from_metadata(artifact.metadata)
        model.load_state_dict(artifact.state_dict)
        model.eval()

        return cls( model=model, is_available=True)

    @classmethod
    def from_artifact_dir(cls, artifact_dir: str) -> "ModelPredictor":
        try:
            artifact = ModelArtifact.load(artifact_dir)
            model = ModelFactory.create_from_metadata(artifact.metadata)
            model.load_state_dict(artifact.state_dict)
        except FileNotFoundError:
            cls.logger.error(f"Failed to load model artifact from {artifact_dir}. Model will not be available "
                              f"for predictions.")
            return cls(model=None, is_available=False)

        return cls(model=model, is_available=True)


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
                label = PersonLabelEncoder.decode(user_type_int=pred_idx)
                results.append(PersonPredict(name=target_names[i], user_type=label, confidence=confidence))
                self.logger.debug(f"Predicted {target_names[i]} as {label} with confidence {confidence:.4f}")
        return results

    def is_model_available(self) -> bool:
        return self.is_available