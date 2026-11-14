"""
Endpoint POST /api/buscar para búsqueda de análogos terrestres.
"""

import logging
from typing import List

from fastapi import APIRouter, HTTPException

from api.schemas import BuscarRequest, BuscarResponse, LugarResponse
from services.motor_service import MotorService

logger = logging.getLogger(__name__)
router = APIRouter()


def get_motor_service() -> MotorService:
    """Obtiene la instancia del servicio de motor desde el estado de la aplicación."""
    from api.main import motor_service
    return motor_service


def clasificar_tramo(puntaje: float) -> str:
    """Clasifica el puntaje en tramos descriptivos."""
    if puntaje >= 75:
        return "Muy buen análogo"
    elif puntaje >= 50:
        return "Bueno"
    elif puntaje >= 25:
        return "Parcial"
    else:
        return "Débil"


@router.post("/buscar", response_model=BuscarResponse)
async def buscar_analogos(request: BuscarRequest):
    """
    Busca análogos terrestres para un sitio de referencia de la Luna o Marte.
    
    Args:
        request: Criterios de búsqueda incluyendo sitio, pesos y filtros.
    
    Returns:
        BuscarResponse: Lista de lugares análogos ordenados por puntaje.
    
    Raises:
        HTTPException: Si el sitio no existe o hay error en el cálculo.
    """
    try:
        motor = get_motor_service()
        
        # Ejecutar búsqueda
        resultado, tierra_no_llega = motor.puntuar(
            sitio=request.sitio,
            pesos=request.pesos,
            imprescindibles=request.imprescindibles,
            descubrimiento=request.descubrimiento,
            top=request.top * 2,  # Obtener más para filtrar
        )
        
        # Construir respuesta
        lugares = []
        for _, row in resultado.head(request.top).iterrows():
            desglose = {
                col.replace("s_", ""): float(row[col])
                for col in row.index
                if col.startswith("s_")
            }
            
            lugares.append(LugarResponse(
                lat=float(row["lat"]),
                lon=float(row["lon"]),
                puntaje=float(row["puntaje"]),
                tramo=clasificar_tramo(row["puntaje"]),
                desglose=desglose,
            ))
        
        return BuscarResponse(
            sitio=request.sitio,
            tierra_no_llega=tierra_no_llega,
            lugares=lugares,
        )
        
    except ValueError as e:
        logger.error("Error de validación en búsqueda: %s", str(e))
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error("Error inesperado en búsqueda: %s", str(e), exc_info=True)
        raise HTTPException(status_code=500, detail="Error interno del servidor")