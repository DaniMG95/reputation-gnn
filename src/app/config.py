from pydantic_settings import BaseSettings, SettingsConfigDict
from core.settings.neo4j import Neo4jSettings
from core.settings.logger import AppLoggerSettings
from pydantic import Field


class AppSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="APP_", env_file='.env', env_file_encoding='utf-8',
                                      case_sensitive=False, extra='ignore')
    model_path: str = "/app/bot_detector_gcn.pth"
    host_redis: str = "localhost"
    port_redis: int = 6379
    db_redis: int = 0
    neo4j: Neo4jSettings = Field(default_factory=Neo4jSettings)
    app_logger: AppLoggerSettings = Field(default_factory=AppLoggerSettings)


settings = AppSettings()