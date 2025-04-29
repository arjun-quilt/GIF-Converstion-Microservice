import httpx
import asyncio
from core.config import settings

class YouTubeClient:
    def __init__(self):
        self.api_token = settings.APIFY_API_TOKEN
        self.base_url = f"https://api.apify.com/v2/actor-tasks/{settings.YOUTUBE_SCRAPER_TASK_ID}/runs"

    async def run_actor_task(self, video_url: str) -> str:
        """Run the Apify actor task for YouTube Shorts and return the run ID."""
        url = f"{self.base_url}?token={self.api_token}"
        headers = {"Content-Type": "application/json"}
        
        data = {
            "includeFailedVideos": False,
            "proxy": {
                "useApifyProxy": True
            },
            "quality": "480",
            "startUrls": [video_url],
            "useFfmpeg": False
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=data, headers=headers)
            response.raise_for_status()
            return response.json()["data"]["id"]

    async def wait_for_completion(self, run_id: str) -> str:
        """Wait for the Apify run to complete and return the dataset ID."""
        url = f"https://api.apify.com/v2/actor-runs/{run_id}?token={self.api_token}"
        
        while True:
            async with httpx.AsyncClient() as client:
                response = await client.get(url)
                response.raise_for_status()
                data = response.json()
                
                status = data["data"]["status"]
                if status == "SUCCEEDED":
                    return data["data"]["defaultDatasetId"]
                elif status == "FAILED":
                    raise Exception(f"Apify run failed: {data['data'].get('error', 'Unknown error')}")
                
                await asyncio.sleep(5)

    async def get_items(self, dataset_id: str) -> list:
        """Get items from the Apify dataset."""
        url = f"https://api.apify.com/v2/datasets/{dataset_id}/items?clean=true&token={self.api_token}"
        
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            response.raise_for_status()
            return response.json()

    async def download_video(self, video_url: str, output_path: str) -> str:
        """Download a YouTube Shorts video using Apify."""
        try:
            # Run Apify actor task
            run_id = await self.run_actor_task(video_url)
            
            # Wait for completion and get results
            dataset_id = await self.wait_for_completion(run_id)
            items = await self.get_items(dataset_id)
            
            if not items:
                raise Exception("No items returned from Apify")
            
            # Get the first item's download URL
            download_url = items[0].get('downloadUrl')
            if not download_url:
                raise Exception("No download URL returned from Apify")
            
            # Download the video
            async with httpx.AsyncClient() as client:
                response = await client.get(download_url)
                response.raise_for_status()
                
                with open(output_path, "wb") as f:
                    f.write(response.content)
            
            return output_path
            
        except Exception as e:
            raise Exception(f"Failed to download YouTube Shorts video: {str(e)}") 