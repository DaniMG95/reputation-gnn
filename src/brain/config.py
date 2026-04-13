from pydantic_settings import BaseSettings
from brain.trainers.factory import TypeModelTrainer
from brain.architectures.factory import TypeModel

class Settings(BaseSettings):
    uri_neo4j: str
    model_name: TypeModel = TypeModel.GCN
    model_path: str = "bot_detector_gcn.pth"
    hidden_channels: int  = 32
    epochs: int = 200
    learning_rate: float = 0.01
    ratio_validation: float = 0.2
    ratio_test: float = 0.1
    n_nodes_test: int = 20
    type_trainer: TypeModelTrainer = TypeModelTrainer.FULL
    num_neighbors: list[int] = [25, 15]
    batch_size: int = 128
    early_stopping_patience: int = 10
    early_stopping_delta: float = 0.001

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        extra = 'ignore'

settings = Settings()