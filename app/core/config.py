from pydantic import Field
from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    # Logging Settings
    logger: str = "logging"
    log_level: str = "DEBUG"
    debug_timing: bool = False
    fastapi_app: str = "main.app"

    # API Settings
    API_PREFIX: str = Field(..., env="API_PREFIX")
    ALLOWED_HOSTS: str = Field(..., env="ALLOWED_HOSTS")
    API_KEY: str = Field(..., env="API_KEY")
    
    # Apify Settings
    TIKTOK_SCRAPER_TASK_ID: str = Field(..., validation_alias="TIKTOK_SCRAPER_TASK_ID")
    YOUTUBE_SCRAPER_TASK_ID: str = Field(..., validation_alias="YOUTUBE_SCRAPER_TASK_ID")
    APIFY_API_TOKEN: str = Field(..., env="APIFY_API_TOKEN")
    
    # GCP Settings
    bucket_name: str = Field(..., validation_alias="TIKTOK_BUCKET")
    image_extracted_folder_name: str = Field(..., validation_alias="IMAGE_EXTRACTED_FOLDER_PATH")
    
    # Video Processing Settings
    MAX_VIDEO_DURATION: int = 2  # seconds
    GIF_FPS: int = 3

    class Config:
        env_file = ".env"
        extra = "allow"

@lru_cache()
def get_settings():
    return Settings()

settings = get_settings() 


