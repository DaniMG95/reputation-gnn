from pydantic_settings import BaseSettings, SettingsConfigDict
from core.settings.neo4j import Neo4jSettings
from core.settings.logger import AppLoggerSettings
from pydantic import Field

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="INGEST_", env_file='.env', env_file_encoding='utf-8',
                                      case_sensitive=False, extra='ignore')

    mean_posts: int = 400
    max_posts_influencers: int = 1500
    mean_posts_bots: int = 15
    percentage_followers_influencers: float = 0.85
    deviation_followers_influencers: float = 0.05
    percentage_followers_person: float = 0.05
    percentage_persons_follow_to_bots: float = 0.02
    percentage_follow_to_bots: float = 0.05
    percentage_bots_following_persons: float = 0.80
    deviation_bots_following_persons: float = 0.10
    percentage_bots_follow_bots: float = 0.9
    percentage_verified_person: float = 0.3
    n_accounts: int = 100
    p_bots: float = 0.3
    p_influencers: float = 0.2
    neo4j: Neo4jSettings = Field(default_factory=Neo4jSettings)
    app_logger: AppLoggerSettings = Field(default_factory=AppLoggerSettings)

settings = Settings()