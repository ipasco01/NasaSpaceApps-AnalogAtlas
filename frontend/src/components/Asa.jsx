// Analog Atlas · frontend/src/components/Asa.jsx
// v1.0 · 2026-11-15 · Isabelita (equipo Ctrl Z)
// Línea para arrastrar los paneles de abajo en celular (como el indicador del iPhone).
// Arrastrar cambia la altura y al soltar se acomoda en la parada más cercana (PARADAS). Tocarla pasa a la siguiente.
// La altura vive en una variable CSS (`variable`) del elemento `en`; en escritorio el CSS la ignora y la línea no se ve.
import { useRef } from "react";

export const PARADAS = [0.25, 0.4, 0.6, 1]; // fracción del alto del área del mapa: baja, ficha, lista, completa

export default function Asa({ alto, setAlto, variable, en, etiqueta }) {
  const arrastre = useRef(null);

  const elemento = (boton) => boton.closest(en);
  const altoActual = (boton) => boton.closest(".panel").getBoundingClientRect().height;
  const altoTotal = (boton) => boton.closest(".stage").clientHeight;

  const bajar = (e) => {
    const boton = e.currentTarget;
    boton.setPointerCapture(e.pointerId);
    arrastre.current = { y: e.clientY, inicio: altoActual(boton), total: altoTotal(boton), movio: false };
  };
  const mover = (e) => {
    const a = arrastre.current;
    if (!a) return;
    const dy = a.y - e.clientY;
    if (Math.abs(dy) > 4) a.movio = true;
    const h = Math.min(a.total, Math.max(64, a.inicio + dy));
    elemento(e.currentTarget).style.setProperty(variable, `${h}px`);
  };
  const soltar = (e) => {
    const a = arrastre.current;
    arrastre.current = null;
    if (!a || !a.movio) return; // fue un toque: lo maneja onClick
    const fraccion = altoActual(e.currentTarget) / a.total;
    const cerca = PARADAS.reduce((m, p) => (Math.abs(p - fraccion) < Math.abs(m - fraccion) ? p : m));
    elemento(e.currentTarget).style.removeProperty(variable);
    setAlto(`${cerca * 100}%`);
    e.currentTarget.dataset.arrastre = "1"; // el click que sigue al arrastre no cuenta como toque
  };
  const tocar = (e) => {
    if (e.currentTarget.dataset.arrastre) { delete e.currentTarget.dataset.arrastre; return; }
    const actual = parseFloat(alto) / 100;
    const siguiente = PARADAS.find((p) => p > actual + 0.01) ?? PARADAS[0];
    setAlto(`${siguiente * 100}%`);
  };

  return (
    <button type="button" className="asa" aria-label={etiqueta} onPointerDown={bajar} onPointerMove={mover}
      onPointerUp={soltar} onPointerCancel={soltar} onClick={tocar}>
      <span aria-hidden="true" />
    </button>
  );
}
