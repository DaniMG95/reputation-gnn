from brain.architectures.bot_detector_gcn import BotDetectorGCN
from brain.architectures.bot_detector_gcn_sage import BotDetectorGnnSage
from enum import Enum

class TypeModel(str, Enum):
    GCN = "gcn"
    SAGE = "sage"

class ModelFactory:
    _map_model = {
        "gcn": BotDetectorGCN,
        "sage": BotDetectorGnnSage
    }


    @classmethod
    def create_model(cls, model_name: TypeModel, **kwargs):
        if model_name not in cls._map_model:
            raise ValueError(f"Model '{model_name}' not found in factory.")
        model_class = cls._map_model[model_name]
        return model_class(**kwargs)