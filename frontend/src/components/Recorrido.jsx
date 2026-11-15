// Analog Atlas · frontend/src/components/Recorrido.jsx
// v1.0 · 2026-11-14 · Isabelita (equipo Ctrl Z)
// Recorrido de bienvenida del paso 3 (mockup "Explore candidate sites"): 3 tarjetas con Skip / Next.
// Se muestra una vez por navegador; el botón de ayuda de la cabecera lo vuelve a abrir.
import { useEffect, useRef, useState } from "react";

const TARJETAS = [
  { t: "What is an analog site?", d: "A place on Earth that resembles a site on the Moon or Mars in some ways, so teams can rehearse there first. No place matches everything: each 28 km patch of land gets a score from 0 to 100, and every place tells you what matches and what breaks.",
    pos: { left: "calc(50% - 160px)", top: "18%" } },
  { t: "Explore candidate sites", d: "Each dot is one of the best matches. Brighter dots score higher. Hover a dot to compare its typical conditions with your reference site; click it to open the place.",
    pos: { left: "calc(50% - 160px)", top: "18%" } },
  { t: "Narrow it down", d: "Day temperature, elevation and slope use the real range of these results. Terrain keeps only volcanic rock or sediment. Hide well-known analog sites to surface new candidates, or use the Ask tab in plain words.",
    pos: { left: 412, top: 200 } },
  { t: "Check any place", d: "Try Sechura in Piura, or type coordinates, to see how any point on land scores against your reference site and why.",
    pos: { left: 412, top: 120 } },
];
const CLAVE = "aa-recorrido-v2"; // v2: tarjetas nuevas (qué es un análogo, filtros, Check a place)

export function recorridoVisto() {
  try {
    return localStorage.getItem(CLAVE) === "1";
  } catch {
    return false;
  }
}

// centrado: se abre desde la portada o el "?" de la cabecera, en el centro y con fondo oscuro.
export default function Recorrido({ cerrar, centrado = false, validacion = null }) {
  const [i, setI] = useState(0);
  const boton = useRef(null);
  useEffect(() => boton.current?.focus(), [i]);
  useEffect(() => {
    const esc = (e) => e.key === "Escape" && terminar();
    window.addEventListener("keydown", esc);
    return () => window.removeEventListener("keydown", esc);
  });
  const terminar = () => {
    try { localStorage.setItem(CLAVE, "1"); } catch { /* sin almacenamiento: se vuelve a mostrar, no pasa nada */ }
    cerrar();
  };
  const c = TARJETAS[i];
  return (
    <>
    {centrado && <div className="tour-scrim" onClick={terminar} aria-hidden="true" />}
    <section className={`tour${centrado ? " tour-center" : ""}`} role="dialog" aria-modal={centrado} aria-labelledby="tour-t"
      aria-describedby="tour-d" style={centrado ? undefined : c.pos}>
      <h2 id="tour-t">{c.t}</h2>
      <p id="tour-d">{c.d}{i === 0 && validacion && ` Check: ${validacion.top20} of ${validacion.total} well-known analog sites rank in Earth's top 20% for at least one reference site.`}</p>
      <div className="tour-foot">
        <button type="button" className="btn btn-ghost" onClick={terminar}>Skip</button>
        <span className="tour-count">{i + 1} of {TARJETAS.length}</span>
        <button ref={boton} type="button" className="btn btn-primary" onClick={() => (i < TARJETAS.length - 1 ? setI(i + 1) : terminar())}>
          {i < TARJETAS.length - 1 ? "Next" : "Done"}
        </button>
      </div>
    </section>
    </>
  );
}
