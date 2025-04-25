import asyncio
import httpx
import os
import tempfile
import subprocess
from typing import List
from app.models.schemas import VideoURL, GIFResponse
from app.core.config import settings
from app.utils.gcs_client import GCSClient
from app.utils.video_utils import convert_to_gif, download_douyin_video
from app.utils.apify_client import ApifyClient
from app.utils.youtube_client import YouTubeClient

class VideoProcessor:
    def __init__(self):
        self.gcs_client = GCSClient()
        self.apify_client = ApifyClient()
        self.youtube_client = YouTubeClient()
        self._tasks = {}
        self._ensure_playwright_installed()

    def _ensure_playwright_installed(self):
        """Ensure Playwright browsers are installed."""
        try:
            subprocess.run(["playwright", "install", "chromium"], check=True, capture_output=True)
        except subprocess.CalledProcessError as e:
            print(f"Error installing Playwright browsers: {e.stderr.decode()}")
            raise Exception("Failed to install Playwright browsers. Please run 'playwright install chromium' manually.")

    async def process_batch(self, urls: List[VideoURL], country_name: str) -> List[GIFResponse]:
        results = []
        
        for video_url in urls:
            try:
                # Process based on platform
                if video_url.platform == "tiktok":
                    result = await self._process_tiktok(video_url.url)
                elif video_url.platform == "youtube":
                    result = await self._process_youtube(video_url.url)
                elif video_url.platform == "douyin":
                    result = await self._process_douyin(video_url.url)
                elif video_url.platform == "gcs":
                    result = await self._process_gcs(video_url.url)
                else:
                    result = GIFResponse(
                        original_url=video_url.url,
                        status="failed",
                        error=f"Unsupported platform: {video_url.platform}"
                    )
                
                results.append(result)
                
            except Exception as e:
                results.append(GIFResponse(
                    original_url=video_url.url,
                    status="failed",
                    error=str(e)
                ))
        
        return results

    async def _process_tiktok(self, url: str) -> GIFResponse:
        try:
            # Run Apify actor task
            run_id = await self.apify_client.run_actor_task(url)
            
            # Wait for completion and get results
            dataset_id = await self.apify_client.wait_for_completion(run_id)
            items = await self.apify_client.get_items(dataset_id)
            
            if not items:
                return GIFResponse(
                    original_url=url,
                    status="failed",
                    error="No items returned from Apify"
                )
            
            # Process the first item
            item = items[0]
            gcs_url = item.get("gcsMediaUrls", [None])[0]
            
            if not gcs_url:
                return GIFResponse(
                    original_url=url,
                    status="failed",
                    error="No GCS URL returned from Apify"
                )
            
            # Convert to GIF
            gif_url = await self._convert_and_upload_gif(gcs_url)
            
            return GIFResponse(
                original_url=url,
                gcs_url=gcs_url,
                gif_url=gif_url,
                status="success"
            )
        except Exception as e:
            return GIFResponse(
                original_url=url,
                status="failed",
                error=str(e)
            )

    async def _process_youtube(self, url: str) -> GIFResponse:
        with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as temp_file:
            video_path = temp_file.name
        
        try:
            # Download video using YouTube client
            video_path = await self.youtube_client.download_video(url, video_path)
            
            # Upload to GCS
            gcs_url = await self.gcs_client.upload_video(video_path)
            
            # Convert to GIF
            gif_url = await self._convert_and_upload_gif(gcs_url)
            
            return GIFResponse(
                original_url=url,
                gcs_url=gcs_url,
                gif_url=gif_url,
                status="success"
            )
        except Exception as e:
            return GIFResponse(
                original_url=url,
                status="failed",
                error=str(e)
            )
        finally:
            if os.path.exists(video_path):
                os.unlink(video_path)

    async def _process_douyin(self, url: str) -> GIFResponse:
        with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as temp_file:
            video_path = temp_file.name
        
        try:
            # Download video
            video_path = await download_douyin_video(url, video_path)
            
            # Upload to GCS
            gcs_url = await self.gcs_client.upload_video(video_path)
            
            # Convert to GIF
            gif_url = await self._convert_and_upload_gif(gcs_url)
            
            return GIFResponse(
                original_url=url,
                gcs_url=gcs_url,
                gif_url=gif_url,
                status="success"
            )
        except Exception as e:
            return GIFResponse(
                original_url=url,
                status="failed",
                error=str(e)
            )
        finally:
            if os.path.exists(video_path):
                os.unlink(video_path)

    async def _process_gcs(self, url: str) -> GIFResponse:
        try:
            # Convert to GIF
            gif_url = await self._convert_and_upload_gif(url)
            
            return GIFResponse(
                original_url=url,
                gcs_url=url,
                gif_url=gif_url,
                status="success"
            )
        except Exception as e:
            return GIFResponse(
                original_url=url,
                status="failed",
                error=str(e)
            )

    async def _convert_and_upload_gif(self, video_url: str) -> str:
        with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as temp_video:
            video_path = temp_video.name
        
        with tempfile.NamedTemporaryFile(suffix=".gif", delete=False) as temp_gif:
            gif_path = temp_gif.name
        
        try:
            # Download video
            async with httpx.AsyncClient() as client:
                response = await client.get(video_url)
                with open(video_path, "wb") as f:
                    f.write(response.content)
            
            # Convert to GIF
            convert_to_gif(
                video_path,
                gif_path,
                max_duration=settings.MAX_VIDEO_DURATION,
                fps=settings.GIF_FPS
            )
            
            # Upload GIF to GCS
            gif_url = await self.gcs_client.upload_gif(gif_path)
            
            return gif_url
        finally:
            if os.path.exists(video_path):
                os.unlink(video_path)
            if os.path.exists(gif_path):
                os.unlink(gif_path)

    async def get_task_status(self, task_id: str) -> str:
        return self._tasks.get(task_id, "unknown") 