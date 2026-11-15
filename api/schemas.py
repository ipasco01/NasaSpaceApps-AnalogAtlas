# Atlas Analog · api/schemas.py
# v0.3 · 2026-11-14 · Isabelita (equipo Ctrl Z), une schemas.py y sschemas.py de asernaque03-lab
"""
Esquemas Pydantic de la API, según contrato/schema.json. Extensiones aditivas (ningún campo
obligatorio del contrato cambia):
- InterpretarOut puede traer una pregunta aclaratoria con opciones (CU-01).
- BuscarResponse trae total_match (contador "N matches") y cada lugar trae id y valores crudos.
- Referencia trae pesos_base; CeldaResponse trae el análogo conocido más cercano.
"""

from typing import Dict, List, Optional

from pydantic import BaseModel, Field


class BuscarRequest(BaseModel):
    sitio: str
    pesos: Dict[str, float]
    imprescindibles: List[str] = []
    descubrimiento: bool = False
    top: int = Field(10, ge=1, le=5000)


class LugarResponse(BaseModel):
    id: int
    lat: float
    lon: float
    puntaje: float
    tramo: str
    desglose: Dict[str, float]
    valores: Dict[str, float] = {}
    pais: str = ""
    puesto: int = 0   # 1 = el más parecido de toda la Tierra
    de: int = 0       # cuántas celdas de tierra se compararon


class BuscarResponse(BaseModel):
    sitio: str
    tierra_no_llega: List[str]
    lugares: List[LugarResponse]
    total_match: int = 0


class InterpretarRequest(BaseModel):
    texto: str = Field(min_length=1, max_length=500)


class InterpretarOut(BaseModel):
    sitio: str
    pesos: Dict[str, float]
    imprescindibles: List[str] = []
    descubrimiento: bool = False
    resumen: str
    pregunta: Optional[str] = None
    opciones: List[str] = []


class Referencia(BaseModel):
    sitio: str
    cuerpo: str
    lat: float
    lon: float
    valores: Dict[str, float]
    fuentes: Dict[str, str]
    pesos_base: Dict[str, float]


class AnalogoConocido(BaseModel):
    nombre: str
    lat: float
    lon: float
    nota: str = ""
    por_que: str = ""   # por qué es famoso, solo si hay fuente
    fuente: str = ""


class ValidacionDetalle(BaseModel):
    nombre: str
    top_pct: float      # mejor puesto en % de la Tierra (1 = está en el 1 % más parecido)
    sitio: str          # contra qué sitio logra ese puesto


class Validacion(BaseModel):
    total: int
    top10: int
    top20: int
    detalle: List[ValidacionDetalle]


class AnalogoCercano(BaseModel):
    nombre: str
    km: float


class CeldaResponse(LugarResponse):
    se_parece: List[str]
    falla: List[str]
    analogo_cercano: AnalogoCercano


class SensibilidadRequest(BaseModel):
    sitio: str
    pesos: Dict[str, float]
    n_top: int = Field(10, ge=1, le=100)


class SensibilidadResponse(BaseModel):
    retencion: float
