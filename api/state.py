# Atlas Analog · api/state.py
# v0.2 · 2026-11-14 · Isabelita (equipo Ctrl Z), sobre la v0.1 de asernaque03-lab
"""
Estado compartido de la API. Evita imports circulares entre main.py y las rutas.
Las rutas llaman a servicio() en cada pedido: importar la variable directamente copiaría el None inicial.
"""

from typing import Optional

from fastapi import HTTPException

from services.motor_service import MotorService

motor_service: Optional[MotorService] = None


def servicio() -> MotorService:
    if motor_service is None:
        raise HTTPException(status_code=503, detail="Servicio no inicializado")
    return motor_service
