from google.cloud import storage
from app.core.config import settings
import os

class GCSClient:
    def __init__(self):
        self.client = storage.Client()
        self.bucket = self.client.bucket(settings.bucket_name)

    async def upload_video(self, file_path: str) -> str:
        """Upload a video file to GCS and return its URL."""
        blob_name = os.path.basename(file_path)
        blob = self.bucket.blob(blob_name)
        
        blob.upload_from_filename(file_path)
        return f"https://storage.googleapis.com/{settings.bucket_name}/{blob_name}"

    async def upload_gif(self, file_path: str) -> str:
        """Upload a GIF file to GCS and return its URL."""
        blob_name = f"{settings.image_extracted_folder_name}/{os.path.basename(file_path)}"
        blob = self.bucket.blob(blob_name)
        
        blob.upload_from_filename(file_path)
        return f"https://storage.googleapis.com/{settings.bucket_name}/{blob_name}" 