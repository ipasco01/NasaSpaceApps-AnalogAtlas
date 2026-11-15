# Atlas Analog · api/main.py
# v0.3 · 2026-11-14 · Isabelita (equipo Ctrl Z), sobre la v0.2 de asernaque03-lab
"""
Aplicación FastAPI de Atlas Analog. Expone los endpoints REST para la app Streamlit y el frontend React.
Uso (desde la raíz del repo): python -m api.main   ->  http://127.0.0.1:8000/docs
"""

import logging
import threading
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from api import state
from api.routes import buscar
from config.settings import API_HOST, API_PORT, usa_datos_prueba
from models.data_loader import cargar_celdas
from services.motor_service import MotorService

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(name)s %(levelname)s %(message)s")
logger = logging.getLogger("atlas")
PRECARGA_TOP = 3000  # igual que TOP en frontend/src/App.jsx


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator:
    """Carga la tabla de celdas una sola vez al arrancar el servidor."""
    logger.info("Cargando tabla de celdas al arrancar el servidor")
    state.motor_service = MotorService(cargar_celdas())
    # Precarga en segundo plano: el servidor responde desde ya y las búsquedas por defecto quedan instantáneas
    threading.Thread(target=state.motor_service.precargar, args=(PRECARGA_TOP,), daemon=True).start()
    logger.info("Servidor Atlas Analog listo")
    yield
    logger.info("Cerrando servidor Atlas Analog")


app = FastAPI(
    title="Atlas Analog API",
    description="Análogos terrestres de sitios de la Luna y Marte (NASA Space Apps 2026)",
    version="0.3.0",
    lifespan=lifespan,
)

# CORS: el frontend React (Vite en :5173) llama a esta API (:8000). Streamlit llama desde el servidor, no lo necesita.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)
app.include_router(buscar.router, prefix="/api")


@app.get("/health")
def health():
    ms = state.motor_service
    return {"status": "ok", "celdas": int(len(ms.celdas)) if ms else 0,
            "faltan": ms.faltantes() if ms else [], "datos_prueba": usa_datos_prueba()}


# Un solo servidor: si existe el frontend compilado (cd frontend && npm run build), se sirve en "/".
# Va al final para que /api y /health tengan prioridad.
FRONTEND = Path(__file__).resolve().parent.parent / "frontend" / "dist"
if FRONTEND.exists():
    app.mount("/", StaticFiles(directory=FRONTEND, html=True), name="frontend")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api.main:app", host=API_HOST, port=API_PORT)
