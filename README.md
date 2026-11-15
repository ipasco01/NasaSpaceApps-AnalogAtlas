# Analog Atlas · Team Ctrl Z

> NASA Space Apps Challenge 2026 · Piura local event
> Challenge: *Identify Earth Locations that Analog the Permanent Moon Base Locations and Mars*
> *There's no Ctrl+Z on Mars. Analog Atlas finds where to rehearse on Earth.*

Analog Atlas searches the whole Earth for places that resemble a chosen site on the Moon or Mars, using NASA data. For each place it shows how similar it is, variable by variable, and where the analogy breaks down.

## What it does

1. **Pick a target site:** Jezero crater or Gale crater (Mars), Shackleton crater rim or Marius Hills (Moon).
2. **Score every land cell on Earth:** 334,741 cells of 0.25° (about 28 km), compared with the target on temperature, slope, vegetation, barren ground, ice, snow, permafrost, airborne dust and rock type.
3. **See the ranking on a map:** each place gets a 0-100 similarity score with a per-variable breakdown.
4. **Understand the limits:** each place card says which conditions Earth cannot reach (for example lunar night temperatures, vacuum, gravity or radiation).
5. **Find new analogs:** discovery mode hides the 17 well-known analog sites (Atacama, Devon Island, Río Tinto and others) so less-studied places come up.
6. **Plan mission tests:** each place card says what it is good for (rover driving, habitat, spacesuit tests) and compares Earth and target images side by side.

## How the score works

`backend/motor.py` compares each Earth cell with the target value of each variable and turns the difference into a 0-1 similarity. The total score is a weighted geometric mean, so one very bad variable pulls the whole score down. Temperatures that Earth can never reach are reported separately instead of hiding every result. A sensitivity test moves each weight ±20 % and reports how much of the Top 10 stays the same.

## Data

All sources, variables and references are in [`USO_DE_IA_Y_FUENTES.md`](USO_DE_IA_Y_FUENTES.md) and the processing notes in [`datos/FUENTES.md`](datos/FUENTES.md). In short:

- **Earth:** NASA MODIS (land surface temperature, NDVI, land cover, snow), NASA MERRA-2 (dust), NOAA ETOPO1 (elevation and slope), GLiM (rock type). Processed in Google Earth Engine with `data-pipeline/earth_engine_tierra.js`.
- **Moon and Mars:** NASA PDS (MOLA, LOLA, LRO Diviner) and rover measurements (Curiosity REMS, Perseverance MEDA). Reference values per site are in `science/referencias.csv`, each with its source.
- **Images:** NASA Mars Trek and Moon Trek; Sentinel-2 cloudless by EOX for Earth.

**Known limits:** precipitation (GPM IMERG) is not in this version, so dryness does not count in the score. A 28 km cell averages out small features such as single lava tubes or crater walls. Earth cannot reproduce reduced gravity, vacuum or the radiation environment of the Moon and Mars.

## Run it

With Docker:

```bash
docker build -t analog-atlas .
docker run -p 8000:8000 analog-atlas
# open http://localhost:8000
```

Without Docker:

```bash
pip install -r requirements-api.txt
cd frontend && npm ci && npm run build && cd ..
python -m api.main          # http://127.0.0.1:8000  (API docs at /docs)
```

Engine only, from the terminal:

```bash
python backend/motor.py --celdas datos/celdas.parquet --sitio gale --descubrimiento --sensibilidad
```

## Repository

| Path | Contents |
|---|---|
| `frontend/` | Web app (React, Vite, MapLibre GL) |
| `api/`, `services/`, `models/` | FastAPI server that serves the app and the search endpoint |
| `backend/motor.py` | Similarity engine, discovery mode and sensitivity test |
| `data-pipeline/` | Earth Engine export script and converters from raster to table |
| `datos/` | Earth table (`celdas.parquet`) and source notes |
| `science/` | Moon and Mars reference values and the list of known analogs |

## Use of AI

The idea and scope are the team's own. We used Claude (Anthropic) to research background, help write and debug code, and polish documentation. Details in [`USO_DE_IA_Y_FUENTES.md`](USO_DE_IA_Y_FUENTES.md).
