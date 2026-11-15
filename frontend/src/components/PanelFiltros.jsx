// Analog Atlas · frontend/src/components/PanelFiltros.jsx
// v2.0 · 2026-11-15 · Isabelita (equipo Ctrl Z)
// Paso 3, pestaña Results: lo principal es la lista de resultados. "Filters" y "Check a place" son botones que
// abren su sección solo cuando se piden. Cada lugar tiene un enlace a Google Maps con sus coordenadas.
import { useState } from "react";
import { coord, enGoogleMaps, fotoTierra, tramo } from "../lib/atlas.js";
import { porcentajeTop } from "./Puntaje.jsx";
import Icono from "./IconosAtlas.jsx";

export const ROCAS = { any: "Any ground", volcanico: "Volcanic rock", sedimento: "Sedimentary ground" };
const POR_PAGINA = 20;
// Lugares de la región del equipo (Piura) para revisar en un clic; coordenadas del centro del desierto de Sechura
const LUGARES_RAPIDOS = [{ nombre: "Sechura Desert, Piura", lat: -5.9, lon: -80.6 }];

function Rango({ id, nombre, unidad, limites, valor, paso, cambiar }) {
  const [lo, hi] = limites;
  const [a, b] = valor;
  const pct = (v) => ((v - lo) / (hi - lo || 1)) * 100;
  const fijar = (i, v) => {
    const n = Math.min(hi, Math.max(lo, Number(v)));
    cambiar(i === 0 ? [Math.min(n, b), b] : [a, Math.max(n, a)]);
  };
  return (
    <div className="range">
      <span className="label" id={`${id}-l`}>{nombre} ({unidad})</span>
      <div className="range-values">
        <input className="input" type="number" aria-label={`${nombre} minimum`} value={a} step={paso} onChange={(e) => fijar(0, e.target.value)} />
        <span className="muted" style={{ fontSize: 14 }}>to</span>
        <input className="input" type="number" aria-label={`${nombre} maximum`} value={b} step={paso} onChange={(e) => fijar(1, e.target.value)} />
      </div>
      <div className="range-track">
        <span className="range-fill" style={{ left: `${pct(a)}%`, width: `${pct(b) - pct(a)}%` }} />
        <input type="range" min={lo} max={hi} step={paso} value={a} aria-labelledby={`${id}-l`} aria-valuetext={`from ${a} ${unidad}`} onChange={(e) => fijar(0, e.target.value)} />
        <input type="range" min={lo} max={hi} step={paso} value={b} aria-labelledby={`${id}-l`} aria-valuetext={`to ${b} ${unidad}`} onChange={(e) => fijar(1, e.target.value)} />
      </div>
    </div>
  );
}

function RevisarLugar({ revisar }) {
  const [lat, setLat] = useState("");
  const [lon, setLon] = useState("");
  const [estado, setEstado] = useState({ cargando: false, error: "" });
  const ir = async (a, b) => {
    setEstado({ cargando: true, error: "" });
    try {
      await revisar(Number(a), Number(b));
      setEstado({ cargando: false, error: "" });
    } catch (e) {
      setEstado({ cargando: false, error: e.message });
    }
  };
  const valido = lat !== "" && lon !== "" && Math.abs(Number(lat)) <= 90 && Math.abs(Number(lon)) <= 180;
  return (
    <>
      <p className="note">See how any point on land scores against your reference site, and why.</p>
      {LUGARES_RAPIDOS.map((p) => (
        <button key={p.nombre} type="button" className="btn btn-secondary btn-block" disabled={estado.cargando} onClick={() => ir(p.lat, p.lon)}>{p.nombre}</button>
      ))}
      <form style={{ display: "grid", gridTemplateColumns: "1fr 1fr auto", gap: 8 }} onSubmit={(e) => { e.preventDefault(); valido && ir(lat, lon); }}>
        <input className="input" type="number" step="any" placeholder="Latitude" aria-label="Latitude, from −90 to 90" value={lat} onChange={(e) => setLat(e.target.value)} />
        <input className="input" type="number" step="any" placeholder="Longitude" aria-label="Longitude, from −180 to 180" value={lon} onChange={(e) => setLon(e.target.value)} />
        <button type="submit" className="btn btn-secondary" disabled={!valido || estado.cargando}>{estado.cargando ? "…" : "Check"}</button>
      </form>
      {estado.error && <p role="alert" className="state error">{estado.error}</p>}
    </>
  );
}

function filtrosActivos(filtros, limites, descubrimiento) {
  const rangos = ["temp_dia", "elevacion", "pendiente"].filter((k) => limites[k] && filtros[k]
    && (filtros[k][0] !== limites[k][0] || filtros[k][1] !== limites[k][1])).length;
  return rangos + (filtros.roca !== "any" ? 1 : 0) + (descubrimiento ? 0 : 1);
}

