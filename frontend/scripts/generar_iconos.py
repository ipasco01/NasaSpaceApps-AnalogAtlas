# Analog Atlas · frontend/scripts/generar_iconos.py
# v1.0 · 2026-11-15 · Isabelita (equipo Ctrl Z)
# Convierte los SVG de views/assets/icons/ (fuente única, hechos por el equipo) en frontend/src/components/IconosAtlas.jsx.
# Cada ícono hereda el color del texto (currentColor). Volver a correr si se agrega o cambia un ícono:
#   python frontend/scripts/generar_iconos.py
import re
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
ORIGEN = RAIZ / "views" / "assets" / "icons"
DESTINO = RAIZ / "frontend" / "src" / "components" / "IconosAtlas.jsx"
PERMITIDAS = {"path", "circle", "rect", "ellipse", "line", "polyline", "polygon"}


def interior(svg: str) -> str:
    cuerpo = re.search(r"<svg[^>]*>(.*)</svg>", svg, re.S).group(1).strip()
    etiquetas = set(re.findall(r"<(\w+)", cuerpo))
    if etiquetas - PERMITIDAS:
        raise ValueError(f"Etiquetas no permitidas en un ícono: {etiquetas - PERMITIDAS}")
    return cuerpo


def main() -> None:
    filas = []
    for f in sorted(ORIGEN.glob("*.svg")):
        filas.append(f'  "{f.stem}": <>{interior(f.read_text(encoding="utf-8"))}</>,')
    DESTINO.write_text(
        "// Analog Atlas · frontend/src/components/IconosAtlas.jsx\n"
        "// ARCHIVO GENERADO por frontend/scripts/generar_iconos.py desde views/assets/icons/. No editar a mano.\n\n"
        "const DIBUJOS = {\n" + "\n".join(filas) + "\n};\n\n"
        "export default function Icono({ nombre, size = 18, titulo }) {\n"
        "  const dibujo = DIBUJOS[nombre];\n"
        "  if (!dibujo) return null;\n"
        "  return (\n"
        '    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"\n'
        '      strokeLinecap="round" strokeLinejoin="round" className="icono" role={titulo ? "img" : undefined}\n'
        '      aria-label={titulo} aria-hidden={titulo ? undefined : "true"}>{dibujo}</svg>\n'
        "  );\n}\n",
        encoding="utf-8")
    print(f"{len(filas)} íconos -> {DESTINO.relative_to(RAIZ)}")


if __name__ == "__main__":
    main()
