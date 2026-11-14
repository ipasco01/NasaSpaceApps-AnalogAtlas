"""
Carga de los artefactos de datos del repo.
"""

import logging
import pandas as pd

from config.settings import ruta_celdas, REFERENCIAS_FILE, ANALOGOS_CONOCIDOS_FILE, COLUMNAS_CELDAS

logger = logging.getLogger(__name__)


def cargar_celdas() -> pd.DataFrame:
    """Lee la tabla de la Tierra (Parquet) y valida sus columnas."""
    ruta = ruta_celdas()
    if not ruta.exists():
        raise FileNotFoundError(f"No existe la tabla de celdas en {ruta}")
    celdas = pd.read_parquet(ruta)
    faltan = set(COLUMNAS_CELDAS) - set(celdas.columns)
    if faltan:
        raise ValueError(f"Columnas faltantes en {ruta.name}: {sorted(faltan)}")
    logger.info("Celdas cargadas desde %s (%d filas)", ruta.name, len(celdas))
    return celdas


def cargar_referencias() -> pd.DataFrame:
    return pd.read_csv(REFERENCIAS_FILE)


def cargar_analogos_conocidos() -> pd.DataFrame:
    return pd.read_csv(ANALOGOS_CONOCIDOS_FILE)


def lista_referencias() -> list:
    """Sitios disponibles con su cuerpo, para el selector del frontend."""
    refs = cargar_referencias()
    return refs[["sitio", "cuerpo", "lat", "lon"]].to_dict(orient="records")
