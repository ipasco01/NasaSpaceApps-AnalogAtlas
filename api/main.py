"""
Aplicación FastAPI principal para Atlas Analog.
Expone los endpoints REST para la interfaz de usuario y clientes externos.
"""

import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI, HTTPException

from config.settings import API_HOST, API_PORT
from models.data_loader import cargar_celdas
from services.motor_service import MotorService

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(name)s %(levelname)s %(message)s",
)
logger = logging.getLogger("atlas")

# Estado compartido: la instancia del motor se crea una sola vez
motor: MotorService = None


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator:
    """Carga la tabla de celdas una sola vez al arrancar el servidor."""
    global motor
    logger.info("Cargando tabla de celdas al arrancar el servidor")
    motor = MotorService(cargar_celdas())
    logger.info("Servidor Atlas Analog listo")
    yield
    logger.info("Cerrando servidor Atlas Analog")


app = FastAPI(
    title="Atlas Analog API",
    description="Análogos terrestres de sitios de la Luna y Marte (NASA Space Apps 2026)",
    version="0.1.0",
    lifespan=lifespan,
)

# Registrar rutas (solo buscar.py existe por ahora)
from api.routes import buscar
app.include_router(buscar.router, prefix="/api")


@app.get("/health")
def health():
    return {"status": "ok", "celdas": int(len(motor.celdas)) if motor else 0}


def get_motor() -> MotorService:
    """Acceso al motor cargado; las rutas lo usan en lugar de recargar datos."""
    return motor


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api.main:app", host=API_HOST, port=API_PORT)
