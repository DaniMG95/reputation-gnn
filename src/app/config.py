from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    uri_neo4j: str
    model_name: str = "bot_detector_gcn"
    model_path: str = "/app/bot_detector_gcn.pth"
    hidden_channels: int  = 32
    num_features: int = 4
    out_channels: int = 2
    host_redis: str = "localhost"
    port_redis: int = 6379
    db_redis: int = 0

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        extra = 'ignore'

settings = Settings()