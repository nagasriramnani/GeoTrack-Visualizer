from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.app.routes import upload, ndvi

app = FastAPI(
    title="GeoTrack - Satellite Ingestion API",
    description="Processes Sentinel imagery for NDVI and LST computation.",
    version="1.0.0"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change to your frontend origin in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(upload.router)
app.include_router(ndvi.router)

@app.get("/")
def read_root():
    return {"status": "OK", "message": "GeoTrack backend is live"}
