# Atlas Analog · services/motor_service.py
# v0.5 · 2026-11-15 · Isabelita (equipo Ctrl Z), sobre la v0.2 de asernaque03-lab · sales, carbonatos y tubos de lava
"""
Servicio de negocio que delega el cálculo en el motor validado del equipo (backend/motor.py).
No duplica la lógica de similitud: solo arma las respuestas del contrato (contrato/schema.json).
"""

import logging
from typing import Dict, List, Tuple

import numpy as np
import pandas as pd

from backend.motor import PESOS_BASE, cargar_referencia, lejos_de_conocidos, puntuar, sensibilidad
from config.settings import TRAMOS
from models.data_loader import cargar_analogos_conocidos, cargar_tubos_lava, cargar_referencias, columnas_faltantes
from services.geo import pais_de

logger = logging.getLogger(__name__)

# Valores crudos de la Tierra que se devuelven con cada lugar (los que la tabla tenga)
CRUDOS = ("temp_dia", "temp_noche", "rango_termico", "pendiente", "ndvi", "nieve", "elevacion", "lluvia", "polvo",
          "volcanico", "sedimento", "evaporita", "carbonato")
CACHE_MAX = 32              # búsquedas guardadas (cada una ~1.6 MB)
UMBRAL_MATCH = 50.0         # contador "N matches": tramo "Bueno" o superior
SE_PARECE, FALLA = 0.75, 0.5  # contrato: se_parece s >= 0.75; falla s < 0.5
COLUMNAS_NO_VALOR = {"sitio", "cuerpo", "lat", "lon", "notas"}


def clasificar_tramo(puntaje: float) -> str:
    """Tramo por umbral inferior (TRAMOS va de mayor a menor): 74.5 es 'Bueno', no cae en un hueco."""
    for minimo, _maximo, nombre in TRAMOS:
        if puntaje >= minimo:
            return nombre
    return TRAMOS[-1][2]


def km_entre(lat: float, lon: float, lats: np.ndarray, lons: np.ndarray) -> np.ndarray:
    lat1, lon1, lat2, lon2 = np.radians(lat), np.radians(lon), np.radians(lats), np.radians(lons)
    a = np.sin((lat2 - lat1) / 2) ** 2 + np.cos(lat1) * np.cos(lat2) * np.sin((lon2 - lon1) / 2) ** 2
    return 6371 * 2 * np.arcsin(np.sqrt(a))


