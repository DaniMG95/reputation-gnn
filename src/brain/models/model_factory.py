from brain.models.bot_detector_gcn import BotDetectorGCN
from brain.models.bot_detector_gcn_sage import BotDetectorGnnSage

class ModelFactory:
    _map_model = {
        "bot_detector_gcn": BotDetectorGCN,
        "bot_detector": BotDetectorGnnSage
    }


    @classmethod
    def create_model(cls, model_name: str, **kwargs):
        if model_name not in cls._map_model:
            raise ValueError(f"Model '{model_name}' not found in factory.")
        model_class = cls._map_model[model_name]
        return model_class(**kwargs)