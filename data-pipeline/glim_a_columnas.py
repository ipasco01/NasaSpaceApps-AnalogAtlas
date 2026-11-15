# Atlas Analog · glim_a_columnas.py
# v0.2 · 2026-11-15 · Isabelita (equipo Ctrl Z) · suma sales (evaporitas) y carbonatos
# Agrega a celdas.parquet el tipo de roca de la superficie desde GLiM (Hartmann & Moosdorf 2012, grilla de 0,5°,
# PANGAEA doi:10.1594/PANGAEA.788537, licencia CC BY 3.0). Columnas de sí o no (0/1):
#   volcanico = clases "vb", "vi", "py" (basaltos, andesitas y piroclastos: campos de lava; sin riolitas "va")
#   sedimento = clases "su", "ss", "sm" (sedimentos sueltos, siliciclásticos y mixtos: dunas, lagos, deltas)
#   evaporita = clase "ev" (sales: salares y lagos secos, análogos de los sulfatos y cloruros de Marte)
#   carbonato = clase "sc" (calizas y dolomías; en Marte hay carbonatos en Jezero)
# Solo agrega las columnas que la tabla todavía no tiene.
# Cada celda de 0,25° toma el píxel de 0,5° que contiene su centro. Sin dato en GLiM -> vacío.
# Uso: python glim_a_columnas.py ../datos/celdas.parquet glim_wgs84_0point5deg.txt.asc Classnames.txt

import csv
import sys

import numpy as np
import pandas as pd
import rasterio

CLASES = {"volcanico": {"vb", "vi", "py"}, "sedimento": {"su", "ss", "sm"}, "evaporita": {"ev"}, "carbonato": {"sc"}}
COBERTURA_MINIMA = 0.95


def leer_clases(ruta_nombres: str) -> dict:
    with open(ruta_nombres, encoding="utf-8") as f:
        return {int(fila["Value_"]): fila["xx"] for fila in csv.DictReader(f, delimiter=";")}


def agregar(ruta_tabla: str, ruta_asc: str, ruta_nombres: str) -> pd.DataFrame:
    tabla = pd.read_parquet(ruta_tabla)
    nuevas = {k: v for k, v in CLASES.items() if k not in tabla.columns}
    if not nuevas:
        raise ValueError("La tabla ya tiene todas las columnas de roca")
    clases = leer_clases(ruta_nombres)
    with rasterio.open(ruta_asc) as src:
        grilla, t, sin_dato = src.read(1), src.transform, src.nodata
    col = np.clip(np.floor((tabla["lon"].to_numpy() - t.c) / t.a).astype(int), 0, grilla.shape[1] - 1)
    fil = np.clip(np.floor((tabla["lat"].to_numpy() - t.f) / t.e).astype(int), 0, grilla.shape[0] - 1)
    codigo = grilla[fil, col]
    letras = np.array([clases.get(int(c), "") for c in codigo])
    con_dato = (codigo != sin_dato) & (letras != "nd") & (letras != "")
    cobertura = con_dato.mean()
    if cobertura < COBERTURA_MINIMA:
        raise SystemExit(f"Solo {cobertura:.1%} de las celdas tiene roca en GLiM (mínimo {COBERTURA_MINIMA:.0%})")
    for nombre, grupo in nuevas.items():
        tabla[nombre] = np.where(con_dato, np.isin(letras, list(grupo)).astype("float32"), np.nan).astype("float32")
        print(f"{nombre}: {np.nanmean(tabla[nombre]):.1%} de las celdas con dato ({cobertura:.1%} cubiertas)")
    tabla.to_parquet(ruta_tabla, index=False)
    return tabla


if __name__ == "__main__":
    if len(sys.argv) != 4:
        raise SystemExit("Uso: python glim_a_columnas.py ../datos/celdas.parquet glim.asc Classnames.txt")
    agregar(*sys.argv[1:])
