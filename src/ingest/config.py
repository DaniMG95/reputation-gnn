from pydantic_settings import BaseSettings

class Settings(BaseSettings):
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

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        extra = 'ignore'

settings = Settings()