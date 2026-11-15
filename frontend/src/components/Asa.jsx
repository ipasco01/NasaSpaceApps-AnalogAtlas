// Analog Atlas · frontend/src/components/Asa.jsx
// v1.1 · 2026-11-15 · Isabelita (equipo Ctrl Z)
// Línea para arrastrar los paneles de abajo en celular (como el indicador del iPhone).
// Solo dos posiciones: cerrado y abierto (`cerrado` y `abierto`, en % del área del mapa).
// Arrastrar hacia arriba abre y hacia abajo cierra; tocarla cambia a la otra posición.
// La altura vive en una variable CSS (`variable`) del elemento `en`; en escritorio el CSS la ignora y la línea no se ve.
import { useRef } from "react";

const UMBRAL = 24; // px de arrastre para decidir hacia dónde va

export default function Asa({ alto, setAlto, cerrado, abierto, variable, en, etiqueta }) {
  const arrastre = useRef(null);

  const bajar = (e) => {
    const boton = e.currentTarget;
    try { boton.setPointerCapture(e.pointerId); } catch { /* sin captura el arrastre igual funciona dentro de la línea */ }
    arrastre.current = { y: e.clientY, inicio: boton.closest(".panel").getBoundingClientRect().height,
      total: boton.closest(".stage").clientHeight, dy: 0 };
  };
  const mover = (e) => {
    const a = arrastre.current;
    if (!a) return;
    a.dy = a.y - e.clientY;
    const h = Math.min(a.total, Math.max(64, a.inicio + a.dy));
    e.currentTarget.closest(".panel").style.transition = "none"; // sin animación mientras sigue al dedo
    e.currentTarget.closest(en).style.setProperty(variable, `${h}px`); // sigue al dedo mientras arrastra
  };
  const soltar = (e) => {
    const a = arrastre.current;
    arrastre.current = null;
    e.currentTarget.closest(".panel").style.transition = "";
    if (!a) return;
    // Se escribe el valor final aquí mismo: si React no cambia el estado (ya estaba abierto), no vuelve a escribirlo
    const destino = Math.abs(a.dy) < UMBRAL ? alto : a.dy > 0 ? abierto : cerrado;
    e.currentTarget.closest(en).style.setProperty(variable, destino);
    if (Math.abs(a.dy) < UMBRAL) return; // fue un toque: lo maneja onClick
    setAlto(destino);
    e.currentTarget.dataset.arrastre = "1"; // el click que sigue al arrastre no cuenta como toque
  };
  const tocar = (e) => {
    if (e.currentTarget.dataset.arrastre) { delete e.currentTarget.dataset.arrastre; return; }
    setAlto(alto === abierto ? cerrado : abierto);
  };

  return (
    <button type="button" className="asa" aria-label={etiqueta} aria-expanded={alto === abierto}
      onPointerDown={bajar} onPointerMove={mover} onPointerUp={soltar} onPointerCancel={soltar} onClick={tocar}>
      <span aria-hidden="true" />
    </button>
  );
}
