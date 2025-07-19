import rasterio
from rasterio.plot import show
import os


def inspect_image_metadata(image_path: str) -> dict:
    with rasterio.open(image_path) as src:
        metadata = {
            "crs": str(src.crs),
            "bounds": [float(b) for b in src.bounds],
            "width": src.width,
            "height": src.height,
            "count": src.count,
            "driver": src.driver
        }
    return metadata


if __name__ == "__main__":
    test_path = "backend/app/uploads/London_B04_2022-07-12.jp2"
    if os.path.exists(test_path):
        meta = inspect_image_metadata(test_path)
        print("🛰️ Metadata Extracted:\n", meta)
    else:
        print("❌ Image file not found:", test_path)
