# Atlas Analog · planetas.py
# v0.1 · 2026-11-14 · Isabelita (equipo Ctrl Z)
# Lee el relieve global de Marte (MOLA MEGDR, 4 px/°) y de la Luna (LOLA LDEM_4, 4 px/°) del PDS de la NASA,
# calcula la pendiente a la misma escala gruesa que la tabla de la Tierra (0,25°) y la escribe en
# science/referencias.csv para cada sitio.
# Archivos esperados en datos/planetas/: megt90n000cb.img y ldem_4.img (con sus .lbl).
# Uso: python planetas.py

from pathlib import Path

import numpy as np
import pandas as pd

RAIZ = Path(__file__).resolve().parent.parent
CARPETA = RAIZ / "datos" / "planetas"
REFERENCIAS = RAIZ / "science" / "referencias.csv"

# Formato tomado de las etiquetas .lbl del PDS
RELIEVE = {
    "marte": {"archivo": "megt90n000cb.img", "tipo": ">i2", "escala": 1.0, "radio_km": 3396.0,
              "fuente": "MOLA MEGDR 4 px/° (MGS, PDS Geosciences)"},
    "luna": {"archivo": "ldem_4.img", "tipo": "<i2", "escala": 0.5, "radio_km": 1737.4,
             "fuente": "LOLA LDEM_4 4 px/° (LRO, PDS Geosciences)"},
}
PX_POR_GRADO = 4
LAT_POLO_NO_FIABLE = 85  # cerca del polo esta proyección deforma la pendiente


def leer_relieve(cuerpo: str) -> np.ndarray:
    cfg = RELIEVE[cuerpo]
    datos = np.fromfile(CARPETA / cfg["archivo"], dtype=cfg["tipo"]).astype(float)
    if datos.size != 720 * 1440:
        raise ValueError(f"{cfg['archivo']}: tamaño inesperado {datos.size}")
    return datos.reshape(720, 1440) * cfg["escala"]  # metros; fila 0 = 90° N, columna 0 = 0° E


def pendiente_grados(relieve_m: np.ndarray, radio_km: float) -> np.ndarray:
    paso = np.radians(1 / PX_POR_GRADO) * radio_km * 1000          # metros por celda en latitud
    lat = 90 - (np.arange(720) + 0.5) / PX_POR_GRADO
    dx = paso * np.maximum(np.cos(np.radians(lat)), 1e-3)[:, None]  # metros por celda en longitud
    dz_dy, dz_dx = np.gradient(relieve_m, paso, axis=0), np.gradient(relieve_m, axis=1) / dx
    return np.degrees(np.arctan(np.hypot(dz_dx, dz_dy)))


def valor_en(grilla: np.ndarray, lat: float, lon: float) -> float:
    fila = int(np.clip((90 - lat) * PX_POR_GRADO, 0, 719))
    col = int(((lon % 360) * PX_POR_GRADO)) % 1440
    return float(grilla[fila, col])


def main() -> None:
    refs = pd.read_csv(REFERENCIAS, dtype={"fuente_pendiente": "string", "fuente_temperatura": "string"})
    pendientes = {c: pendiente_grados(leer_relieve(c), RELIEVE[c]["radio_km"]) for c in RELIEVE}
    for i, ref in refs.iterrows():
        cuerpo = ref["cuerpo"]
        valor = round(valor_en(pendientes[cuerpo], ref["lat"], ref["lon"]), 2)
        nota = RELIEVE[cuerpo]["fuente"]
        if abs(ref["lat"]) > LAT_POLO_NO_FIABLE:
            nota += "; cerca del polo la proyección deforma la pendiente: valor no fiable"
        refs.loc[i, "pendiente"] = valor
        refs.loc[i, "fuente_pendiente"] = nota
        print(f"{ref['sitio']:<14} {cuerpo:<6} pendiente {valor:>6} °")
    refs.to_csv(REFERENCIAS, index=False)
    for c, p in pendientes.items():
        print(f"{c}: pendiente mediana {np.median(p):.2f} °, percentil 95 {np.percentile(p, 95):.2f} °")


if __name__ == "__main__":
    main()
