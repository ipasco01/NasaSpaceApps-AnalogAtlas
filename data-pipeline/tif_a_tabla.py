# Atlas Analog · tif_a_tabla.py
# v0.2 · 2026-11-14 · Isabelita (equipo Ctrl Z)
# Convierte el GeoTIFF exportado de Earth Engine en una tabla con una fila por celda de tierra firme.
# La pendiente se calcula aquí, desde la elevación de la cuadrícula de 0,25°, con la misma fórmula que
# planetas.py usa para la Luna y Marte: así las tres pendientes son comparables.
# Uso: python tif_a_tabla.py atlas_analog_global_025_v3.tif ../datos/celdas.parquet

import sys

import numpy as np
import pandas as pd
import rasterio

RADIO_TIERRA_KM = 6371.0


def pendiente_grados(elevacion_m: np.ndarray, transform) -> np.ndarray:
    """Pendiente (°) en una cuadrícula lat/lon regular. Igual método que planetas.py."""
    paso_lon, paso_lat = transform.a, -transform.e
    filas = np.arange(elevacion_m.shape[0])
    lat = transform.f - (filas + 0.5) * paso_lat
    dy = np.radians(paso_lat) * RADIO_TIERRA_KM * 1000
    dx = np.radians(paso_lon) * RADIO_TIERRA_KM * 1000 * np.maximum(np.cos(np.radians(lat)), 1e-3)[:, None]
    dz_dy = np.gradient(elevacion_m, axis=0) / dy
    dz_dx = np.gradient(elevacion_m, axis=1) / dx
    return np.degrees(np.arctan(np.hypot(dz_dx, dz_dy)))


def convertir(ruta_tif: str, ruta_salida: str) -> pd.DataFrame:
    with rasterio.open(ruta_tif) as src:
        datos = src.read(masked=True)
        nombres = list(src.descriptions)
        if not all(nombres):
            raise ValueError("El GeoTIFF no trae nombres de banda; revisa la exportación de Earth Engine")
        transform = src.transform
        filas, cols = np.indices((src.height, src.width))
        lon, lat = rasterio.transform.xy(transform, filas.ravel(), cols.ravel())

    tabla = pd.DataFrame({n: datos[i].filled(np.nan).ravel() for i, n in enumerate(nombres)})
    if "pendiente" not in tabla.columns:
        elev = datos[nombres.index("elevacion")].filled(np.nan)
        tabla["pendiente"] = pendiente_grados(elev, transform).ravel()
    tabla["lon"], tabla["lat"] = np.asarray(lon), np.asarray(lat)
    tabla = tabla.dropna(subset=["temp_dia", "ndvi"])  # sin mar ni celdas vacías
    tabla.to_parquet(ruta_salida, index=False)
    return tabla


def revisar_cobertura(tabla: pd.DataFrame) -> None:
    """Falla rápido si la exportación vino incompleta, como pasó con v1 y v2."""
    problemas = []
    if (tabla["lon"] < 0).mean() < 0.2:
        problemas.append("casi no hay celdas en el hemisferio oeste")
    if tabla["lat"].max() < 70:
        problemas.append(f"la latitud máxima es {tabla['lat'].max():.1f}° (faltan Groenlandia y Siberia norte)")
    if problemas:
        raise SystemExit("Exportación incompleta: " + "; ".join(problemas))


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit("Uso: python tif_a_tabla.py entrada.tif salida.parquet")
    t = convertir(sys.argv[1], sys.argv[2])
    print(f"{len(t)} celdas · columnas: {', '.join(t.columns)}")
    print(t.describe().T[["min", "50%", "max"]].round(2).to_string())
    revisar_cobertura(t)
    print("Cobertura OK: hay hemisferio oeste y latitudes altas")
