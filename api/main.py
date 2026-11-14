"""
Aplicación FastAPI principal para Atlas Analog.
Expone los endpoints REST para la interfaz de usuario y clientes externos.
"""

import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI, HTTPException

from config.settings import API_HOST, API_PORT, API_DEBUG
from models.data_loader import DataLoader
from services.motor_service import MotorService
from api.routes import referencias, buscar, interpretar

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Instancias globales
data_loader: DataLoader
motor_service: MotorService


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator:
    """
    Context manager para inicialización y cierre de recursos.
    Carga los datos una sola vez al iniciar el servidor.
    """
    global data_loader, motor_service
    
    logger.info("Inicializando aplicación Atlas Analog...")
    data_loader = DataLoader()
    motor_service = MotorService(data_loader)
    
    # Precargar datos en memoria
    try:
        data_loader.cargar_celdas()
        data_loader.cargar_referencias()
        data_loader.cargar_analogos_conocidos()
        logger.info("Datos precargados exitosamente")
    except Exception as e:
        logger.error("Error al precargar datos: %s", str(e))
        raise
    
    yield
    
    logger.info("Cerrando aplicación Atlas Analog...")


# Crear aplicación FastAPI
app = FastAPI(
    title="Atlas Analog API",
    description="API para identificación de análogos terrestres de bases lunares y marcianas",
    version="0.1.0",
    lifespan=lifespan,
)

# Registrar rutas
app.include_router(referencias.router, prefix="/api", tags=["referencias"])
app.include_router(buscar.router, prefix="/api", tags=["buscar"])
app.include_router(interpretar.router, prefix="/api", tags=["interpretar"])


@app.get("/health")
async def health_check():
    """Endpoint de verificación de salud del servicio."""
    return {"status": "ok", "service": "atlas-analog"}


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "api.main:app",
        host=API_HOST,
        port=API_PORT,
        reload=API_DEBUG,
        log_level="info",
    )