# Atlas Analog · tif_a_tabla.py
# v0.4 · 2026-11-14 · Isabelita (equipo Ctrl Z)
# Convierte el GeoTIFF exportado de Earth Engine en una tabla con una fila por celda de tierra firme.
# La pendiente se calcula aquí, desde la elevación de la cuadrícula de 0,25°, con la misma fórmula que
# planetas.py usa para la Luna y Marte: así las tres pendientes son comparables.
# Uso: python tif_a_tabla.py ../datos/celdas.parquet clima.tif [temperatura.tif nieve.tif relieve.tif]

import sys

import numpy as np
import pandas as pd
import rasterio

RADIO_TIERRA_KM = 6371.0
ELEVACION_MINIMA_TIERRA = -450.0  # m; por debajo es fondo marino mezclado en celdas de costa
LAT_SOLO_NORTE_SUR = 80.0         # misma regla que planetas.py para la Luna y Marte


def pendiente_grados(elevacion_m: np.ndarray, transform) -> np.ndarray:
    """Pendiente (°) en una cuadrícula lat/lon regular. Igual método que planetas.py."""
    paso_lon, paso_lat = transform.a, -transform.e
    filas = np.arange(elevacion_m.shape[0])
    lat = transform.f - (filas + 0.5) * paso_lat
    dy = np.radians(paso_lat) * RADIO_TIERRA_KM * 1000
    dx = np.radians(paso_lon) * RADIO_TIERRA_KM * 1000 * np.maximum(np.cos(np.radians(lat)), 1e-3)[:, None]
    dz_dy = np.gradient(elevacion_m, axis=0) / dy
    dz_dx = np.gradient(elevacion_m, axis=1) / dx
    # Cerca del polo las celdas se angostan de este a oeste y dz_dx se dispara (daba hasta 82°).
    # Sobre LAT_SOLO_NORTE_SUR solo se usa la componente norte-sur: un mínimo de la pendiente real.
    polar = (np.abs(lat) > LAT_SOLO_NORTE_SUR)[:, None]
    dz_dx = np.where(polar, 0.0, dz_dx)
    return np.degrees(np.arctan(np.hypot(dz_dx, dz_dy)))


def leer_tif(ruta_tif: str) -> pd.DataFrame:
    """Tabla con una fila por píxel. Si trae elevación, agrega la pendiente."""
    with rasterio.open(ruta_tif) as src:
        datos = src.read(masked=True)
        nombres = list(src.descriptions)
        if not all(nombres):
            raise ValueError(f"{ruta_tif} no trae nombres de banda; revisa la exportación de Earth Engine")
        transform = src.transform
        filas, cols = np.indices((src.height, src.width))
        lon, lat = rasterio.transform.xy(transform, filas.ravel(), cols.ravel())
    tabla = pd.DataFrame({n: datos[i].filled(np.nan).ravel() for i, n in enumerate(nombres)})
    if "elevacion" in nombres and "pendiente" not in nombres:
        elev = datos[nombres.index("elevacion")].filled(np.nan)
        # En celdas de costa ETOPO1 mezcla fondo marino (llegaba a -6108 m). La tierra firme más baja es la orilla
        # del Mar Muerto (~-430 m), así que todo valor menor a -450 m se descarta antes de calcular la pendiente.
        elev = np.where(elev < ELEVACION_MINIMA_TIERRA, np.nan, elev)
        tabla["elevacion"] = elev.ravel()
        # Para la pendiente, el mar (celdas vacías) cuenta como nivel del mar (0 m); si no, toda celda de
        # costa quedaría sin pendiente.
        tabla["pendiente"] = np.where(np.isnan(elev), np.nan,
                                      pendiente_grados(np.nan_to_num(elev, nan=0.0), transform)).ravel()
    # Clave de unión: centro de celda redondeado (las dos exportaciones usan la misma cuadrícula de 0,25°)
    tabla["lon"], tabla["lat"] = np.round(np.asarray(lon), 3), np.round(np.asarray(lat), 3)
    return tabla


def convertir(rutas_tif: list[str], ruta_salida: str) -> pd.DataFrame:
    """Junta exportaciones de la misma cuadrícula de 0,25°.
    Archivos con las mismas columnas (franjas de un mismo grupo) se apilan como filas;
    grupos con columnas distintas se unen por lat/lon. La columna ndvi marca la tierra firme."""
    grupos: dict[frozenset, list[pd.DataFrame]] = {}
    for ruta in rutas_tif:
        t = leer_tif(ruta)
        grupos.setdefault(frozenset(t.columns), []).append(t)
    tablas = [pd.concat(partes, ignore_index=True).drop_duplicates(["lat", "lon"]) for partes in grupos.values()]
    # La tierra firme la marca "arido" (MCD12C1, cubre todo el planeta). El NDVI de MODIS no cubre la
    # Antártida, así que no sirve como máscara.
    tablas.sort(key=lambda t: "arido" not in t.columns)
    tabla = tablas[0]
    if "arido" not in tabla.columns:
        raise ValueError("Falta el archivo arido_hielo (la máscara de tierra firme)")
    for otra in tablas[1:]:
        repetidas = (set(otra.columns) & set(tabla.columns)) - {"lat", "lon"}
        if repetidas:
            raise ValueError(f"Dos grupos traen las mismas columnas: {', '.join(sorted(repetidas))}")
        tabla = tabla.merge(otra, on=["lat", "lon"], how="left")
    tabla = tabla.dropna(subset=["arido"])  # solo tierra firme
    if "ndvi" in tabla.columns and "hielo" in tabla.columns:
        # Sobre hielo permanente no hay vegetación: NDVI faltante se pone en 0 y queda marcado
        relleno = tabla["ndvi"].isna() & (tabla["hielo"] >= 0.5)
        tabla.loc[relleno, "ndvi"] = 0.0
        tabla["ndvi_relleno"] = relleno
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


ESPERADAS = ["temp_dia", "temp_noche", "rango_termico", "permafrost_proxy", "lluvia", "ndvi", "arido",
             "hielo", "nieve", "polvo", "elevacion", "pendiente"]

if __name__ == "__main__":
    if len(sys.argv) < 3:
        sys.exit("Uso: python tif_a_tabla.py salida.parquet clima.tif [temperatura.tif nieve.tif relieve.tif ...]")
    t = convertir(sys.argv[2:], sys.argv[1])
    faltan = [c for c in ESPERADAS if c not in t.columns or t[c].isna().all()]
    if faltan:
        print("Aviso: faltan columnas (el motor las ignora hasta que lleguen):", ", ".join(faltan))
    print(f"{len(t)} celdas · columnas: {', '.join(t.columns)}")
    print(t.describe().T[["min", "50%", "max"]].round(2).to_string())
    revisar_cobertura(t)
    print("Cobertura OK: hay hemisferio oeste y latitudes altas")
