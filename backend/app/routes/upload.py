from fastapi import APIRouter, UploadFile, File
import shutil
import os
from backend.app.services.extract_metadata import extract_image_metadata
from backend.app.services.ndvi_processor import compute_ndvi

router = APIRouter()
UPLOAD_DIR = "backend/app/uploads"
NDVI_DIR = "backend/app/ndvi_outputs"

@router.post("/upload/")
async def upload_image(files: list[UploadFile] = File(...)):
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    os.makedirs(NDVI_DIR, exist_ok=True)

    uploaded = []
    red_path = nir_path = thermal_path = None
    ndvi_file = lst_file = None

    for file in files:
        file_path = os.path.join(UPLOAD_DIR, file.filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        metadata = extract_image_metadata(file_path)
        uploaded.append({
            "filename": file.filename,
            "metadata": metadata
        })

        if "B04" in file.filename:
            red_path = file_path
        elif "B08" in file.filename:
            nir_path = file_path

    if red_path and nir_path:
        ndvi_file = compute_ndvi(nir_path, red_path, NDVI_DIR)
        
    return {
        "message": f"✅ {len(uploaded)} file(s) uploaded successfully",
        "files": uploaded,
        "ndvi_generated": bool(ndvi_file),
        "ndvi_file": ndvi_file,
        "lst_generated": bool(lst_file),
        "lst_file": lst_file
    }
