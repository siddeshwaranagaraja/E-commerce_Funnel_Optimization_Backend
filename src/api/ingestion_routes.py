from fastapi import APIRouter, UploadFile, File, HTTPException
from src.services.ingestion_service import run_ingestion_pipeline, load_data, clean_data, transform_data, save_to_db_events, save_to_db_stages

ingestion_router = APIRouter()

@ingestion_router.post("/manual-ingest")
async def manual_ingest(file: UploadFile = File(...)):
    """Manually ingest data from uploaded file."""
    # placeholder: handle file upload and process
    pass

@ingestion_router.post("/load-sample")
async def load_sample_dataset():
    """Load sample dataset."""
    # placeholder: load predefined sample data
    pass

@ingestion_router.post("/run-preprocessing")
async def run_preprocessing():
    """Run the full preprocessing pipeline."""
    # placeholder: execute pipeline and return status
    pass