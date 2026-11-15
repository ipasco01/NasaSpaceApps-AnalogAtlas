# Atlas Analog · motor.py
# v0.3 · 2026-11-14 · Isabelita (equipo Ctrl Z)
# Puntaje de parecido entre cada celda de la Tierra y un sitio de referencia de la Luna o Marte.
#
# Por variable k:
#   1. Si la referencia queda fuera del rango de la Tierra, se lleva al extremo de la Tierra (percentil 1 o 99)
#      y se marca como "la Tierra no llega".
#   2. Distancia normalizada con el rango robusto de la Tierra (percentiles 5 a 95).
#   3. Tolerancia con margen (idea de HADES-T): dentro de la tolerancia no se resta nada.
#   4. Parecido s_k = exp(-distancia / 0.25), entre 0 y 1.
# Total: media geométrica ponderada de los s_k (forma del Earth Similarity Index):
#   una variable que falla mucho baja todo el puntaje, no se compensa con las demás.
# Criterio imprescindible: si su s_k < 0.5, el total no pasa de 49.
# v0.3: una temperatura a la que la Tierra no llega (paso 1) se muestra pero no entra al total: si entrara, todos
#   los sitios terminarían buscando "lo más frío de la Tierra". Otras variables saturadas (polvo) sí entran: lo más
#   polvoriento de la Tierra es una buena aproximación. Se suman roca volcánica y sedimento (GLiM).
#
# Uso: python motor.py --celdas ../datos/celdas.parquet --sitio gale [--descubrimiento] [--sensibilidad]

import argparse
from pathlib import Path

import numpy as np
import pandas as pd

RAIZ = Path(__file__).resolve().parent.parent
REFERENCIAS = RAIZ / "science" / "referencias.csv"
CONOCIDOS = RAIZ / "science" / "analogos_conocidos.csv"

# Pesos de partida por cuerpo; la IA o la persona los cambian. Solo entran las variables con valor de referencia.
# v0.2: se suma temp_dia (Shackleton solo tiene máxima del día) y permafrost_proxy para la Luna.
PESOS_BASE = {
    "marte": {"lluvia": 0.15, "ndvi": 0.15, "arido": 0.15, "rango_termico": 0.15,
              "temp_noche": 0.10, "temp_dia": 0.10, "pendiente": 0.10, "polvo": 0.10,
              "volcanico": 0.10, "sedimento": 0.10},
    "luna": {"lluvia": 0.10, "ndvi": 0.10, "arido": 0.10, "rango_termico": 0.15,
             "temp_noche": 0.15, "temp_dia": 0.15, "pendiente": 0.10, "hielo": 0.05,
             "permafrost_proxy": 0.10, "volcanico": 0.10, "sedimento": 0.10},
}
# Variables de sí o no (0/1): el parecido es directo
TERMICAS = {"temp_dia", "temp_noche", "rango_termico"}
BINARIAS = {"arido", "hielo", "permafrost_proxy", "volcanico", "sedimento"}
# Tolerancia con margen, en la unidad de cada variable
TOLERANCIA = {"temp_dia": 3.0, "temp_noche": 3.0, "rango_termico": 3.0, "lluvia": 20.0,
              "ndvi": 0.03, "pendiente": 2.0, "nieve": 5.0, "polvo": 0.02}
ESCALA_DISTANCIA = 0.25
TOPE_IMPRESCINDIBLE = 49
RADIO_CONOCIDO_KM = 150


def cargar_referencia(sitio: str) -> pd.Series:
    refs = pd.read_csv(REFERENCIAS)
    fila = refs[refs["sitio"] == sitio]
    if fila.empty:
        raise ValueError(f"Sitio '{sitio}' no está en {REFERENCIAS.name}. Disponibles: {', '.join(refs['sitio'])}")
    return fila.iloc[0]


def parecido_por_variable(celdas: pd.DataFrame, ref: pd.Series, variables: list[str]):
    """Devuelve (tabla de s_k, variables donde la Tierra no llega al valor de referencia)."""
    partes, saturadas = {}, []
    for k in variables:
        x = celdas[k].to_numpy(dtype=float)
        objetivo = float(ref[k])
        if k in BINARIAS:
            partes[k] = 1.0 - np.abs(np.nan_to_num(x, nan=0.0) - objetivo)
            continue
        p1, p5, p95, p99 = np.nanpercentile(x, [1, 5, 95, 99])
        objetivo_tierra = min(max(objetivo, p1), p99)
        if objetivo_tierra != objetivo:
            saturadas.append(k)
        rango = max(p95 - p5, 1e-9)
        distancia = np.maximum(0.0, np.abs(x - objetivo_tierra) - TOLERANCIA.get(k, 0.0)) / rango
        s = np.exp(-distancia / ESCALA_DISTANCIA)
        partes[k] = np.where(np.isnan(x), np.nan, s)
    return pd.DataFrame(partes, index=celdas.index), saturadas