export default function PanelFiltros({ limites, filtros, setFiltros, filtrados, total, elegido, alElegir, mostrar, setMostrar, limpiar,
  descubrimiento, cambiarDescubrimiento, cargando, revisarLugar, conocidos = [] }) {
  const [abierto, setAbierto] = useState(null); // null | "filtros" | "lugar"
  const activos = filtrosActivos(filtros, limites, descubrimiento);
  const visibles = filtrados.slice(0, mostrar);
  const alternar = (q) => setAbierto(abierto === q ? null : q);

  return (
    <div className="panel-body results-body" id="panel-filtros">
      <div className="toolbar">
        <button type="button" className={`btn btn-secondary${abierto === "filtros" ? " on" : ""}`} aria-expanded={abierto === "filtros"}
          aria-controls="sec-filtros" onClick={() => alternar("filtros")}>
          Filters{activos > 0 && <span className="badge num">{activos}</span>}
        </button>
        <button type="button" className={`btn btn-secondary${abierto === "lugar" ? " on" : ""}`} aria-expanded={abierto === "lugar"}
          aria-controls="sec-lugar" onClick={() => alternar("lugar")}><Icono nombre="check-place" size={16} /> Check a place</button>
      </div>

      {abierto === "filtros" && (
        <section id="sec-filtros" className="drawer" aria-label="Filters">
          {limites.temp_dia && <Rango id="temp" nombre="Day temperature" unidad="°C" paso={1} limites={limites.temp_dia}
            valor={filtros.temp_dia} cambiar={(v) => setFiltros({ ...filtros, temp_dia: v })} />}
          {limites.elevacion && <Rango id="elev" nombre="Elevation" unidad="m" paso={50} limites={limites.elevacion}
            valor={filtros.elevacion} cambiar={(v) => setFiltros({ ...filtros, elevacion: v })} />}
          {limites.pendiente && <Rango id="pend" nombre="Slope, 28 km average" unidad="°" paso={0.1} limites={limites.pendiente}
            valor={filtros.pendiente} cambiar={(v) => setFiltros({ ...filtros, pendiente: v })} />}
          <div className="field">
            <label htmlFor="roca">Terrain</label>
            <select id="roca" className="select" value={filtros.roca} onChange={(e) => setFiltros({ ...filtros, roca: e.target.value })}>
              {Object.entries(ROCAS).map(([k, v]) => <option key={k} value={k}>{v}</option>)}
            </select>
          </div>
          <label className="toggle">
            <input type="checkbox" checked={descubrimiento} disabled={cargando} onChange={(e) => cambiarDescubrimiento(e.target.checked)} />
            <span>Hide well-known analog sites <span className="note">(within 150 km of the {conocidos.length || 17} studied sites, so new candidates show up)</span></span>
          </label>
          {conocidos.length > 0 && (
            <details>
              <summary><span className="con-icono"><Icono nombre="known-analog" size={16} />The {conocidos.length} well-known analog sites</span></summary>
              <p className="note">Shown on the map as white rings. Pick one to see how it scores. Some score low because they are famous for things we do not measure (water chemistry, microbes) or are smaller than our 28 km cells.</p>
              <ul className="known-list">
                {conocidos.map((c) => (
                  <li key={c.nombre}>
                    <button type="button" className="btn btn-ghost" onClick={() => revisarLugar(c.lat, c.lon)}>{c.nombre}</button>
                    {c.por_que && <p className="note">{c.por_que}. <span className="muted">{c.fuente}</span></p>}
                  </li>
                ))}
              </ul>
            </details>
          )}
          <div className="drawer-foot">
            <button type="button" className="btn btn-ghost" onClick={limpiar} disabled={activos === 0}>Clear all</button>
            <button type="button" className="btn btn-primary" onClick={() => setAbierto(null)}>Done</button>
          </div>
        </section>
      )}

      {abierto === "lugar" && (
        <section id="sec-lugar" className="drawer" aria-label="Check a place">
          <RevisarLugar revisar={revisarLugar} />
          <div className="drawer-foot"><span /><button type="button" className="btn btn-primary" onClick={() => setAbierto(null)}>Done</button></div>
        </section>
      )}

      <section style={{ display: "flex", flexDirection: "column", gap: 12 }} aria-labelledby="r-t" aria-live="polite">
        <div className="section-title">
          <h2 id="r-t" style={{ fontSize: 16 }}>Results</h2>
          <span className="num">{filtrados.length.toLocaleString()} of {total.toLocaleString()} places · best first</span>
        </div>
        {filtrados.length === 0 ? (
          <div className="state">
            <b>No places fit these filters.</b>
            <span className="muted">Widen the slope or elevation range, or set Terrain to Any ground.</span>
            <button type="button" className="btn btn-secondary" onClick={limpiar}>Clear all filters</button>
          </div>
        ) : (
          <ul className="results">
            {visibles.map((l) => (
              <li key={l.id} className="result-item">
                <button type="button" className="result" aria-current={elegido?.id === l.id} onClick={() => alElegir(l.id)}>
                  <img src={fotoTierra(l.lat, l.lon, 30, 176, 132)} alt="" loading="lazy" />
                  <span className="result-text">
                    <span className="result-top"><span>{l.pais}</span><strong>{l.puesto > 0 ? porcentajeTop(l.puesto, l.de) : `${Math.round(l.puntaje)}/100`}</strong></span>
                    <span className="result-meta">
                      {[`${Math.round(l.puntaje)}/100`, tramo(l.puntaje), l.valores.elevacion != null && `${Math.round(l.valores.elevacion).toLocaleString()} m`,
                        l.valores.pendiente != null && `slope ${l.valores.pendiente.toFixed(1)}°`].filter(Boolean).join(" · ")}
                    </span>
                    <span className="result-meta mono">{coord(l.lat, l.lon)}</span>
                  </span>
                </button>
                <a className="maps-link" href={enGoogleMaps(l.lat, l.lon)} target="_blank" rel="noopener noreferrer"
                  aria-label={`Open ${l.pais}, ${coord(l.lat, l.lon)} in Google Maps (new tab)`} title="Open in Google Maps">
                  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
                    <path d="M12 21s-7-6.2-7-11.5A7 7 0 0 1 19 9.5C19 14.8 12 21 12 21z" /><circle cx="12" cy="9.5" r="2.5" />
                  </svg>
                </a>
              </li>
            ))}
          </ul>
        )}
        {filtrados.length > mostrar && (
          <button type="button" className="btn btn-secondary btn-block" onClick={() => setMostrar(mostrar + POR_PAGINA)}>Load more results</button>
        )}
      </section>
    </div>
  );
}
