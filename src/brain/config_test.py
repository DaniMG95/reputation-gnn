from pydantic_settings import BaseSettings, SettingsConfigDict
from core.settings.neo4j import Neo4jSettings
from pydantic import Field
from brain.trainers.factory import TypeModelTrainer
from core.ml.models.type_model import TypeModel
from core.settings.logger import AppLoggerSettings

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="BRAIN_", env_file='.env', env_file_encoding='utf-8',
                                      case_sensitive=False, extra='ignore')

    model_path: str = "bot_detector_gcn.pth"
    n_nodes_test: int = 20
    neo4j: Neo4jSettings = Field(default_factory=Neo4jSettings)
    app_logger: AppLoggerSettings = Field(default_factory=AppLoggerSettings)

settings = Settings()