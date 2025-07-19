import rasterio
from rasterio.plot import reshape_as_image
from typing import Dict

def extract_image_metadata(file_path: str) -> Dict:
    try:
        with rasterio.open(file_path) as src:
            metadata = {
                "filename": file_path,
                "crs": str(src.crs),
                "bounds": src.bounds._asdict(),
                "width": src.width,
                "height": src.height,
                "resolution": src.res,
                "count": src.count,
                "driver": src.driver,
                "dtype": src.dtypes[0]
            }
            return metadata
    except Exception as e:
        raise RuntimeError(f"❌ Failed to extract metadata: {e}")
