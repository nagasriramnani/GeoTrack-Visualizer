# backend/app/services/colorize_ndvi.py

import numpy as np
import rasterio
from matplotlib import cm
from matplotlib.colors import Normalize

def colorize_ndvi(input_path, output_path):
    with rasterio.open(input_path) as src:
        ndvi = src.read(1)
        meta = src.meta.copy()

    norm = Normalize(vmin=-1, vmax=1)
    cmap = cm.get_cmap("RdYlGn")
    colored = (cmap(norm(ndvi))[:, :, :3] * 255).astype(np.uint8)

    meta.update({
        "count": 3,
        "dtype": "uint8"
    })

    with rasterio.open(output_path, 'w', **meta) as dst:
        for i in range(3):
            dst.write(colored[:, :, i], i + 1)
