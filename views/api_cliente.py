# Analog Atlas · views/api_cliente.py
# v0.2 · 2026-11-14 · Isabelita (equipo Ctrl Z)
# Cliente de la API para la app Streamlit, con dos modos y las mismas respuestas (esquemas de api/schemas.py):
#   - ATLAS_API sin definir o "local": llama a MotorService en el mismo proceso. Un solo servidor (demo pública).
#   - ATLAS_API=http://...: pide por HTTP a la API (api/main.py), como el frontend React.

import os
from functools import lru_cache

import requests

from api.schemas import (BuscarResponse, CeldaResponse, InterpretarOut, Referencia)

DESTINO = (os.getenv("ATLAS_API") or "local").rstrip("/")
LOCAL = DESTINO == "local"
ESPERA_S = 120


class ApiNoDisponible(RuntimeError):
    """La API no responde o devolvió un error."""


@lru_cache(maxsize=1)
def _servicio():
    """Modo local: la misma pieza que usa la API, cargada una vez por proceso."""
    from config.settings import usa_datos_prueba
    from models.data_loader import cargar_celdas
    from services.motor_service import MotorService
    return MotorService(cargar_celdas()), usa_datos_prueba()


def _pedir(metodo: str, ruta: str, **kwargs):
    try:
        r = requests.request(metodo, DESTINO + ruta, timeout=ESPERA_S, **kwargs)
    except requests.RequestException as e:
        raise ApiNoDisponible(f"No responde {DESTINO} ({type(e).__name__})") from e
    if not r.ok:
        raise ApiNoDisponible(f"{metodo} {ruta} respondió {r.status_code}: {r.text[:200]}")
    return r.json()


def salud() -> dict:
    if LOCAL:
        ms, prueba = _servicio()
        return {"status": "ok", "celdas": len(ms.celdas), "faltan": ms.faltantes(), "datos_prueba": prueba}
    return _pedir("GET", "/health")


def referencias() -> list:
    if LOCAL:
        return [Referencia(**r).model_dump() for r in _servicio()[0].referencias()]
    return _pedir("GET", "/api/referencias")


def interpretar(texto: str) -> dict:
    if LOCAL:
        from services.interpretar_service import interpretar as leer_texto
        return InterpretarOut(**leer_texto(texto)).model_dump()
    return _pedir("POST", "/api/interpretar", json={"texto": texto})


def buscar(sitio: str, pesos: dict, imprescindibles: list, descubrimiento: bool, top: int) -> dict:
    if LOCAL:
        lugares, no_llega, total = _servicio()[0].buscar(sitio, pesos, imprescindibles, descubrimiento, top)
        return BuscarResponse(sitio=sitio, tierra_no_llega=no_llega, lugares=lugares, total_match=total).model_dump()
    return _pedir("POST", "/api/buscar", json={"sitio": sitio, "pesos": pesos, "imprescindibles": imprescindibles,
                                               "descubrimiento": descubrimiento, "top": top})


def conocidos() -> list:
    if LOCAL:
        return _servicio()[0].conocidos_lista()
    return _pedir("GET", "/api/conocidos")


def celda(lat: float, lon: float, sitio: str) -> dict:
    if LOCAL:
        return CeldaResponse(**_servicio()[0].celda(lat, lon, sitio)).model_dump()
    return _pedir("GET", "/api/celda", params={"lat": lat, "lon": lon, "sitio": sitio})


def sensibilidad(sitio: str, pesos: dict, n_top: int = 10) -> float:
    if LOCAL:
        return _servicio()[0].sensibilidad(sitio, pesos, n_top)
    return _pedir("POST", "/api/sensibilidad", json={"sitio": sitio, "pesos": pesos, "n_top": n_top})["retencion"]
