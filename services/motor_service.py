"""
Servicio de negocio que delega el cálculo en el motor validado del equipo
(backend/motor.py). No duplica la lógica de similitud.
"""

import logging
from typing import Dict, List, Tuple

import numpy as np
import pandas as pd

from config.settings import PESOS_BASE, TRAMOS
from backend.motor import (
    cargar_referencia,
    puntuar,
    lejos_de_conocidos,
    sensibilidad,
)

logger = logging.getLogger(__name__)


class MotorService:
    """Fachada de alto nivel sobre backend/motor.py para la capa de API."""

    def __init__(self, celdas: pd.DataFrame) -> None:
        self.celdas = celdas
        logger.info("MotorService listo con %d celdas en memoria", len(celdas))

    def buscar(
        self,
        sitio: str,
        pesos: Dict[str, float],
        imprescindibles: List[str],
        descubrimiento: bool,
        top: int,
    ) -> Tuple[List[dict], List[str]]:
        """Calcula el Top N de análogos terrestres para un sitio de referencia."""
        ref = cargar_referencia(sitio)
        salida, saturadas = puntuar(self.celdas, ref, pesos, tuple(imprescindibles))
        if descubrimiento:
            salida = salida[lejos_de_conocidos(salida)]
        top_df = salida.nlargest(top, "puntaje")
        lugares = [self._fila_a_lugar(row) for _, row in top_df.iterrows()]
        return lugares, saturadas

    @staticmethod
    def _fila_a_lugar(row: pd.Series) -> dict:
        desglose = {c[2:]: float(row[c]) for c in row.index if c.startswith("s_")}
        return {
            "lat": float(row["lat"]), "lon": float(row["lon"]),
            "puntaje": float(row["puntaje"]), "tramo": _clasificar_tramo(row["puntaje"]),
            "desglose": desglose,
        }


def _clasificar_tramo(puntaje: float) -> str:
    for lo, hi, nombre in TRAMOS:
        if lo <= puntaje <= hi:
            return nombre
    return "Débil"
