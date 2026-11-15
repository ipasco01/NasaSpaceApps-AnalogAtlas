"""
Endpoint POST /api/buscar para búsqueda de análogos terrestres.
"""

import logging
from typing import List

from fastapi import APIRouter, HTTPException

from api.schemas import BuscarRequest, BuscarResponse, LugarResponse
from api.state import motor_service
from config.settings import TRAMOS

logger = logging.getLogger(__name__)
router = APIRouter()

# Si el texto es muy corto o ambiguo (heurística: < 6 palabras o sin cuerpo detectado),
# devolver pregunta + opciones en vez de forzar un sitio. El frontend muestra los chips.
if len(req.texto.split()) < 6 or _detectar_sitio(req.texto) is None:
    return InterpretarOut(
        sitio="jezero",
        pesos=PESOS_BASE["marte"],
        imprescindibles=[],
        descubrimiento=False,
        resumen="Necesito un detalle para afinar la búsqueda.",
        pregunta="What slope range and surface roughness are you targeting?",
        opciones=[
            "Gentle (0-15 deg) and moderate roughness",
            "Moderate (15-30 deg) and high roughness",
            "Steep (30-45 deg) and very high roughness",
        ],
    )
def clasificar_tramo(puntaje: float) -> str:
    """Clasifica el puntaje en tramos descriptivos según el contrato."""
    for lo, hi, nombre in TRAMOS:
        if lo <= puntaje <= hi:
            return nombre
    return "Débil"


@router.post("/buscar", response_model=BuscarResponse)
def buscar(req: BuscarRequest):
    """
    Busca análogos terrestres para un sitio de referencia de la Luna o Marte.
    
    Args:
        req: Criterios de búsqueda incluyendo sitio, pesos y filtros.
    
    Returns:
        BuscarResponse: Lista de lugares análogos ordenados por puntaje.
    
    Raises:
        HTTPException: Si el sitio no existe o hay error en el cálculo.
    """
    try:
        if motor_service is None:
            raise HTTPException(status_code=503, detail="Servicio no inicializado")
        
        # Ejecutar búsqueda
        lugares, tierra_no_llega = motor_service.buscar(
            sitio=req.sitio,
            pesos=req.pesos,
            imprescindibles=req.imprescindibles,
            descubrimiento=req.descubrimiento,
            top=req.top,
        )
        
        return BuscarResponse(
            sitio=req.sitio,
            tierra_no_llega=tierra_no_llega,
            lugares=lugares,
        )
        
    except ValueError as e:
        logger.error("Error de validación en búsqueda: %s", str(e))
        raise HTTPException(status_code=400, detail=str(e)) from e
    except Exception as e:
        logger.error("Error inesperado en búsqueda: %s", str(e), exc_info=True)
        raise HTTPException(status_code=500, detail="Error interno del servidor")
