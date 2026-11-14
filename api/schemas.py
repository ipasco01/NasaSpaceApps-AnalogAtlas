"""
Esquemas Pydantic para la API REST.
Define los modelos de entrada y salida de los endpoints.
"""

from typing import Dict, List, Optional
from pydantic import BaseModel, Field


class ReferenciaResponse(BaseModel):
    """Respuesta del endpoint GET /api/referencias."""
    sitio: str
    cuerpo: str
    lat: float
    lon: float
    valores: Dict[str, Optional[float]]
    fuentes: Dict[str, Optional[str]]


class InterpretarRequest(BaseModel):
    """Petición del endpoint POST /api/interpretar."""
    texto: str = Field(..., description="Descripción en lenguaje natural de la búsqueda")


class InterpretarResponse(BaseModel):
    """Respuesta del endpoint POST /api/interpretar."""
    sitio: str
    pesos: Dict[str, float]
    imprescindibles: List[str]
    descubrimiento: bool
    resumen: str


class BuscarRequest(BaseModel):
    """Petición del endpoint POST /api/buscar."""
    sitio: str
    pesos: Dict[str, float]
    imprescindibles: List[str] = []
    descubrimiento: bool = False
    top: int = 10


class LugarResponse(BaseModel):
    """Representa un lugar análogo en la respuesta de búsqueda."""
    lat: float
    lon: float
    puntaje: float
    tramo: str
    desglose: Dict[str, float]


class BuscarResponse(BaseModel):
    """Respuesta del endpoint POST /api/buscar."""
    sitio: str
    tierra_no_llega: List[str]
    lugares: List[LugarResponse]


class CeldaDetalleResponse(BaseModel):
    """Respuesta del endpoint GET /api/celda."""
    lat: float
    lon: float
    valores: Dict[str, Optional[float]]
    puntaje: float
    desglose: Dict[str, float]
    se_parece: List[str]
    falla: List[str]