class MotorService:
    """Fachada de alto nivel sobre backend/motor.py para la capa de API."""

    def __init__(self, celdas: pd.DataFrame) -> None:
        self.celdas = celdas
        self.conocidos = cargar_analogos_conocidos()
        self.tubos = cargar_tubos_lava()
        self._cache: Dict[tuple, tuple] = {}
        self._validacion = None
        logger.info("MotorService listo con %d celdas en memoria", len(celdas))

    def conocidos_lista(self) -> List[dict]:
        """Los análogos ya estudiados (science/analogos_conocidos.csv) que el modo descubrimiento oculta."""
        texto = lambda f, k: "" if k not in f.index or pd.isna(f[k]) else str(f[k])
        return [{"nombre": str(f["nombre"]), "lat": float(f["lat"]), "lon": float(f["lon"]), "nota": texto(f, "nota"),
                 "por_que": texto(f, "por_que"), "fuente": texto(f, "fuente_por_que")} for _, f in self.conocidos.iterrows()]

    def tubos_lista(self) -> List[dict]:
        """Tubos de lava conocidos, con por qué importan y su fuente (solo para el mapa)."""
        return [{"nombre": str(f["nombre"]), "lat": float(f["lat"]), "lon": float(f["lon"]), "nota": str(f["nota"]),
                 "por_que": str(f["por_que"]), "fuente": str(f["fuente_por_que"])} for _, f in self.tubos.iterrows()]

    def validacion(self) -> dict:
        """Prueba del método: mejor puesto (en % de la Tierra) de cada análogo famoso contra cualquiera de los sitios,
        con los pesos base. Se calcula una vez (los datos no cambian en marcha)."""
        if self._validacion is None:
            lats, lons = self.celdas["lat"].to_numpy(), self.celdas["lon"].to_numpy()
            idx = [self.celdas.index[int(np.argmin(km_entre(f["lat"], f["lon"], lats, lons)))] for _, f in self.conocidos.iterrows()]
            mejor = {i: (100.0, "") for i in range(len(idx))}
            for r in self.referencias():
                salida, _ = puntuar(self.celdas, cargar_referencia(r["sitio"]), r["pesos_base"])
                top = 100 - 100 * salida["puntaje"].rank(pct=True)
                for i, etiqueta in enumerate(idx):
                    if float(top[etiqueta]) < mejor[i][0]:
                        mejor[i] = (round(float(top[etiqueta]), 1), r["sitio"])
            detalle = [{"nombre": str(self.conocidos.iloc[i]["nombre"]), "top_pct": v, "sitio": s} for i, (v, s) in mejor.items()]
            self._validacion = {"total": len(detalle), "top10": sum(d["top_pct"] <= 10 for d in detalle),
                                "top20": sum(d["top_pct"] <= 20 for d in detalle), "detalle": detalle}
        return self._validacion

    def faltantes(self) -> List[str]:
        return columnas_faltantes(self.celdas)

    @staticmethod
    def referencias() -> List[dict]:
        refs = cargar_referencias()
        salida = []
        for _, f in refs.iterrows():
            valores = {k: float(f[k]) for k in refs.columns
                       if k not in COLUMNAS_NO_VALOR and not k.startswith("fuente_") and pd.notna(f[k])}
            fuentes = {k.removeprefix("fuente_"): str(f[k]) for k in refs.columns if k.startswith("fuente_") and pd.notna(f[k])}
            salida.append({"sitio": f["sitio"], "cuerpo": f["cuerpo"], "lat": float(f["lat"]), "lon": float(f["lon"]),
                           "valores": valores, "fuentes": fuentes, "pesos_base": PESOS_BASE[f["cuerpo"]]})
        return salida

    def buscar(self, sitio: str, pesos: Dict[str, float], imprescindibles: List[str], descubrimiento: bool,
               top: int) -> Tuple[List[dict], List[str], int]:
        """Top N de análogos terrestres. Devuelve (lugares, variables que la Tierra no alcanza, total sobre el umbral).
        Guarda en caché las últimas búsquedas: la misma pregunta responde al instante (los datos no cambian en marcha)."""
        clave = (sitio, tuple(sorted(pesos.items())), tuple(sorted(imprescindibles)), descubrimiento, top)
        if clave in self._cache:
            return self._cache[clave]
        resultado = self._buscar(sitio, pesos, imprescindibles, descubrimiento, top)
        if len(self._cache) >= CACHE_MAX:
            self._cache.pop(next(iter(self._cache)))
        self._cache[clave] = resultado
        return resultado

    def precargar(self, top: int) -> None:
        """Calcula de antemano la búsqueda por defecto de cada sitio (la que usa la página)."""
        for r in self.referencias():
            for descubrimiento in (True, False):
                self.buscar(r["sitio"], r["pesos_base"], [], descubrimiento, top)
        self.validacion()
        logger.info("Precarga lista: %d búsquedas en caché y validación con %d análogos", len(self._cache), len(self.conocidos))

    def _buscar(self, sitio: str, pesos: Dict[str, float], imprescindibles: List[str], descubrimiento: bool,
                top: int) -> Tuple[List[dict], List[str], int]:
        todas, saturadas = puntuar(self.celdas, cargar_referencia(sitio), pesos, tuple(imprescindibles))
        # Puesto entre TODAS las celdas de tierra (también las cercanas a análogos conocidos), para que se pueda leer
        # "puesto N de 334.741" igual en la búsqueda y en "Check a place".
        puesto = todas["puntaje"].rank(ascending=False, method="min")
        salida = todas[lejos_de_conocidos(todas)] if descubrimiento else todas
        total_match = int((salida["puntaje"] >= UMBRAL_MATCH).sum())
        top_df = salida.nlargest(top, "puntaje")
        paises = pais_de(top_df["lat"].to_numpy(), top_df["lon"].to_numpy())
        lugares = [{**self._lugar(idx, fila), "pais": str(p), "puesto": int(puesto[idx]), "de": len(todas)}
                   for (idx, fila), p in zip(top_df.iterrows(), paises)]
        return lugares, list(saturadas), total_match

    def _lugar(self, idx, fila: pd.Series) -> dict:
        crudos = self.celdas.loc[idx]
        return {"id": int(idx), "lat": float(fila["lat"]), "lon": float(fila["lon"]),
                "puntaje": float(fila["puntaje"]), "tramo": clasificar_tramo(float(fila["puntaje"])),
                "desglose": {c[2:]: float(fila[c]) for c in fila.index if c.startswith("s_") and pd.notna(fila[c])},
                "valores": {k: float(crudos[k]) for k in CRUDOS if k in crudos.index and pd.notna(crudos[k])}}

    def celda(self, lat: float, lon: float, sitio: str) -> dict:
        """Ficha de la celda más cercana a (lat, lon), con los pesos base del cuerpo del sitio."""
        ref = cargar_referencia(sitio)
        idx = int(np.argmin(km_entre(lat, lon, self.celdas["lat"].to_numpy(), self.celdas["lon"].to_numpy())))
        etiqueta = self.celdas.index[idx]
        salida, _ = puntuar(self.celdas, ref, PESOS_BASE[ref["cuerpo"]])
        valor = float(salida.loc[etiqueta, "puntaje"])
        lugar = {**self._lugar(etiqueta, salida.loc[etiqueta]),
                 "pais": str(pais_de(np.array([self.celdas["lat"].iloc[idx]]), np.array([self.celdas["lon"].iloc[idx]]))[0]),
                 "puesto": int((salida["puntaje"] > valor).sum()) + 1, "de": len(salida)}
        km = km_entre(lugar["lat"], lugar["lon"], self.conocidos["lat"].to_numpy(), self.conocidos["lon"].to_numpy())
        cerca = int(np.argmin(km))
        return {**lugar,
                "se_parece": [k for k, s in lugar["desglose"].items() if s >= SE_PARECE],
                "falla": [k for k, s in lugar["desglose"].items() if s < FALLA],
                "analogo_cercano": {"nombre": str(self.conocidos.iloc[cerca]["nombre"]), "km": round(float(km[cerca]), 1)}}

    def sensibilidad(self, sitio: str, pesos: Dict[str, float], n_top: int) -> float:
        """Proporción del Top N que se mantiene al mover cada peso ±20 % (motor.sensibilidad)."""
        return sensibilidad(self.celdas, cargar_referencia(sitio), pesos, n_top=n_top)
