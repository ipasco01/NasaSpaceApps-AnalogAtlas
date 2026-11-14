"""
Esquemas de datos internos para el modelo de dominio.
Define las estructuras de datos que circulan entre capas.
"""

from dataclasses import dataclass
from typing import Dict, List, Optional


@dataclass
class CeldaData:
    """Representa una celda de la cuadrícula terrestre."""
    lat: float
    lon: float
    elevacion: Optional[float]
    pendiente: Optional[float]
    temp_dia: Optional[float]
    temp_noche: Optional[float]
    rango_termico: Optional[float]
    lluvia: Optional[float]
    ndvi: Optional[float]
    arido: Optional[int]
    nieve: Optional[float]
    hielo: Optional[int]
    permafrost_proxy: Optional[int]
    polvo: Optional[float]


@dataclass
class ReferenciaExtraterrestre:
    """Representa un sitio de referencia de la Luna o Marte."""
    sitio: str
    cuerpo: str
    lat: float
    lon: float
    pendiente: Optional[float]
    temp_dia: Optional[float]
    temp_noche: Optional[float]
    rango_termico: Optional[float]
    lluvia: Optional[float]
    ndvi: Optional[float]
    arido: Optional[int]
    nieve: Optional[float]
    hielo: Optional[int]
    permafrost_proxy: Optional[int]
    fuente_temperatura: Optional[str]
    fuente_pendiente: Optional[str]
    notas: Optional[str]


@dataclass
class ResultadoBusqueda:
    """Resultado de una búsqueda de análogos terrestres."""
    lat: float
    lon: float
    puntaje: float
    desglose: Dict[str, float]
    tramo: str


@dataclass
class CriteriosBusqueda:
    """Criterios para una búsqueda de análogos."""
    sitio: str
    pesos: Dict[str, float]
    imprescindibles: List[str]
    descubrimiento: bool
    top: int