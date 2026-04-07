from brain.trainers.full_batch import FullBatch
from brain.trainers.sampling import Sampling
from enum import Enum

class TypeModelTrainer(str, Enum):
    SAMPLING = "sampling"
    FULL = "full"


class ModelTrainerFactory:
    _map_model = {
        TypeModelTrainer.SAMPLING: Sampling,
        TypeModelTrainer.FULL: FullBatch
    }


    @classmethod
    def create_trainer_model(cls, type_model_trainer: TypeModelTrainer, **kwargs):
        if type_model_trainer not in cls._map_model:
            raise ValueError(f"Model '{type_model_trainer}' not found in factory.")
        model_class = cls._map_model[type_model_trainer]
        return model_class(**kwargs)