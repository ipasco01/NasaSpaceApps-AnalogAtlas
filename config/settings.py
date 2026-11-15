"""
Configuración centralizada de Atlas Analog (equipo Ctrl Z).
"""

import os
from pathlib import Path
from typing import Dict, List


PROJECT_ROOT = Path(__file__).resolve().parent.parent

DATA_DIR = PROJECT_ROOT / "datos"
SCIENCE_DIR = PROJECT_ROOT / "science"
BACKEND_DIR = PROJECT_ROOT / "backend"

CELDS_REAL = DATA_DIR / "celdas.parquet"
CELDS_PRUEBA = DATA_DIR / "celdas_PRUEBA_no_reales.parquet"
REFERENCIAS_FILE = SCIENCE_DIR / "referencias.csv"
ANALOGOS_CONOCIDOS_FILE = SCIENCE_DIR / "analogos_conocidos.csv"


def ruta_celdas() -> Path:
    """Tabla real si existe; si no, la de prueba. Usar usa_datos_prueba() para avisar en pantalla."""
    if CELDS_REAL.exists():
        return CELDS_REAL
    return CELDS_PRUEBA


def usa_datos_prueba() -> bool:
    """True si la app está usando valores inventados (nunca deben llegar a la demo sin aviso)."""
    return ruta_celdas() == CELDS_PRUEBA


# Sin estas no se puede calcular nada; las demás columnas pueden faltar (el motor las ignora).
COLUMNAS_OBLIGATORIAS: List[str] = ["lat", "lon", "arido"]


COLUMNAS_CELDAS: List[str] = [
    "lat", "lon", "elevacion", "pendiente", "temp_dia", "temp_noche",
    "rango_termico", "lluvia", "ndvi", "arido", "nieve", "hielo",
    "permafrost_proxy", "polvo", "volcanico", "sedimento",
]

# Igual que backend/motor.py PESOS_BASE (v0.3). Si cambian allá, cambiar aquí.
PESOS_BASE: Dict[str, Dict[str, float]] = {
    "marte": {
        "lluvia": 0.15, "ndvi": 0.15, "arido": 0.15, "rango_termico": 0.15,
        "temp_noche": 0.10, "temp_dia": 0.10, "pendiente": 0.10, "polvo": 0.10,
        "volcanico": 0.10, "sedimento": 0.10,
    },
    "luna": {
        "lluvia": 0.10, "ndvi": 0.10, "arido": 0.10, "rango_termico": 0.15,
        "temp_noche": 0.15, "temp_dia": 0.15, "pendiente": 0.10, "hielo": 0.05,
        "permafrost_proxy": 0.10, "volcanico": 0.10, "sedimento": 0.10,
    },
}

TRAMOS = [(75, 100, "Muy buen análogo"), (50, 74, "Bueno"),
          (25, 49, "Parcial"), (0, 24, "Débil")]

# Solo esta computadora por defecto (mínimo privilegio). Para exponerla en la red: ATLAS_API_HOST=0.0.0.0
API_HOST = os.getenv("ATLAS_API_HOST", "127.0.0.1")
API_PORT = 8000
