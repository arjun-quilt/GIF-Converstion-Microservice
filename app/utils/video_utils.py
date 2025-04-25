from moviepy.editor import VideoFileClip
import yt_dlp
import re
from playwright.async_api import async_playwright
import nest_asyncio
import asyncio
import httpx

# Apply nested event loop fix
nest_asyncio.apply()

def convert_to_gif(video_path: str, output_path: str, max_duration: int = 2, fps: int = 3):
    """Convert a video to GIF with specified duration and FPS."""
    with VideoFileClip(video_path) as clip:
        if clip.duration > max_duration:
            clip = clip.subclip(0, max_duration)
        clip = clip.set_fps(fps)
        clip.write_gif(output_path)

async def download_youtube_video(url: str, output_path: str) -> str:
    """Download a YouTube video using yt-dlp."""
    ydl_opts = {
        'format': 'mp4',
        'outtmpl': output_path,
        'quiet': True,
        'socket_timeout': 30,
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36'
        },
        'nocheckcertificate': True,
        'merge_output_format': 'mp4',
        'postprocessors': [{
            'key': 'FFmpegVideoConvertor',
            'preferedformat': 'mp4',
        }],
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])
    return output_path

async def download_douyin_video(url: str, output_path: str) -> str:
    """Download a Douyin video using Playwright."""
    match = re.search(r'/video/(\d+)', url)
    if not match:
        raise Exception("Unable to extract video ID from URL")
    
    video_id = match.group(1)
    video_url = None
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        async def intercept_response(response):
            nonlocal video_url
            url = response.url
            if "video" in url and (url.endswith(".mp4") or "mime_type=video_mp4" in url):
                video_url = url
        
        page.on("response", intercept_response)
        await page.goto(url, timeout=120000)
        
        try:
            await page.wait_for_selector("video", timeout=15000)
        except Exception:
            pass
        
        await page.wait_for_timeout(5000)
        await browser.close()
    
    if not video_url:
        raise Exception("Failed to extract video URL")
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36",
        "Referer": "https://www.douyin.com/",
        "Range": "bytes=0-"
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.get(video_url, headers=headers)
        response.raise_for_status()
        
        with open(output_path, "wb") as f:
            f.write(response.content)
    
    return output_path 