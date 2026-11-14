# Atlas Analog · diviner.py
# v0.2 · 2026-11-14 · Isabelita (equipo Ctrl Z)
# Saca temperaturas de la Luna de los productos derivados de Diviner (LRO, PDS Geosciences) y las escribe
# en science/referencias.csv. Baja solo las filas necesarias (pedidos por rango de bytes): las tablas
# completas pesan 156 MB y 605 MB.
#   - Marius Hills: tabla global acumulada (GCP), franja 10-20° N. Temperatura bolométrica en cada una de
#     las 96 horas locales de su celda de 0,5°: máximo del día y mínimo de la noche.
#   - Shackleton: producto polar sur (PRP), cuadrícula de 1200 x 1200 celdas de ~0,507 km centrada en el
#     polo, 2 triángulos por celda. Temperatura media y máxima y profundidad del hielo estable en el borde
#     (9,5 a 12 km del centro) y en el fondo (menos de 5 km).
# Uso: python diviner.py

import math
import urllib.request
from pathlib import Path

import numpy as np
import pandas as pd

RAIZ = Path(__file__).resolve().parent.parent
CARPETA = RAIZ / "datos" / "planetas" / "diviner"
REFERENCIAS = RAIZ / "science" / "referencias.csv"
BASE = "https://pds-geosciences.wustl.edu/lro/urn-nasa-pds-lro_diviner_derived1"
URL_GCP = f"{BASE}/data_derived_gcp/global_cumul_avg_cyl_10n20n_002.tab"
URL_PRP = f"{BASE}/data_derived_prp/dlre_prp_south.tab"
RADIO_LUNA_KM = 1737.4
SHACKLETON_CENTRO = (-89.67, 129.78)

# Formato de las tablas (etiquetas .lbl y .xml del PDS). Posiciones de columna en base 0.
GCP_FILA_BYTES, GCP_HORAS, GCP_LATS = 113, 96, 20
PRP_FILA_BYTES, PRP_N, PRP_PASO_KM = 210, 1200, 0.507
COLS_GCP = {"lon": (0, 7), "lat": (9, 15), "hora": (17, 23), "tbol": (102, 111)}
COLS_PRP = {"lon": (126, 141), "lat": (143, 158), "temp_avg": (177, 185), "temp_max": (187, 195),
            "ice_depth": (197, 208)}
FALTANTE = -900  # el PDS marca los vacíos con -999 o -9999


def pedir_bytes(url: str, ini: int, fin: int) -> bytes:
    req = urllib.request.Request(url, headers={"Range": f"bytes={ini}-{fin}", "User-Agent": "hackathon-prototype/0.1"})
    with urllib.request.urlopen(req, timeout=60) as r:
        if r.status != 206:
            raise RuntimeError(f"El servidor no aceptó el pedido parcial ({r.status})")
        return r.read()


def bajar_celda_gcp(lat: float, lon: float, destino: Path) -> None:
    ilon = round((lon + 179.75) / 0.5)
    ilat = round((lat - 10.25) / 0.5)
    fila = ilon * GCP_LATS * GCP_HORAS + ilat * GCP_HORAS
    ini = GCP_FILA_BYTES * (1 + fila)  # +1 por la fila de encabezado
    destino.write_bytes(pedir_bytes(URL_GCP, ini, ini + GCP_FILA_BYTES * GCP_HORAS - 1))


def bajar_zona_prp(lat: float, lon: float, mitad_celdas: int, destino: Path) -> None:
    r = RADIO_LUNA_KM * math.radians(90 + lat)
    x, y = r * math.cos(math.radians(lon)), r * math.sin(math.radians(lon))
    ix0, iy0 = round(PRP_N / 2 - x / PRP_PASO_KM), round(PRP_N / 2 + y / PRP_PASO_KM)
    partes = []
    for ix in range(ix0 - mitad_celdas, ix0 + mitad_celdas + 1):
        ini = PRP_FILA_BYTES * (1 + (ix * PRP_N + iy0 - mitad_celdas) * 2)
        fin = PRP_FILA_BYTES * (1 + (ix * PRP_N + iy0 + mitad_celdas + 1) * 2) - 1
        partes.append(pedir_bytes(URL_PRP, ini, fin))
    destino.write_bytes(b"".join(partes))


def leer_tabla(ruta: Path, columnas: dict) -> pd.DataFrame:
    tabla = pd.read_fwf(ruta, colspecs=list(columnas.values()), names=list(columnas), dtype=str)
    return tabla.apply(pd.to_numeric, errors="coerce").dropna()


def distancia_km(lat1, lon1, lat2, lon2):
    lat1, lon1, lat2, lon2 = map(np.radians, (lat1, lon1, lat2, lon2))
    a = np.sin((lat2 - lat1) / 2) ** 2 + np.cos(lat1) * np.cos(lat2) * np.sin((lon2 - lon1) / 2) ** 2
    return 2 * RADIO_LUNA_KM * np.arcsin(np.sqrt(a))


