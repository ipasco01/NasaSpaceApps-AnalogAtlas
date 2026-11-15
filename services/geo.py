# Analog Atlas · services/geo.py
# v0.1 · 2026-11-14 · Isabelita (equipo Ctrl Z)
# Geografía para la app: país de cada celda (Natural Earth 1:50m, dominio público) e imagen satelital
# de la Tierra a la misma escala que la referencia de Marte o la Luna (Sentinel-2 cloudless 2021, EOX).

import json
import math
import urllib.request
from functools import lru_cache

import numpy as np
from matplotlib.path import Path as Trazo

from config.settings import DATA_DIR

PAISES_GEOJSON = DATA_DIR / "geo" / "paises_50m.geojson"
EOX_WMS = ("https://tiles.maps.eox.at/wms?SERVICE=WMS&VERSION=1.1.1&REQUEST=GetMap"
           "&LAYERS=s2cloudless-2021&SRS=EPSG:4326&FORMAT=image/jpeg")


@lru_cache(maxsize=1)
def _paises() -> list:
    """Lista de (nombre, continente, caja, [trazos]) para cada país."""
    datos = json.loads(PAISES_GEOJSON.read_text(encoding="utf-8"))
    salida = []
    for f in datos["features"]:
        geo, prop = f["geometry"], f["properties"]
        poligonos = geo["coordinates"] if geo["type"] == "MultiPolygon" else [geo["coordinates"]]
        trazos = [Trazo(np.asarray(p[0])) for p in poligonos]
        todos = np.vstack([t.vertices for t in trazos])
        caja = (todos[:, 0].min(), todos[:, 1].min(), todos[:, 0].max(), todos[:, 1].max())
        salida.append((prop["NAME"], prop["CONTINENT"], caja, trazos))
    return salida


def pais_de(lats: np.ndarray, lons: np.ndarray, margen_grados: float = 0.5) -> np.ndarray:
    """Nombre del país de cada punto. Celdas de costa que caen fuera del contorno 1:50m se asignan
    al país cuyo contorno está a menos de `margen_grados`; si no hay ninguno, 'Open area'."""
    lats, lons = np.asarray(lats, float), np.asarray(lons, float)
    nombres = np.full(len(lats), "", dtype=object)
    puntos = np.column_stack([lons, lats])
    for nombre, _, (x0, y0, x1, y1), trazos in _paises():
        en_caja = (lons >= x0 - margen_grados) & (lons <= x1 + margen_grados) & \
                  (lats >= y0 - margen_grados) & (lats <= y1 + margen_grados) & (nombres == "")
        if not en_caja.any():
            continue
        idx = np.where(en_caja)[0]
        dentro = np.zeros(len(idx), bool)
        for t in trazos:
            dentro |= t.contains_points(puntos[idx], radius=margen_grados)
        nombres[idx[dentro]] = nombre
    # Segundo intento con más margen (zonas en disputa o islas que el contorno deja fuera)
    if (nombres == "").any() and margen_grados < 2.0:
        faltan = np.where(nombres == "")[0]
        nombres[faltan] = pais_de(lats[faltan], lons[faltan], margen_grados=2.0)
    nombres[nombres == ""] = "Open area"
    return nombres


def ancho_vista_km(cuerpo: str) -> int:
    """Ancho real de las imágenes de referencia: Marte (Viking) 120 km, Luna (LRO WAC) 60 km."""
    return 120 if cuerpo == "marte" else 60


def imagen_tierra(lat: float, lon: float, ancho_km: int, ancho_px: int = 480, alto_px: int = 360) -> bytes:
    """JPEG de Sentinel-2 cloudless centrado en el punto, con el ancho real pedido."""
    dlon = ancho_km / (111.32 * max(math.cos(math.radians(lat)), 0.05))
    dlat = ancho_km * alto_px / ancho_px / 111.2
    url = (f"{EOX_WMS}&BBOX={lon - dlon / 2},{lat - dlat / 2},{lon + dlon / 2},{lat + dlat / 2}"
           f"&WIDTH={ancho_px}&HEIGHT={alto_px}")
    req = urllib.request.Request(url, headers={"User-Agent": "analog-atlas/0.1"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read()
