from pydantic_settings import BaseSettings, SettingsConfigDict
from core.settings.neo4j import Neo4jSettings
from pydantic import Field
from brain.trainers.factory import TypeModelTrainer
from core.ml.models.type_model import TypeModel
from core.settings.logger import AppLoggerSettings

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="BRAIN_", env_file='.env', env_file_encoding='utf-8',
                                      case_sensitive=False, extra='ignore')

    model_name: TypeModel = TypeModel.GCN
    model_path: str = "bot_detector_gcn.pth"
    num_features: int = 4
    hidden_channels: int  = 32
    output_channels: int = 2
    epochs: int = 200
    learning_rate: float = 0.01
    ratio_validation: float = 0.2
    ratio_test: float = 0.1
    type_trainer: TypeModelTrainer = TypeModelTrainer.FULL
    num_neighbors: list[int] = [25, 15]
    batch_size: int = 128
    early_stopping_patience: int = 10
    early_stopping_delta: float = 0.001
    neo4j: Neo4jSettings = Field(default_factory=Neo4jSettings)
    app_logger: AppLoggerSettings = Field(default_factory=AppLoggerSettings)

settings = Settings()