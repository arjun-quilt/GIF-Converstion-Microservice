# GIF Conversion Microservice

A microservice for converting videos from various platforms (TikTok, YouTube, Douyin) to GIFs.

## Features

- Convert videos from multiple platforms to GIFs
- Support for TikTok, YouTube, Douyin, and GCS videos
- Asynchronous processing
- Google Cloud Storage integration
- Apify integration for TikTok video processing

## Prerequisites

- Python 3.8+
- Google Cloud credentials
- Apify API token
- Playwright browsers installed

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd gif-microservice
```

2. Create a virtual environment and activate it:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Install Playwright browsers:
```bash
playwright install chromium
```

5. Create a `.env` file with the following variables:
```env
APIFY_API_TOKEN=your_apify_token
GCP_BUCKET_NAME=your_bucket_name
GCP_GIF_FOLDER=your_gif_folder
```

## Running the Service

1. Start the service:
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

2. Access the API documentation at:
```
http://localhost:8000/docs
```

## API Endpoints

### POST /api/v1/process-batch
Process a batch of videos and convert them to GIFs.

Request body:
```json
{
  "urls": [
    {
      "url": "https://example.com/video",
      "platform": "tiktok"
    }
  ],
  "country_name": "US"
}

#youtube
{
  "urls": [
    {
      "url": "https://youtube.com/shorts/zsvfUQgwfdU",
      "platform": "youtube"
    }
  ],
  "country_name": "US"
}
```

### GET /api/v1/status/{task_id}
Get the status of a processing task.

## Development

### Project Structure
```
app/
├── api/
│   └── routes.py
├── core/
│   └── config.py
├── models/
│   └── schemas.py
├── services/
│   └── video_processor.py
├── utils/
│   ├── gcs_client.py
│   ├── apify_client.py
│   └── video_utils.py
└── main.py
```

### Testing
```bash
pytest
```

## License

MIT 