"""
Esquemas Pydantic de la API. Replican exactamente los formatos de
contrato/schema.json.
"""
"""
Esquemas Pydantic de la API. Extensión aditiva sobre contrato/schema.json:
- InterpretarOut ahora puede devolver una pregunta aclaratoria con opciones (CU-01).
- BuscarOut ahora reporta el total de celdas que pasan los filtros (contador de la UI).
Ningún campo obligatorio cambia; los clientes antiguos siguen funcionando.
"""

from typing import Dict, List, Optional
from pydantic import BaseModel, Field


class InterpretarOut(BaseModel):
    sitio: str
    pesos: Dict[str, float]
    imprescindibles: List[str] = []
    descubrimiento: bool = False
    resumen: str
    # Nuevo (opcional): cuando el texto es ambiguo, la IA pregunta en vez de adivinar.
    pregunta: Optional[str] = None
    opciones: List[str] = []


class BuscarOut(BaseModel):
    sitio: str
    tierra_no_llega: List[str]
    lugares: List[dict]
    # Nuevo (opcional): total de celdas que superan el umbral, para el contador "N matches".
    total_match: int = 0
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
