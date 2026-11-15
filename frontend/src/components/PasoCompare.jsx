// Analog Atlas · frontend/src/components/PasoCompare.jsx
// v3.0 · 2026-11-15 · Isabelita (equipo Ctrl Z)
// Paso 2: sistema solar fijo (Tierra, Luna, Marte) + panel derecho con desplazamiento propio.
// 1) Recomendación según la búsqueda con "Go there". 2) La cámara vuela al sitio y el panel muestra sus datos
// medidos. 3) "See analogs on Earth" continúa. También se puede tocar un planeta o elegir otro sitio de la lista.
import { useEffect, useRef, useState } from "react";
import { ICONO_VAR, SITIOS } from "../lib/atlas.js";
import Icono from "./IconosAtlas.jsx";
import SistemaSolar, { CUERPOS } from "./SistemaSolar.jsx";

const DATOS = [
  ["temp_dia", "Day temperature", (v) => `${Math.round(v)} °C`],
  ["temp_noche", "Night temperature", (v) => `${Math.round(v)} °C`],
  ["rango_termico", "Day–night swing", (v) => `${Math.round(v)} °C`],
  ["pendiente", "Slope, 28 km average", (v) => `${v.toFixed(1)}°`],
  ["polvo", "Dust in the air (optical depth)", (v) => v.toFixed(2)],
  ["hielo", "Surface ice", (v) => (v >= 0.5 ? "Yes" : "No")],
  ["permafrost_proxy", "Frozen ground", (v) => (v >= 0.5 ? "Yes" : "No")],
];
const FUENTE = { temperatura: "Temperature", pendiente: "Slope", polvo: "Dust", roca: "Rock" };
const roca = (v) => (v.volcanico === 1 ? "Volcanic rock" : v.sedimento === 1 ? "Sedimentary ground" : null);
const LISTA = Object.entries(SITIOS).map(([clave, s]) => ({ clave, ...s }));

function FilaSitio({ s, alElegir }) {
  return (
    <button type="button" className="site-row" onClick={() => alElegir(s.clave)}>
      <img src={s.img} alt="" />
      <span><b>{s.nombre}, {s.cuerpo}</b><span>{s.resumen}</span></span>
    </button>
  );
}

export default function PasoCompare({ consulta, sitioSugerido, referencias, continuar, cargando, error, acento }) {
  const [foco, setFoco] = useState(null);
  const [elegido, setElegido] = useState(null);
  const titulo = useRef(null);
  useEffect(() => titulo.current?.focus(), [foco, elegido]);

  const irSitio = (clave) => { setElegido(clave); setFoco(SITIOS[clave].cuerpo); };
  const irPlaneta = (c) => { setElegido(null); setFoco(c); };
  const volver = () => { setElegido(null); setFoco(null); };
  const sug = SITIOS[sitioSugerido];

  let panel;
  if (elegido) {
    const s = SITIOS[elegido];
    const ref = referencias?.[elegido];
    const v = ref?.valores ?? {};
    panel = (
      <>
        <img src={s.img} alt={`${s.nombre}, ${s.cuerpo}`} className="site-photo" />
        <div className="site-body">
          <div style={{ display: "flex", flexDirection: "column", gap: 4 }}>
            <span className="note">{s.cuerpo}</span>
            <h2 ref={titulo} tabIndex={-1} className="panel-title">{s.nombre}</h2>
            <span className="mono muted">{s.resumen}</span>
          </div>
          <section aria-label="Measured on site">
            <h3 className="section-title" style={{ marginBottom: 8 }}>What we compare Earth against <span>measured on site</span></h3>
            {!ref ? <div className="bar-loading" aria-label="Loading reference data" /> : (
              <div className="rows">
                {DATOS.filter(([k]) => v[k] != null).map(([k, n, f]) => (
                  <div key={k} className="row"><span className="con-icono"><Icono nombre={ICONO_VAR[k]} size={16} />{n}</span><b className="num">{f(v[k])}</b></div>
                ))}
                {roca(v) && <div className="row"><span className="con-icono"><Icono nombre={v.volcanico === 1 ? "volcanic-rock" : "sedimentary-ground"} size={16} />Ground</span><b>{roca(v)}</b></div>}
                <div className="row"><span className="con-icono"><Icono nombre="no-vegetation" size={16} />Vegetation and rain</span><b>None</b></div>
              </div>
            )}
          </section>
          {ref?.fuentes && (
            <details>
              <summary>Sources</summary>
              <ul>{Object.entries(ref.fuentes).map(([k, t]) => <li key={k}><b>{FUENTE[k] ?? k}:</b> {t}</li>)}</ul>
            </details>
          )}
          {error && <p role="alert" className="state error">{error}</p>}
        </div>
        <div className="site-actions">
          <button type="button" className="btn btn-secondary" onClick={volver}>Back to the solar system</button>
          <button type="button" className="btn btn-primary" disabled={cargando} onClick={() => continuar(elegido)}>
            {cargando ? "Scoring every land cell…" : "See analogs on Earth"}
          </button>
        </div>
      </>
    );
  } else if (foco === "Earth") {
    panel = (
      <div className="site-body">
        <span className="note">Earth</span>
        <h2 ref={titulo} tabIndex={-1} className="panel-title">This is where we search</h2>
        <p>Every 28 km patch of land on Earth, 334,741 in total, is compared with the place you pick on the Moon or Mars, using NASA satellite data.</p>
        <p className="muted">Pick a place on the Moon or Mars to start.</p>
        <div className="site-list-col">{LISTA.map((s) => <FilaSitio key={s.clave} s={s} alElegir={irSitio} />)}</div>
        <button type="button" className="btn btn-secondary" onClick={volver}>Back to the solar system</button>
      </div>
    );
  } else if (foco) {
    panel = (
      <div className="site-body">
        <span className="note">{CUERPOS[foco].nombre}</span>
        <h2 ref={titulo} tabIndex={-1} className="panel-title">Places on {foco === "Moon" ? "the Moon" : "Mars"}</h2>
        <p className="muted">Pick one to see what it is like there.</p>
        <div className="site-list-col">{LISTA.filter((s) => s.cuerpo === foco).map((s) => <FilaSitio key={s.clave} s={s} alElegir={irSitio} />)}</div>
        <button type="button" className="btn btn-secondary" onClick={volver}>Back to the solar system</button>
      </div>
    );
  } else {
    panel = (
      <div className="site-body">
        <span className="note">Based on your search</span>
        {consulta && <p className="quote">“{consulta}”</p>}
        <h2 ref={titulo} tabIndex={-1} className="panel-title">Start with {sug.nombre} on {sug.cuerpo === "Moon" ? "the Moon" : "Mars"}</h2>
        <div className="sug">
          <img src={sug.img} alt="" />
          <p>{sug.resumen}. We matched your words to this place; pick another below if it is not what you meant.</p>
        </div>
        <button type="button" className="btn btn-primary btn-block" onClick={() => irSitio(sitioSugerido)}>Go there</button>
        <h3 className="section-title">Other places</h3>
        <div className="site-list-col">{LISTA.filter((s) => s.clave !== sitioSugerido).map((s) => <FilaSitio key={s.clave} s={s} alElegir={irSitio} />)}</div>
      </div>
    );
  }

  return (
    <main className="solar-stage">
      <SistemaSolar sitios={LISTA} foco={foco} elegido={elegido} alPlaneta={irPlaneta} alSitio={irSitio} acento={acento} />
      <aside className="panel panel-right solar-panel" aria-label="Place details">{panel}</aside>
    </main>
  );
}