def puntuar(celdas: pd.DataFrame, ref: pd.Series, pesos: dict[str, float],
            imprescindibles: tuple[str, ...] = ()) -> tuple[pd.DataFrame, list[str]]:
    variables = [k for k in pesos if k in celdas.columns and pd.notna(ref.get(k))]
    if not variables:
        raise ValueError("Ninguna variable tiene valor de referencia y columna en la tabla de la Tierra")
    s, saturadas = parecido_por_variable(celdas, ref, variables)
    # Las temperaturas que la Tierra no alcanza quedan fuera del total (se informan aparte)
    en_total = [k for k in variables if not (k in saturadas and k in TERMICAS)] or variables
    w = np.array([pesos[k] for k in en_total], dtype=float)
    w = w / w.sum()
    s_seguro = s[en_total].clip(lower=0.01).fillna(0.01)          # nada en cero absoluto; dato faltante cuenta como malo
    total = np.exp((np.log(s_seguro.to_numpy()) * w).sum(axis=1)) * 100
    for k in imprescindibles:
        if k in s.columns:
            total = np.where(s[k].fillna(0) < 0.5, np.minimum(total, TOPE_IMPRESCINDIBLE), total)
    salida = celdas[["lat", "lon"]].copy()
    salida["puntaje"] = np.round(total, 1)
    for k in variables:
        salida[f"s_{k}"] = s[k].round(3)
    return salida, saturadas


def lejos_de_conocidos(salida: pd.DataFrame) -> pd.Series:
    """True si la celda está a más de RADIO_CONOCIDO_KM de todo análogo conocido."""
    conocidos = pd.read_csv(CONOCIDOS)
    lat1, lon1 = np.radians(salida["lat"].to_numpy())[:, None], np.radians(salida["lon"].to_numpy())[:, None]
    lat2, lon2 = np.radians(conocidos["lat"].to_numpy())[None, :], np.radians(conocidos["lon"].to_numpy())[None, :]
    a = np.sin((lat2 - lat1) / 2) ** 2 + np.cos(lat1) * np.cos(lat2) * np.sin((lon2 - lon1) / 2) ** 2
    km = 6371 * 2 * np.arcsin(np.sqrt(a))
    return pd.Series(km.min(axis=1) > RADIO_CONOCIDO_KM, index=salida.index)


def sensibilidad(celdas, ref, pesos, n_top=10, cambio=0.2) -> float:
    """Proporción media del Top n que se mantiene al subir o bajar cada peso un 20 %."""
    base = set(puntuar(celdas, ref, pesos)[0].nlargest(n_top, "puntaje").index)
    coincidencias = []
    for k in pesos:
        for factor in (1 - cambio, 1 + cambio):
            p = dict(pesos, **{k: pesos[k] * factor})
            top = set(puntuar(celdas, ref, p)[0].nlargest(n_top, "puntaje").index)
            coincidencias.append(len(base & top) / n_top)
    return float(np.mean(coincidencias))


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--celdas", required=True)
    ap.add_argument("--sitio", required=True)
    ap.add_argument("--top", type=int, default=10)
    ap.add_argument("--imprescindible", nargs="*", default=[])
    ap.add_argument("--descubrimiento", action="store_true", help="oculta celdas cerca de análogos conocidos")
    ap.add_argument("--sensibilidad", action="store_true")
    args = ap.parse_args()

    celdas = pd.read_parquet(args.celdas)
    ref = cargar_referencia(args.sitio)
    pesos = PESOS_BASE[ref["cuerpo"]]
    salida, saturadas = puntuar(celdas, ref, pesos, tuple(args.imprescindible))
    if args.descubrimiento:
        salida = salida[lejos_de_conocidos(salida)]

    print(f"Referencia: {ref['sitio']} ({ref['cuerpo']}) · {len(salida)} celdas evaluadas")
    if saturadas:
        print("La Tierra no llega al valor de referencia en:", ", ".join(saturadas))
    print(salida.nlargest(args.top, "puntaje").to_string(index=False))
    if args.sensibilidad:
        print(f"Sensibilidad: el Top {args.top} se mantiene en promedio un "
              f"{sensibilidad(celdas, ref, pesos, args.top):.0%} al mover cada peso ±20 %")


if __name__ == "__main__":
    main()
