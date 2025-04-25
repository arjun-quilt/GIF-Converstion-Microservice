from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    # API Settings
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "GIF Conversion Microservice"
    
    # GCP Settings
    GCP_BUCKET_NAME: str = "tiktok-actor-content"
    GCP_GIF_FOLDER: str = "gifs_20240419"
    
    # Apify Settings
    APIFY_API_TOKEN: str
    APIFY_ACTOR_TASK_URL: str = "https://api.apify.com/v2/actor-tasks/eKYRHMIgvYqAlh1r3/runs"
    YOUTUBE_ACTOR_TASK_URL : str = "https://api.apify.com/v2/actor-tasks/gCbxCQhqwZikH7fLZ/runs"
    
    # Video Processing Settings
    MAX_VIDEO_DURATION: int = 2  # seconds
    GIF_FPS: int = 3
    
    class Config:
        env_file = ".env"
        case_sensitive = True

@lru_cache()
def get_settings():
    return Settings()

settings = get_settings() 