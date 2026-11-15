# Atlas Analog · agregar_columna.py
# v0.1 · 2026-11-14 · Isabelita (equipo Ctrl Z)
# Agrega a celdas.parquet las bandas de un GeoTIFF de la misma cuadrícula de 0,25° (exportado de Earth Engine),
# sin rehacer toda la tabla. Cada celda toma el píxel que contiene su centro. Falla si la banda ya existe
# o si la cobertura sobre tierra firme es menor al 95 %.
# Uso: python agregar_columna.py ../datos/celdas.parquet atlas_analog_polvo_v12.tif

import sys

import numpy as np
import pandas as pd
import rasterio

COBERTURA_MINIMA = 0.95


def agregar(ruta_tabla: str, ruta_tif: str) -> pd.DataFrame:
    tabla = pd.read_parquet(ruta_tabla)
    with rasterio.open(ruta_tif) as src:
        nombres, datos, t = list(src.descriptions), src.read().astype(float), src.transform
    if not all(nombres):
        raise ValueError(f"{ruta_tif} no trae nombres de banda")
    repetidas = set(nombres) & set(tabla.columns)
    if repetidas:
        raise ValueError(f"La tabla ya tiene: {', '.join(sorted(repetidas))}")
    col = np.floor((tabla["lon"].to_numpy() - t.c) / t.a).astype(int)
    fil = np.floor((tabla["lat"].to_numpy() - t.f) / t.e).astype(int)
    dentro = (col >= 0) & (col < datos.shape[2]) & (fil >= 0) & (fil < datos.shape[1])
    for i, nombre in enumerate(nombres):
        valores = np.full(len(tabla), np.nan)
        valores[dentro] = datos[i, fil[dentro], col[dentro]]
        cobertura = np.isfinite(valores).mean()
        if cobertura < COBERTURA_MINIMA:
            raise SystemExit(f"{nombre}: solo {cobertura:.1%} de las celdas tiene dato (mínimo {COBERTURA_MINIMA:.0%})")
        tabla[nombre] = valores.astype("float32")
        print(f"{nombre}: {cobertura:.1%} de {len(tabla):,} celdas con dato · "
              f"p5 {np.nanpercentile(valores, 5):.3f} · mediana {np.nanmedian(valores):.3f} · p95 {np.nanpercentile(valores, 95):.3f}")
    tabla.to_parquet(ruta_tabla, index=False)
    return tabla


if __name__ == "__main__":
    if len(sys.argv) != 3:
        raise SystemExit("Uso: python agregar_columna.py ../datos/celdas.parquet archivo.tif")
    agregar(sys.argv[1], sys.argv[2])
