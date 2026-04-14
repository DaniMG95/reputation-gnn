from core.ml.models.gcn import Gcn
from core.ml.models.graphsage import GraphSage
from core.ml.serialization.model_artifact import ModelArtifactMetadata
from core.ml.models.type_model import TypeModel


class ModelFactory:
    _map_model = {
        "gcn": Gcn,
        "sage": GraphSage
    }


    @classmethod
    def create_model(cls, model_name: TypeModel, in_channels: int, hidden_channels: int, out_channels: int):
        if model_name not in cls._map_model:
            raise ValueError(f"Model '{model_name}' not found in factory.")
        model_class = cls._map_model[model_name]
        return model_class(in_channels=in_channels, hidden_channels=hidden_channels, out_channels=out_channels)

    @classmethod
    def create_from_metadata(cls, metadata: ModelArtifactMetadata):
        return cls.create_model(
            model_name=metadata.model_name,
            in_channels=metadata.input_dim,
            hidden_channels=metadata.hidden_dim,
            out_channels=metadata.output_dim,
        )