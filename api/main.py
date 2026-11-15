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
from api.state import motor_service

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(name)s %(levelname)s %(message)s",
)
logger = logging.getLogger("atlas")


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator:
    """Carga la tabla de celdas una sola vez al arrancar el servidor."""
    logger.info("Cargando tabla de celdas al arrancar el servidor")
    motor_service = MotorService(cargar_celdas())
    from api.state import motor_service as ms
    ms.motor_service = motor_service
    logger.info("Servidor Atlas Analog listo")
    yield
    logger.info("Cerrando servidor Atlas Analog")
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# ... (resto de imports y lifespan igual)

app = FastAPI(
    title="Atlas Analog API",
    description="Analogos terrestres de sitios de la Luna y Marte (NASA Space Apps 2026)",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS: permite que el frontend (Vite en :5173) llame a esta API (:8000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from api.routes import buscar
app.include_router(buscar.router, prefix="/api")

app = FastAPI(
    title="Atlas Analog API",
    description="Análogos terrestres de sitios de la Luna y Marte (NASA Space Apps 2026)",
    version="0.1.0",
    lifespan=lifespan,
)

# Registrar rutas
from api.routes import buscar
app.include_router(buscar.router, prefix="/api")


@app.get("/health")
def health():
    from api.state import motor_service as ms
    return {"status": "ok", "celdas": int(len(ms.motor_service.celdas)) if ms.motor_service else 0}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api.main:app", host=API_HOST, port=API_PORT)
