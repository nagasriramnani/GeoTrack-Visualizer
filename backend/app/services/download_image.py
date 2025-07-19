import os
import requests

def download_sentinel_band(band_url: str, band_name: str, save_dir: str = "backend/app/uploads") -> str:
    os.makedirs(save_dir, exist_ok=True)
    filename = os.path.join(save_dir, band_name)

    response = requests.get(band_url)
    if response.status_code == 200:
        with open(filename, "wb") as f:
            f.write(response.content)
        print(f"✅ Downloaded {band_name}")
    else:
        raise Exception(f"❌ Failed to download {band_name}. Status code: {response.status_code}")
    
    return filename

if __name__ == "__main__":
    B04_URL = "https://sentinel-s2-l2a.s3.amazonaws.com/tiles/30/U/XC/2022/7/12/0/R10m/B04.jp2"
    B08_URL = "https://sentinel-s2-l2a.s3.amazonaws.com/tiles/30/U/XC/2022/7/12/0/R10m/B08.jp2"
    B11_URL = "https://sentinel-s2-l2a.s3.amazonaws.com/tiles/30/U/XC/2022/7/12/0/R20m/B11.jp2"

    red_path = download_sentinel_band(B04_URL, "London_B04_2022-07-12.jp2")
    nir_path = download_sentinel_band(B08_URL, "London_B08_2022-07-12.jp2")
    thermal_path = download_sentinel_band(B11_URL, "London_B11_2022-07-12.jp2")
