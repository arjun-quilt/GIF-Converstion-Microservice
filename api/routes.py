from fastapi import APIRouter, HTTPException, BackgroundTasks
from model.schemas import BatchProcessRequest, BatchProcessResponse
from services.video_processor import VideoProcessor
from core.config import settings

router = APIRouter()
video_processor = VideoProcessor()

@router.post("/process-batch", response_model=BatchProcessResponse)
async def process_batch(request: BatchProcessRequest, background_tasks: BackgroundTasks):
    try:
        results = await video_processor.process_batch(request.urls, request.sheet_name)
        return BatchProcessResponse(
            results=results,
            total_processed=len(results),
            successful=sum(1 for r in results if r.status == "success"),
            failed=sum(1 for r in results if r.status == "failed")
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
