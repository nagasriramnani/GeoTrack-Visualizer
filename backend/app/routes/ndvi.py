from fastapi import APIRouter
from fastapi.responses import FileResponse, JSONResponse
import os
from backend.app.services.ndvi_processor import get_ndvi_stats

router = APIRouter()
NDVI_DIR = "backend/app/ndvi_outputs"

@router.get("/ndvi/files")
def list_ndvi_files():
    files = [f for f in os.listdir(NDVI_DIR) if f.endswith(".tif")]
    return JSONResponse(content={"ndvi_files": files})

@router.get("/ndvi/{filename}")
def get_ndvi_file(filename: str):
    file_path = os.path.join(NDVI_DIR, filename)
    if os.path.exists(file_path):
        return FileResponse(path=file_path, media_type="image/tiff", filename=filename)
    return JSONResponse(status_code=404, content={"error": "File not found"})

@router.get("/ndvi/stats/{filename}")
def get_ndvi_statistics(filename: str):
    file_path = os.path.join(NDVI_DIR, filename)
    if os.path.exists(file_path):
        stats = get_ndvi_stats(file_path)
        return JSONResponse(content=stats)
    return JSONResponse(status_code=404, content={"error": "File not found"})
