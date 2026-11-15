# Atlas Analog · api/routes/buscar.py
# v0.3 · 2026-11-14 · Isabelita (equipo Ctrl Z), sobre la v0.2 de asernaque03-lab
"""Endpoints del contrato: buscar, interpretar, referencias, celda y sensibilidad."""

import logging
from typing import List

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import JSONResponse

from api import state
from api.schemas import (AnalogoConocido, Validacion, BuscarRequest, BuscarResponse, CeldaResponse, InterpretarOut, InterpretarRequest,
                         Referencia, SensibilidadRequest, SensibilidadResponse)
from services.interpretar_service import interpretar as leer_texto

logger = logging.getLogger(__name__)
router = APIRouter()


def _con_errores(funcion, *args, **kwargs):
    """Sitio desconocido o dato inválido -> 400; cualquier otra falla -> 500 sin exponer detalles."""
    try:
        return funcion(*args, **kwargs)
    except HTTPException:
        raise
    except ValueError as e:
        logger.warning("Pedido inválido: %s", e)
        raise HTTPException(status_code=400, detail=str(e)) from e
    except Exception as e:
        logger.error("Error inesperado: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail="Error interno del servidor") from e


@router.post("/buscar", response_model=BuscarResponse)
def buscar(req: BuscarRequest):
    """Top N de análogos terrestres para un sitio de la Luna o Marte."""
    lugares, tierra_no_llega, total = _con_errores(state.servicio().buscar, sitio=req.sitio, pesos=req.pesos,
                                                   imprescindibles=req.imprescindibles,
                                                   descubrimiento=req.descubrimiento, top=req.top)
    # Respuesta directa: los 3000 lugares ya salen del servicio con la forma de BuscarResponse; validarlos otra vez
    # costaba ~2 s por búsqueda. El esquema sigue publicado en /docs.
    return JSONResponse({"sitio": req.sitio, "tierra_no_llega": tierra_no_llega, "lugares": lugares, "total_match": total})


@router.post("/interpretar", response_model=InterpretarOut)
def interpretar(req: InterpretarRequest):
    """Texto -> criterios. Por ahora por palabras clave; pregunta si el texto es ambiguo."""
    return _con_errores(leer_texto, req.texto)


@router.get("/referencias", response_model=List[Referencia])
def referencias():
    return _con_errores(state.servicio().referencias)


@router.get("/conocidos", response_model=List[AnalogoConocido])
def conocidos():
    """Análogos terrestres ya estudiados (los que oculta el modo descubrimiento)."""
    return state.servicio().conocidos_lista()


@router.get("/validacion", response_model=Validacion)
def validacion():
    """Cuántos análogos famosos quedan en el 10 % y el 20 % más parecido de la Tierra para algún sitio."""
    return _con_errores(state.servicio().validacion)


@router.get("/celda", response_model=CeldaResponse)
def celda(lat: float = Query(ge=-90, le=90), lon: float = Query(ge=-180, le=180), sitio: str = Query()):
    return _con_errores(state.servicio().celda, lat, lon, sitio)


@router.post("/sensibilidad", response_model=SensibilidadResponse)
def sensibilidad(req: SensibilidadRequest):
    return SensibilidadResponse(retencion=_con_errores(state.servicio().sensibilidad, req.sitio, req.pesos, req.n_top))
