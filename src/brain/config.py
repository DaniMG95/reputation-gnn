from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    model_name: str = "bot_detector_gcn"
    model_path: str = "bot_detector_gcn.pth"
    hidden_channels: int  = 32
    epochs: int = 200
    learning_rate: float = 0.01
    ratio_validation: float = 0.2
    ratio_test: float = 0.1
    n_nodes_test: int = 20

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        extra = 'ignore'

settings = Settings()