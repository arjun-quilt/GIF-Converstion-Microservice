from pydantic import BaseModel
from typing import List, Optional

class VideoURL(BaseModel):
    url: str
    platform: str  # "tiktok", "youtube", "douyin", "gcs"

class BatchProcessRequest(BaseModel):
    urls: List[VideoURL]
    sheet_name: str

class GIFResponse(BaseModel):
    original_url: str
    gcs_url: Optional[str] = None
    gif_url: Optional[str] = None
    status: str
    error: Optional[str] = None

class BatchProcessResponse(BaseModel):
    results: List[GIFResponse]
    total_processed: int
    successful: int
    failed: int 