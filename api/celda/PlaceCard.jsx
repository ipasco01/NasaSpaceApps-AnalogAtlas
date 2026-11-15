// src/components/PlaceCard.jsx
// Ficha de un lugar. Consume GET /api/celda (valores reales, ya no "Data pending").
// Incluye el comparador de imágenes con barra de escala y el bloque de limites de la Tierra
// (conocimiento de dominio, no dato medido: se define aqui con su fuente).
// Botones "Copiar ficha cientifica" y "Exportar JSON" segun requisito 3.4.

import { useState } from "react";
import { colorTramo } from "../lib/atlasApi";

// Limites que ningun lugar de la Tierra imita, por cuerpo. Fuente: ARQUITECTURA 3.2.
// No es dato medido: es el recordatorio cientifico que el jurado pide ver siempre.
const LIMITES = {
  marte: [
    "Gravity 0.38 g (Earth 1 g)",
    "Atmosphere ~6 mbar, CO2 95% (Earth 1013 mbar)",
    "No global magnetic field: unshielded radiation",
  ],
  luna: [
    "Gravity 0.16 g (Earth 1 g)",
    "Vacuum: no atmosphere",
    "No global magnetic field: unshielded radiation",
  ],
};

export default function PlaceCard({ cell, cuerpo, onClose }) {
  const [wipe, setWipe] = useState(50); // posicion de la barra del comparador

  const seParece = cell.se_parece || [];
  const falla = cell.falla || [];
  const limites = LIMITES[cuerpo] || [];

  const copiarFicha = () => {
    const texto = [
      `Site: ${cell.lat.toFixed(2)}, ${cell.lon.toFixed(2)}`,
      `Score: ${cell.puntaje} (${cell.tramo})`,
      `Resembles: ${seParece.join(", ")}`,
      `Fails: ${falla.join(", ")}`,
      `Earth limits: ${limites.join("; ")}`,
    ].join("\n");
    navigator.clipboard.writeText(texto);
  };

  const exportarJson = () => {
    const blob = new Blob([JSON.stringify(cell, null, 2)], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `celda_${cell.lat.toFixed(2)}_${cell.lon.toFixed(2)}.json`;
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <aside className="aa-card">
      {/* Comparador Tierra / planeta con barra de escala (requisito 3.4) */}
      <div className="aa-compare">
        <img src={cell.imgTierra} alt="Earth" className="aa-compare-base" />
        <div className="aa-compare-top" style={{ clipPath: `inset(0 ${100 - wipe}% 0 0)` }}>
          <img src={cell.imgPlaneta} alt={cuerpo} />
        </div>
        <input
          type="range" min="0" max="100" value={wipe}
          onChange={(e) => setWipe(e.target.value)}
          className="aa-compare-slider" aria-label="Comparison slider"
        />
        <span className="aa-scale">Scale: 120 km</span>
      </div>

      <button className="aa-card-close" onClick={onClose} aria-label="Close">X</button>

      <h2 className="aa-card-title">Site preview</h2>
      <p className="aa-card-sub">{cell.lat.toFixed(2)}, {cell.lon.toFixed(2)}</p>

      {/* Valores reales de la API; ya no "Data pending" */}
      <dl className="aa-rows">
        <Row k="Slope" v={fmt(cell.valores?.pendiente, "deg")} />
        <Row k="Elevation" v={fmt(cell.valores?.elevacion, "m")} />
        <Row k="Day temp" v={fmt(cell.valores?.temp_dia, "C")} />
        <Row k="Night temp" v={fmt(cell.valores?.temp_noche, "C")} />
      </dl>

      <div className="aa-score">
        <span className="aa-score-num" style={{ color: colorTramo(cell.tramo) }}>
          {cell.puntaje}
        </span>
        <span className="aa-score-tramo">{cell.tramo}</span>
      </div>

      {/* Barras por dimension: el desglose de 0 a 1 */}
      <div className="aa-bars">
        {Object.entries(cell.desglose || {}).map(([k, v]) => (
          <div className="aa-bar" key={k}>
            <span className="aa-bar-label">{k}</span>
            <span className="aa-bar-track">
              <span className="aa-bar-fill" style={{ width: `${v * 100}%` }} />
            </span>
            <span className="aa-bar-val">{v.toFixed(2)}</span>
          </div>
        ))}
      </div>

      <section className="aa-method">
        <h3>Methodology &amp; evidence</h3>
        <p>Percentile-normalized distance per variable, weighted geometric mean (Earth Similarity Index form).</p>
      </section>

      {/* Bloque de limites: pesa igual que el comparador (requisito 3.4) */}
      <section className="aa-limits">
        <h3>Limitations (Earth cannot imitate)</h3>
        <ul>{limites.map((l) => <li key={l}>{l}</li>)}</ul>
      </section>

      <p className="aa-resemble">
        <strong>Resembles:</strong> {seParece.join(", ") || "—"}<br />
        <strong>Fails:</strong> {falla.join(", ") || "—"}
      </p>

      <div className="aa-card-actions">
        <button onClick={copiarFicha}>Copy scientific card</button>
        <button onClick={exportarJson}>Export JSON</button>
      </div>
      <div className="aa-card-links">
        <a href="#compare">Compare sites</a>
        <a href="#refine">Refine with AI</a>
      </div>
    </aside>
  );
}

function Row({ k, v }) {
  return (
    <>
      <dt className="aa-row-label">{k}</dt>
      <dd className="aa-row-value aa-tabular">{v}</dd>
    </>
  );
}

function fmt(x, unit) {
  if (x == null || Number.isNaN(x)) return "—";
  return `${x.toFixed(1)} ${unit}`;
}
