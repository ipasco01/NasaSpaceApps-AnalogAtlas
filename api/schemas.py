"""
Esquemas Pydantic de la API. Replican exactamente los formatos de
contrato/schema.json.
"""

from typing import Dict, List, Optional
from pydantic import BaseModel, Field


class BuscarRequest(BaseModel):
    sitio: str
    pesos: Dict[str, float]
    imprescindibles: List[str] = []
    descubrimiento: bool = False
    top: int = 10


class LugarResponse(BaseModel):
    lat: float
    lon: float
    puntaje: float
    tramo: str
    desglose: Dict[str, float]


class BuscarResponse(BaseModel):
    sitio: str
    tierra_no_llega: List[str]
    lugares: List[LugarResponse]
