// Analog Atlas · frontend/src/components/Cabecera.jsx
// v1.1 · 2026-11-15 · Isabelita (equipo Ctrl Z) · botón al código en GitHub junto al de modo
// Logo (vuelve al inicio), pasos numerados (los ya recorridos se pueden tocar) y botones de ayuda y modo.
import { Ayuda, Codigo, Luna, Sol } from "./Iconos.jsx";

const REPOSITORIO = "https://github.com/ipasco01/NasaSpaceApps-AnalogAtlas";

const PASOS = ["Search", "Compare", "Explore", "Place"];

export function Marca() {
  return (
    <span className="brand-mark" aria-hidden="true">
      <i className="a" />
      <i className="o" />
    </span>
  );
}

export function BotonTema({ tema, cambiar, clase = "btn btn-secondary btn-icon" }) {
  const otro = tema === "light" ? "dark" : "light";
  return (
    <button type="button" className={clase} onClick={cambiar} aria-label={`Switch to ${otro} mode`} title={`Switch to ${otro} mode`}>
      {tema === "light" ? <Luna /> : <Sol />}
    </button>
  );
}

export function BotonCodigo({ clase = "btn btn-secondary btn-icon" }) {
  return (
    <a className={clase} href={REPOSITORIO} target="_blank" rel="noopener noreferrer"
      aria-label="Source code on GitHub (opens in a new tab)" title="Source code on GitHub">
      <Codigo />
    </a>
  );
}

export default function Cabecera({ paso, irA, alInicio, tema, cambiarTema, verRecorrido }) {
  return (
    <header className="header">
      <button type="button" className="brand" onClick={alInicio} aria-label="Analog Atlas, back to the start">
        <Marca />
        <b>Analog Atlas</b>
        <span>Space to Earth</span>
      </button>
      <nav aria-label="Progress">
        <ol className="steps">
          {PASOS.map((nombre, i) => {
            const n = i + 1;
            const estado = n < paso ? "done" : n === paso ? "now" : "";
            return (
              <li key={nombre} style={{ display: "contents" }}>
                {i > 0 && <span className="step-line" aria-hidden="true" />}
                <button type="button" className={`step ${estado}`} disabled={n >= paso}
                  aria-current={n === paso ? "step" : undefined} onClick={() => irA(n)}>
                  <span className="n">{n}</span>
                  <span className="label">{nombre}</span>
                </button>
              </li>
            );
          })}
        </ol>
      </nav>
      <div className="header-actions">
        <button type="button" className="btn btn-secondary" onClick={verRecorrido}>
          <Ayuda /> <span className="label">How it works</span>
        </button>
        <BotonCodigo />
        <BotonTema tema={tema} cambiar={cambiarTema} />
      </div>
    </header>
  );
}
