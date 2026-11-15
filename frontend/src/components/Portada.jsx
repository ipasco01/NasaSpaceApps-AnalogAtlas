// Analog Atlas · frontend/src/components/Portada.jsx
// v1.1 · 2026-11-15 · Isabelita (equipo Ctrl Z)
// Paso 1: portada a pantalla completa. Jerarquía: marca → frase → buscador (foco) → ejemplos cortos → "cómo funciona".
// v1.1: todo cabe en el teléfono (antes la marca empujaba el contenido fuera de la pantalla), Search nunca se ve
// deshabilitado, ejemplos en una línea y la guía como enlace discreto.
import { useRef, useState } from "react";
import { BotonTema, Marca } from "./Cabecera.jsx";
import { Ayuda, Lupa } from "./Iconos.jsx";

const EJEMPLOS = [
  { etiqueta: "Rover terrain on Mars", texto: "Rocky terrain to test rover mobility on Mars" },
  { etiqueta: "Volcanic plains like Jezero", texto: "Dry volcanic plains like Jezero" },
  { etiqueta: "Lava tubes on the Moon", texto: "Lava tubes like Marius Hills on the Moon" },
];

export default function Portada({ buscar, cargando, error, tema, cambiarTema, verGuia }) {
  const [texto, setTexto] = useState("");
  const campo = useRef(null);
  const enviar = (t) => {
    if (cargando) return;
    if (!t.trim()) return campo.current?.focus();
    buscar(t.trim());
  };
  return (
    <main className="landing">
      <div className="float-theme">
        <BotonTema tema={tema} cambiar={cambiarTema} />
      </div>
      <div className="landing-inner">
        <div className="landing-mark">
          <Marca />
          <div className="landing-title">
            <h1>Analog Atlas</h1>
            <span className="sub">Space to Earth</span>
            <span className="by">by <b>Ctrl Z</b></span>
          </div>
        </div>
        <p className="lead">There's no Ctrl+Z on Mars. Find where on Earth to rehearse, scored with NASA data and clear about where the analogy breaks.</p>
        <div className="landing-search">
          <form className="search" role="search" onSubmit={(e) => { e.preventDefault(); enviar(texto); }}>
            <label htmlFor="q" className="sr-only">What would you like to explore?</label>
            <input id="q" ref={campo} value={texto} onChange={(e) => setTexto(e.target.value)}
              placeholder="What would you like to explore?" autoComplete="off" />
            <button type="submit" className="btn btn-primary" disabled={cargando}>
              <Lupa /> <span className="search-label">{cargando ? "Reading…" : "Search"}</span>
            </button>
          </form>
          {error && <p role="alert" className="state error landing-error">{error}</p>}
          <div className="examples">
            <span>Try</span>
            {EJEMPLOS.map((ej) => (
              <button key={ej.etiqueta} type="button" className="chip" disabled={cargando}
                onClick={() => { setTexto(ej.texto); enviar(ej.texto); }}>{ej.etiqueta}</button>
            ))}
          </div>
        </div>
        <button type="button" className="btn btn-ghost landing-help" onClick={verGuia}>
          <Ayuda /> How does Analog Atlas work?
        </button>
      </div>
      <span className="credit">Piura and the Sechura Desert · Sentinel-2 cloudless 2021 (EOX)</span>
    </main>
  );
}
