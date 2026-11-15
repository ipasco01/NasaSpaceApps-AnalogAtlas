// src/components/PlaceCard.jsx
// Ficha de lugar. Respeta el protocolo visual de Analog Atlas (captura aprobada).
// Todo en inglés, layout comparador-barras-matches/breaks, límites físicos obligatorios.

import { useState } from "react";
import { colorTramo } from "../lib/atlasApi";

// Mapeo de variables del backend a nombres en inglés (protocolo)
const VARIABLE_NAMES = {
  ndvi: "No vegetation",
  arido: "Barren ground",
  pendiente: "Slope",
  rango_termico: "Day-night swing",
  temp_dia: "Day temperature",
  temp_noche: "Night temperature",
};

// Tramos en inglés (protocolo)
const TRAMOS_EN = {
  "Muy buen análogo": "Strong analog",
  "Bueno": "Good analog",
  "Parcial": "Partial analog",
  "Débil": "Weak analog",
};

// Límites físicos que ningún lugar de la Tierra puede reproducir (protocolo)
const LIMITES_FISICOS = {
  marte: [
    { label: "Gravity", mars: "0.379 g", earth: "1 g" },
    { label: "Air pressure", mars: "~0.63%", earth: "of Earth's" },
    { label: "Surface radiation", mars: "~0.67 mSv/day", earth: "far above Earth" },
  ],
  luna: [
    { label: "Gravity", moon: "0.165 g", earth: "1 g" },
    { label: "Air pressure", moon: "vacuum", earth: "1 atm" },
    { label: "Surface radiation", moon: "~1.3 mSv/day", earth: "far above Earth" },
  ],
};

export default function PlaceCard({ cell, cuerpo, sitio, onClose }) {
  const [wipe, setWipe] = useState(50);

  const seParece = cell.se_parece || [];
  const falla = cell.falla || [];
  const limites = LIMITES_FISICOS[cuerpo] || [];
  const tramoEn = TRAMOS_EN[cell.tramo] || cell.tramo;

  // Separar variables en matches (s >= 0.75) y breaks (s < 0.5)
  const matches = Object.entries(cell.desglose || {})
    .filter(([_, v]) => v >= 0.75)
    .sort((a, b) => b[1] - a[1]);
  
  const breaks = Object.entries(cell.desglose || {})
    .filter(([_, v]) => v < 0.5)
    .sort((a, b) => a[1] - b[1]);

  const copiarFicha = () => {
    const texto = [
      `Site: ${cell.lat.toFixed(2)}, ${cell.lon.toFixed(2)}`,
      `Score: ${cell.puntaje} (${tramoEn})`,
      `vs ${sitio}, ${cuerpo}`,
      `Matches: ${matches.map(([k]) => VARIABLE_NAMES[k] || k).join(", ")}`,
      `Breaks: ${breaks.map(([k]) => VARIABLE_NAMES[k] || k).join(", ")}`,
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
    <div className="aa-ficha">
      {/* Header con breadcrumbs */}
      <div className="aa-ficha-header">
        <div className="aa-breadcrumbs">
          <span>{sitio}, {cuerpo}</span>
          <span>›</span>
          <span>India</span>
          <span>›</span>
          <span>{cell.lat.toFixed(2)}° {cell.lat >= 0 ? "N" : "S"}, {cell.lon.toFixed(2)}° {cell.lon >= 0 ? "E" : "W"}</span>
          <span>· Mission and equipment testing weights</span>
        </div>
        <button onClick={onClose} className="aa-close">✕</button>
      </div>

      {/* Puntaje principal */}
      <div className="aa-score-header">
        <span className="aa-score-num">{cell.puntaje}</span>
        <span className="aa-score-text">{tramoEn}</span>
        <span className="aa-score-sub">vs {sitio}, {cuerpo} · Mission and equipment testing weights</span>
      </div>

      {/* Layout principal: comparador + barras */}
      <div className="aa-ficha-body">
        {/* Comparador de imágenes (izquierda) */}
        <div className="aa-compare">
          <div className="aa-compare-imgs">
            <img src={cell.imgTierra} alt="Earth" className="aa-compare-base" />
            <div className="aa-compare-top" style={{ clipPath: `inset(0 ${100 - wipe}% 0 0)` }}>
              <img src={cell.imgPlaneta} alt={cuerpo} />
            </div>
            <div className="aa-compare-handle" style={{ left: `${wipe}%` }}>
              <div className="aa-handle-circle">↔</div>
            </div>
          </div>
          <div className="aa-compare-labels">
            <span className="aa-scale">20 km</span>
            <span className="aa-scale">20 km</span>
          </div>
          <div className="aa-compare-corners">
            <span>Earth</span>
            <span>{cuerpo === "marte" ? "Mars" : "Moon"}</span>
          </div>
          <input
            type="range"
            min="0"
            max="100"
            value={wipe}
            onChange={(e) => setWipe(e.target.value)}
            className="aa-compare-slider"
          />
        </div>

        {/* Barras de similitud (derecha) */}
        <div className="aa-bars-section">
          <h3>Similarity by variable</h3>
          {Object.entries(cell.desglose || {}).map(([k, v]) => (
            <div className="aa-bar-row" key={k}>
              <span className="aa-bar-label">{VARIABLE_NAMES[k] || k}</span>
              <div className="aa-bar-track">
                <div className="aa-bar-fill" style={{ width: `${v * 100}%` }} />
              </div>
              <span className="aa-bar-value">{Math.round(v * 100)}</span>
            </div>
          ))}
        </div>
      </div>

      {/* Matches vs Breaks */}
      <div className="aa-matches-breaks">
        <div className="aa-matches">
          <h3>Matches</h3>
          {matches.map(([k, v]) => (
            <div className="aa-match-row" key={k}>
              <span>{VARIABLE_NAMES[k] || k}</span>
              <span>{Math.round(v * 100)}</span>
            </div>
          ))}
        </div>
        <div className="aa-breaks">
          <h3>Breaks the analogy</h3>
          {breaks.map(([k, v]) => (
            <div className="aa-break-row" key={k}>
              <span>{VARIABLE_NAMES[k] || k}</span>
              <span className="aa-break-value">{Math.round(v * 100)}</span>
            </div>
          ))}
        </div>
      </div>

      {/* Límites físicos */}
      <div className="aa-limites">
        <h2>What no place on Earth reproduces</h2>
        <div className="aa-limites-list">
          {limites.map((l) => (
            <div className="aa-limite-row" key={l.label}>
              <span className="aa-limite-label">{l.label}</span>
              <span className="aa-limite-mars">{l.mars || l.moon}</span>
              <span className="aa-limite-earth">{l.earth}</span>
            </div>
          ))}
        </div>
      </div>

      {/* Footer de fuentes */}
      <div className="aa-fuentes">
        Earth view 120 km wide: Sentinel-2 cloudless 2021 (EOX). Reference: Viking MDIM 2.1, NASA Mars Trek.
      </div>

      {/* Acciones */}
      <div className="aa-actions">
        <button onClick={copiarFicha}>Copy scientific card</button>
        <button onClick={exportarJson}>Export JSON</button>
      </div>
    </div>
  );
}
