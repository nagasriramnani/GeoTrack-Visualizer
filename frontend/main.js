document.addEventListener("DOMContentLoaded", () => {
  const downloadButton = document.getElementById("download-ndvi");
  const lstButton = document.getElementById("generate-lst");

  // NDVI Download Button
  if (downloadButton) {
    downloadButton.addEventListener("click", async () => {
      try {
        const response = await fetch("http://127.0.0.1:8000/ndvi/ndvi_output.tif");
        if (!response.ok) throw new Error("NDVI download failed");
        const blob = await response.blob();
        const url = URL.createObjectURL(blob);
        const link = document.createElement("a");
        link.href = url;
        link.download = "ndvi_output.tif";
        link.click();
        URL.revokeObjectURL(url);
      } catch (err) {
        console.error("❌ Download failed:", err);
      }
    });
  }

  // Leaflet Map Init
  const map = L.map("map").setView([51.5074, -0.1278], 10);
  L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
    maxZoom: 18,
    attribution: "© OpenStreetMap contributors"
  }).addTo(map);

  // Load NDVI Layers
  let ndviLayers = {};

  fetch("http://127.0.0.1:8000/ndvi/files")
    .then(res => {
      if (!res.ok) throw new Error(`NDVI file fetch failed: ${res.status}`);
      return res.json();
    })
    .then(data => {
      if (!data.ndvi_files || !data.ndvi_files.length) {
        throw new Error("No NDVI files found in response");
      }

      data.ndvi_files.forEach(filename => {
        fetch(`http://127.0.0.1:8000/ndvi/${filename}`)
          .then(res => res.arrayBuffer())
          .then(tiffData => parseGeoraster(tiffData))
          .then(georaster => {
            const layer = new GeoRasterLayer({
              georaster,
              opacity: 0.6,
              resolution: 256,
              pixelValuesToColorFn: val => {
                if (val == null) return null;
                if (val < 0) return "#d73027";
                if (val < 0.1) return "#f46d43";
                if (val < 0.2) return "#fdae61";
                if (val < 0.3) return "#fee08b";
                if (val < 0.4) return "#d9ef8b";
                if (val < 0.5) return "#a6d96a";
                if (val < 0.6) return "#66bd63";
                return "#1a9850";
              }
            });

            ndviLayers[filename] = layer;

            if (Object.keys(ndviLayers).length === 1) {
              layer.addTo(map);
              map.fitBounds(layer.getBounds());
              setTimeout(() => loadNDVIStats(filename), 500);
            }

            L.control.layers(null, ndviLayers, { collapsed: false }).addTo(map);
          })
          .catch(err => console.error("❌ Failed to load GeoTIFF:", err));
      });
    })
    .catch(err => console.error("❌ Failed to load NDVI layers:", err));

  // Load NDVI Stats
  function loadNDVIStats(filename) {
    fetch(`http://127.0.0.1:8000/ndvi/stats/${filename}`)
      .then(res => {
        if (!res.ok) throw new Error(`NDVI stats failed: ${res.status}`);
        return res.json();
      })
      .then(stats => {
        const statsBox = document.getElementById("ndvi-stats-text");
        const histogramImg = document.getElementById("ndvi-histogram");

        statsBox.innerHTML = `
          <p><strong>Mean:</strong> ${stats.mean.toFixed(3)}</p>
          <p><strong>Std Dev:</strong> ${stats.std.toFixed(3)}</p>
          <p><strong>Min:</strong> ${stats.min.toFixed(3)}</p>
          <p><strong>Max:</strong> ${stats.max.toFixed(3)}</p>
          <p><strong>Barren Pixels:</strong> ${stats.classes.barren.toLocaleString()}</p>
          <p><strong>Low Vegetation:</strong> ${stats.classes.low.toLocaleString()}</p>
          <p><strong>Moderate Vegetation:</strong> ${stats.classes.moderate.toLocaleString()}</p>
          <p><strong>Healthy Vegetation:</strong> ${stats.classes.healthy.toLocaleString()}</p>
          <p><strong>% Vegetated:</strong> ${stats.veg_percent}%</p>
        `;

        histogramImg.src = `data:image/png;base64,${stats.histogram_base64}`;
      })
      .catch(err => console.error("❌ Failed to load NDVI stats:", err));
  }

  // LST Generation
  if (lstButton) {
    lstButton.addEventListener("click", async () => {
      const lstBox = document.getElementById("lst-stats-text");
      try {
        const res = await fetch("http://127.0.0.1:8000/lst/compute");
        if (!res.ok) throw new Error("LST computation failed");
        const data = await res.json();

        lstBox.innerHTML = `
          <p><strong>Status:</strong> ${data.message}</p>
          <p><strong>Filename:</strong> ${data.filename}</p>
          <a href="http://127.0.0.1:8000/lst/${data.filename}" target="_blank">⬇️ Download LST File</a>
        `;
      } catch (err) {
        console.error("❌ LST generation error:", err);
        lstBox.innerHTML = `<p style="color:red;">❌ Failed to generate LST.</p>`;
      }
    });
  }
});
