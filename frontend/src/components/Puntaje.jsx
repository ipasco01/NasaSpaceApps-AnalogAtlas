// Analog Atlas · frontend/src/components/Puntaje.jsx
// v2.1 · 2026-11-15 · Isabelita (equipo Ctrl Z) · la explicación del puntaje se pliega en celular
// El parecido explicado para cualquiera. Número principal: en qué % de la Tierra queda el lugar ("Top 3 %"),
// porque un puntaje absoluto bajo puede ser de los mejores del planeta. Debajo: puntaje 0-100 con sus tramos,
// puesto exacto, cuántas características coinciden y la prueba con los análogos famosos.
import { useState } from "react";
import { TRAMOS } from "../lib/atlas.js";

const ESCALA = [...TRAMOS].reverse(); // de 0 a 100: Weak, Partial, Good, Strong

export function porcentajeTop(puesto, de) {
  const p = (puesto / de) * 100;
  return p < 0.1 ? "top 0.1%" : p < 1 ? `top ${p.toFixed(1)}%` : `top ${Math.ceil(p)}%`;
}

export default function Puntaje({ lugar, nombreRef, cuerpo, compacto = false, validacion = null }) {
  const valores = Object.values(lugar.desglose);
  const coinciden = valores.filter((v) => v >= 0.75).length;
  const p = Math.round(lugar.puntaje);
  const tramo = TRAMOS.find(([min]) => lugar.puntaje >= min)[1];
  const top = lugar.puesto > 0 ? porcentajeTop(lugar.puesto, lugar.de) : null;
  // Abierta en pantallas grandes; plegada en celular para que las pestañas se vean antes
  const [abierto, setAbierto] = useState(() => window.matchMedia("(min-width: 641px)").matches);
  return (
    <section className={`kpi${compacto ? " kpi-sm" : ""}`} aria-label="How alike this place is, explained">
      <div className="kpi-main">
        {top ? (
          <>
            <span className="kpi-num">{top.replace("top", "Top")}</span>
            <span className="kpi-label"><b>of Earth's land</b><span>ranked by how alike it is to {nombreRef}</span></span>
          </>
        ) : (
          <>
            <span className="kpi-num">{p}<small>/100</small></span>
            <span className="kpi-label"><b>{tramo}</b><span>How alike this place is to {nombreRef}</span></span>
          </>
        )}
      </div>
      <div className="kpi-scale" role="img" aria-label={`Score ${p} on a scale from 0 to 100, in the ${tramo} band`}>
        {ESCALA.map(([min, nombre], i) => {
          const max = i < ESCALA.length - 1 ? ESCALA[i + 1][0] : 101;
          return (
            <span key={nombre} className={`kpi-band${lugar.puntaje >= min && lugar.puntaje < max ? " on" : ""}`} style={{ flex: Math.min(max, 100) - min }}>
              <i />
              <em>{nombre.replace(" analog", "")}</em>
            </span>
          );
        })}
        <span className="kpi-marker" style={{ left: `${Math.min(100, Math.max(0, lugar.puntaje))}%` }} />
      </div>
      <dl className="kpi-facts">
        <div><dt>Score</dt><dd className="num">{p}<span>/100 · {tramo.replace(" analog", "")}</span></dd></div>
        {lugar.puesto > 0 && (
          <div><dt>Rank on Earth</dt><dd className="num">#{lugar.puesto.toLocaleString()} <span>of {lugar.de.toLocaleString()}</span></dd></div>
        )}
        <div><dt>Features that match</dt><dd className="num">{coinciden} <span>of {valores.length} measured</span></dd></div>
      </dl>
      {!compacto && (
        <details className="kpi-how" open={abierto} onToggle={(e) => setAbierto(e.currentTarget.open)}>
          <summary>How is this scored?</summary>
          <p className="note">
            Each feature (temperature, dryness, rock, slope…) gets 0 to 100 and they are combined, so one big difference pulls the
            score down. 100 means as close as Earth gets, not identical: no place on Earth has the gravity or the air
            of {cuerpo === "Moon" ? "the Moon" : "Mars"}.
            {validacion && ` Check: ${validacion.top20} of ${validacion.total} well-known analog sites rank in Earth's top 20% for at least one reference site.`}
          </p>
        </details>
      )}
    </section>
  );
}
