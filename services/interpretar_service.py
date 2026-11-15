# Atlas Analog · services/interpretar_service.py
# v0.2 · 2026-11-14 · Isabelita (equipo Ctrl Z), con la regla de pregunta aclaratoria de asernaque03-lab
"""
Lectura del texto de búsqueda por palabras clave, mientras no esté conectada la IA (Claude).
Cumple el contrato de POST /api/interpretar: sitio, pesos, imprescindibles, descubrimiento, resumen,
y una pregunta con opciones cuando el texto es corto o no nombra un lugar.
"""

from typing import Optional

from backend.motor import PESOS_BASE, cargar_referencia

# Orden importa: el primero que coincide gana
PALABRAS_SITIO = [
    ("shackleton", ("moon", "lunar", "pole", "polar", "shackleton", "artemis", "luna")),
    ("marius_hills", ("lava tube", "cave", "marius", "tube", "tubo")),
    ("gale", ("gale", "sediment", "clay", "curiosity")),
    ("jezero", ("jezero", "mars", "marte", "martian", "volcanic", "delta", "perseverance")),
]
PALABRAS_PRUEBA = ("rover", "test", "habitat", "drill", "suit", "prueba")
# Pendiente media de celdas de 28 km: mediana 0.1°, percentil 99 2.3° (datos/celdas.parquet). Rangos reales.
PREGUNTA = "What kind of ground do you need? Slope is averaged over each 28 km cell."
OPCIONES = ["Flat plains (under 0.2°)", "Rolling ground (0.2° to 1°)", "Rugged terrain (over 1°)"]


def detectar_sitio(texto: str) -> Optional[str]:
    t = texto.lower()
    return next((sitio for sitio, claves in PALABRAS_SITIO if any(k in t for k in claves)), None)


def interpretar(texto: str) -> dict:
    sitio = detectar_sitio(texto)
    elegido = sitio or "jezero"
    cuerpo = cargar_referencia(elegido)["cuerpo"]
    prueba = any(k in texto.lower() for k in PALABRAS_PRUEBA)
    salida = {"sitio": elegido, "pesos": dict(PESOS_BASE[cuerpo]), "imprescindibles": ["arido"] if prueba else [],
              "descubrimiento": True,
              "resumen": f"Keyword reading (AI not connected yet): compared with {elegido}"
                         + (", barren ground required for equipment testing." if prueba else ".")}
    # Texto corto o sin lugar: se pregunta en vez de adivinar (el frontend muestra las opciones)
    if len(texto.split()) < 6 or sitio is None:
        salida.update(pregunta=PREGUNTA, opciones=OPCIONES)
    return salida