def ciclo_marius(ruta: Path) -> tuple[float, float, int]:
    t = leer_tabla(ruta, COLS_GCP)
    t = t[t["tbol"] > 0]
    if len(t) < 24:
        raise ValueError(f"Muy pocas horas con dato en Marius Hills: {len(t)}")
    return float(t["tbol"].max()), float(t["tbol"].min()), len(t)


def resumen_shackleton(ruta: Path) -> dict:
    t = leer_tabla(ruta, COLS_PRP)
    t = t[t["temp_max"] > 0].copy()
    # ice_depth: 0 = hielo estable en la superficie; -999 = más hondo que 2,87 m (sin hielo cercano).
    # -1 no está documentado; aparece donde la máxima anual es < ~110 K (trampas frías), así que se toma como 0.
    t["ice_depth"] = t["ice_depth"].replace(-1, 0)
    km = distancia_km(t["lat"], t["lon"], *SHACKLETON_CENTRO)
    borde, fondo = t[(km >= 9.5) & (km <= 12)], t[km < 5]
    if borde.empty or fondo.empty:
        raise ValueError("No hay triángulos de Diviner en el borde o en el fondo de Shackleton")
    hielo = lambda d: float(d.loc[d["ice_depth"] > FALTANTE, "ice_depth"].median()) if (d["ice_depth"] > FALTANTE).any() else float("nan")
    return {"borde_max": float(borde["temp_max"].median()), "borde_media": float(borde["temp_avg"].median()),
            "fondo_max": float(fondo["temp_max"].median()), "fondo_media": float(fondo["temp_avg"].median()),
            "borde_hielo_m": hielo(borde), "fondo_hielo_m": hielo(fondo),
            "borde_con_hielo": float((borde["ice_depth"] > FALTANTE).mean()),
            "n_borde": len(borde), "n_fondo": len(fondo)}


def main() -> None:
    CARPETA.mkdir(parents=True, exist_ok=True)
    refs = pd.read_csv(REFERENCIAS, dtype={"fuente_temperatura": "string", "notas": "string"})
    k_a_c = lambda k: round(k - 273.15, 1)

    i = refs.index[refs["sitio"] == "marius_hills"][0]
    ruta_m = CARPETA / "marius_96h.tab"
    if not ruta_m.exists():
        bajar_celda_gcp(refs.at[i, "lat"], refs.at[i, "lon"], ruta_m)
    tmax, tmin, horas = ciclo_marius(ruta_m)
    refs.loc[i, ["temp_dia", "temp_noche", "rango_termico"]] = [k_a_c(tmax), k_a_c(tmin), round(tmax - tmin, 1)]
    refs.at[i, "fuente_temperatura"] = (f"Diviner GCP (LRO, PDS Geosciences), global_cumul_avg_cyl_10n20n_002: "
                                        f"temperatura bolométrica, máximo y mínimo de {horas} horas locales con dato "
                                        f"en la celda de 0,5° (14,25° N, 56,75° O)")
    print(f"Marius Hills: máx {tmax:.1f} K ({k_a_c(tmax)} °C), mín {tmin:.1f} K ({k_a_c(tmin)} °C), {horas} horas")

    ruta_s = CARPETA / "shackleton_zona.tab"
    if not ruta_s.exists():
        bajar_zona_prp(*SHACKLETON_CENTRO, mitad_celdas=27, destino=ruta_s)
    s = resumen_shackleton(ruta_s)
    j = refs.index[refs["sitio"] == "shackleton"][0]
    refs.loc[j, ["lat", "lon"]] = SHACKLETON_CENTRO
    refs.loc[j, "temp_dia"] = k_a_c(s["borde_max"])
    refs.at[j, "fuente_temperatura"] = (
        f"Diviner PRP sur (LRO, PDS Geosciences): borde (9,5-12 km del centro, {s['n_borde']} triángulos) "
        f"máx {s['borde_max']:.0f} K, media {s['borde_media']:.0f} K; fondo (<5 km, {s['n_fondo']} triángulos) "
        f"máx {s['fondo_max']:.0f} K, media {s['fondo_media']:.0f} K. El producto no trae mínimo: temp_noche vacía")
    refs.at[j, "notas"] = (f"Valores del borde. Hielo estable en el {s['borde_con_hielo']:.0%} del borde "
                           f"(mediana {s['borde_hielo_m']:.2f} m) y en el fondo a {s['fondo_hielo_m']:.2f} m (Diviner PRP)")
    print("Shackleton:", {k: round(v, 3) for k, v in s.items()})
    refs.to_csv(REFERENCIAS, index=False)


if __name__ == "__main__":
    main()
