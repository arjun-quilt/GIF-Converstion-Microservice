import httpx
import asyncio
from app.core.config import settings

class ApifyClient:
    def __init__(self):
        self.api_token = settings.APIFY_API_TOKEN
        self.base_url = f"https://api.apify.com/v2/actor-tasks/{settings.TIKTOK_SCRAPER_TASK_ID}/runs"

    async def run_actor_task(self, video_url: str) -> str:
        """Run the Apify actor task and return the run ID."""
        url = f"{self.base_url}?token={self.api_token}"
        headers = {"Content-Type": "application/json"}
        
        data = {
            "disableCheerioBoost": False,
            "disableEnrichAuthorStats": False,
            "resultsPerPage": 1,
            "searchSection": "/video",
            "shouldDownloadCovers": True,
            "shouldDownloadSlideshowImages": False,
            "shouldDownloadVideos": True,
            "maxProfilesPerQuery": 10,
            "tiktokMemoryMb": "default",
            "postURLs": [video_url]
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