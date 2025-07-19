import rasterio
import numpy as np
import os
from datetime import datetime
import matplotlib
matplotlib.use('Agg')  # Use non-GUI backend for FastAPI
import matplotlib.pyplot as plt
import io
import base64

def compute_ndvi(nir_path, red_path, output_dir):
    with rasterio.open(nir_path) as nir_src, rasterio.open(red_path) as red_src:
        nir = nir_src.read(1).astype("float32")
        red = red_src.read(1).astype("float32")

        # Scale values from 0–10000 to 0–1
        nir = nir / 10000.0
        red = red / 10000.0

        # Avoid division by 0 and compute NDVI
        np.seterr(divide='ignore', invalid='ignore')
        ndvi = (nir - red) / (nir + red + 1e-6)
        ndvi = np.clip(ndvi, -1, 1)

        profile = nir_src.profile
        profile.update(
            dtype=rasterio.float32,
            count=1,
            driver="GTiff"
        )

        ndvi_filename = "ndvi_output.tif"
        output_path = os.path.join(output_dir, ndvi_filename)

        with rasterio.open(output_path, "w", **profile) as dst:
            dst.write(ndvi, 1)

        print("✅ NDVI saved to", output_path)
        return ndvi_filename


def get_ndvi_stats(ndvi_path):
    with rasterio.open(ndvi_path) as src:
        ndvi = src.read(1).astype("float32")
        mask = ndvi != src.nodata if src.nodata is not None else ~np.isnan(ndvi)
        valid_ndvi = ndvi[mask]

        mean_val = float(np.mean(valid_ndvi))
        std_val = float(np.std(valid_ndvi))
        min_val = float(np.min(valid_ndvi))
        max_val = float(np.max(valid_ndvi))

        # Histogram image
        fig, ax = plt.subplots()
        ax.hist(valid_ndvi, bins=20, color='green', edgecolor='black')
        ax.set_title("NDVI Histogram")
        ax.set_xlabel("NDVI Value")
        ax.set_ylabel("Frequency")
        buf = io.BytesIO()
        plt.tight_layout()
        plt.savefig(buf, format="png")
        buf.seek(0)
        histogram_base64 = base64.b64encode(buf.read()).decode("utf-8")
        buf.close()
        plt.close(fig)

        # Classification
        total_pixels = len(valid_ndvi)
        barren = np.sum(valid_ndvi < 0.1)
        low_veg = np.sum((valid_ndvi >= 0.1) & (valid_ndvi < 0.3))
        moderate_veg = np.sum((valid_ndvi >= 0.3) & (valid_ndvi < 0.5))
        healthy_veg = np.sum(valid_ndvi >= 0.5)
        veg_percent = float((healthy_veg + moderate_veg + low_veg) / total_pixels * 100)

        return {
            "mean": mean_val,
            "std": std_val,
            "min": min_val,
            "max": max_val,
            "histogram_base64": histogram_base64,
            "classes": {
                "barren": int(barren),
                "low": int(low_veg),
                "moderate": int(moderate_veg),
                "healthy": int(healthy_veg)
            },
            "veg_percent": round(veg_percent, 2)
        }
