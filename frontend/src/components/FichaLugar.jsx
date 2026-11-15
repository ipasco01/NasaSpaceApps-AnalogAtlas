// Analog Atlas · frontend/src/components/FichaLugar.jsx
// v2.3 · 2026-11-15 · Isabelita (equipo Ctrl Z) · la roca también puede ser sal o carbonato
// Paso 4: ficha del lugar. Un solo puntaje; "View as" cambia qué se muestra primero (Educator, Researcher,
// Mission test, Explorer). "Expand comparison" abre la Tierra y la referencia grandes, lado a lado o con deslizador.
// v2.2: en celular la ficha es una hoja que se arrastra con la línea de arriba (Asa); tabla de prueba con encabezados y nombres cortos.
import { Fragment, useEffect, useRef, useState } from "react";
import { createPortal } from "react-dom";
import { ICONO_VAR, LIMITES, SITIOS, VARIABLES, VISTAS, anchoVistaKm, api, coord, enGoogleMaps, fotoTierra, tramo } from "../lib/atlas.js";
import { Cerrar } from "./Iconos.jsx";
import Asa from "./Asa.jsx";
import Icono from "./IconosAtlas.jsx";
import Puntaje from "./Puntaje.jsx";

const UNIDAD = { temp_dia: " °C", temp_noche: " °C", rango_termico: " °C", pendiente: "°", elevacion: " m" };
const CHEQUEO = ["roca", "pendiente", "polvo", "elevacion", "temp_dia", "temp_noche"];
// Nombres cortos para la tabla de la prueba (caben en una línea a 390 px)
const CORTO = { roca: "Rock", pendiente: "Slope", polvo: "Dust", elevacion: "Elevation", temp_dia: "Day temp.", temp_noche: "Night temp." };
// "Good for" en la vista Mission test: [texto, ícono de tipo de prueba]
const BUENO_PARA = { roca: (r) => [`Driving on ${r.toLowerCase()}`, "rover-mobility"], pendiente: () => ["Slope and mobility tests", "rover-mobility"],
  polvo: () => ["Dust on suits and moving parts", "spacesuit"], arido: () => ["Mobility on barren ground", "rover-mobility"],
  ndvi: () => ["Setting up a habitat with no vegetation in the way", "habitat"] };

const roca = (v) => (v?.volcanico === 1 ? "Volcanic rock" : v?.sedimento === 1 ? "Sedimentary ground" : v?.evaporita === 1 ? "Salt flats"
  : v?.carbonato === 1 ? "Carbonate rock" : v?.volcanico === 0 ? "Other rock" : null);
function fmt(k, v) {
  if (v == null) return "n/a";
  if (k === "elevacion") return `${Math.round(v).toLocaleString()} m`;
  if (k === "polvo") return v.toFixed(2);
  return `${v.toFixed(k === "pendiente" ? 1 : 0)}${UNIDAD[k] ?? ""}`;
}
function estado(desglose, k) {
  const s = k === "roca" ? Math.min(desglose.volcanico ?? 1, desglose.sedimento ?? 1) : desglose[k];
  if (s == null || (k === "roca" && desglose.volcanico == null && desglose.sedimento == null)) return "";
  return s >= 0.75 ? "ok" : s < 0.5 ? "ko" : "mid";
}
const SIMBOLO = { ok: "✓", ko: "✗", mid: "~", "": "" };

function Deslizador({ tierra, imagenRef, etiquetaRef, alto }) {
  const [corte, setCorte] = useState(50);
  const caja = useRef(null);
  const mover = (x) => {
    const r = caja.current.getBoundingClientRect();
    setCorte(Math.max(0, Math.min(100, ((x - r.left) / r.width) * 100)));
  };
  return (
    <div ref={caja} className="compare" style={{ "--corte": `${corte}%`, ...(alto ? { aspectRatio: "auto", height: alto } : {}) }}
      onPointerDown={(e) => { e.currentTarget.setPointerCapture(e.pointerId); mover(e.clientX); }}
      onPointerMove={(e) => e.currentTarget.hasPointerCapture(e.pointerId) && mover(e.clientX)}>
      <img src={tierra.src} alt={tierra.alt} />
      <img className="ref" src={imagenRef.src} alt={imagenRef.alt} />
      <span className="line" />
      <button type="button" className="handle" role="slider" aria-label={`Drag to compare Earth and ${etiquetaRef}`}
        aria-valuemin={0} aria-valuemax={100} aria-valuenow={Math.round(corte)}
        onKeyDown={(e) => {
          if (e.key === "ArrowLeft") setCorte((c) => Math.max(0, c - 5));
          if (e.key === "ArrowRight") setCorte((c) => Math.min(100, c + 5));
        }}>↔</button>
      <span className="tagimg l">Earth</span>
      <span className="tagimg r">{etiquetaRef}</span>
    </div>
  );
}

function Barras({ filas, lugar, referencia }) {
  return (
    <div className="bars">
      {filas.map(([k, v]) => (
        <div key={k} className="bar bar-4">
          <span className="con-icono"><Icono nombre={ICONO_VAR[k]} size={16} />{VARIABLES[k] ?? k}</span>
          <span className="track"><i style={{ width: `${v * 100}%` }} /></span>
          <output>{Math.round(v * 100)}</output>
          <span className="bar-vals mono">{k in UNIDAD || k === "polvo" ? `${fmt(k, lugar.valores[k])} · ${fmt(k, referencia[k])}` : ""}</span>
        </div>
      ))}
    </div>
  );
}

// Modal sobre el mapa: se recorren los lugares con Previous / Next (o las flechas del teclado) sin cerrarlo.
function Agrandada({ lugar, sitio, referencia, filas, tierraNoLlega, cerrar, anterior, siguiente, posicion }) {
  const s = SITIOS[sitio];
  const ancho = anchoVistaKm(s.cuerpo);
  const [modo, setModo] = useState("lado");
  const boton = useRef(null);
  useEffect(() => { boton.current?.focus(); }, []);
  useEffect(() => {
    const teclas = (e) => {
      if (e.key === "Escape") cerrar();
      if (e.target.getAttribute?.("role") === "slider") return; // las flechas mueven el deslizador
      if (e.key === "ArrowLeft" && anterior) anterior();
      if (e.key === "ArrowRight" && siguiente) siguiente();
    };
    window.addEventListener("keydown", teclas);
    return () => window.removeEventListener("keydown", teclas);
  }, [anterior, siguiente]);
  const tierra = { src: fotoTierra(lugar.lat, lugar.lon, ancho, 960, 720), alt: `Earth, ${lugar.pais}, ${ancho} km wide` };
  const refImg = { src: s.img, alt: `${s.nombre}, ${s.cuerpo}, ${ancho} km wide` };
  return (
    <div className="expand" onClick={(e) => e.target === e.currentTarget && cerrar()}>
     <div className="expand-card" role="dialog" aria-modal="true" aria-labelledby="exp-t">
      <div className="expand-head">
        <div style={{ display: "flex", alignItems: "baseline", gap: 12, flexWrap: "wrap" }}>
          <h2 id="exp-t" className="panel-title">{lugar.pais} vs {s.nombre}</h2>
          <span className="muted" style={{ fontSize: 14 }}>{s.escala ? `Same scale: both views are ${ancho} km wide` : "Reference scale not matched"}</span>
        </div>
        <div style={{ display: "flex", gap: 8, alignItems: "center", flexWrap: "wrap" }}>
          <div className="pager" aria-label="Browse places">
            <button type="button" className="btn btn-secondary" onClick={anterior} disabled={!anterior}>‹ Previous</button>
            {posicion && <span className="note num">{posicion}</span>}
            <button type="button" className="btn btn-secondary" onClick={siguiente} disabled={!siguiente}>Next ›</button>
          </div>
          <div className="tabs" role="tablist" aria-label="Comparison mode" style={{ width: 240 }}>
            <button type="button" role="tab" className="tab" aria-selected={modo === "lado"} onClick={() => setModo("lado")}><Icono nombre="side-by-side" size={16} /> Side by side</button>
            <button type="button" role="tab" className="tab" aria-selected={modo === "desl"} onClick={() => setModo("desl")}><Icono nombre="slider-compare" size={16} /> Slider</button>
          </div>
          <button ref={boton} type="button" className="btn btn-secondary btn-icon" onClick={cerrar} aria-label="Close comparison"><Cerrar /></button>
        </div>
      </div>
      <div className="expand-body">
        {modo === "lado" ? (
          <div className="side">
            {[[tierra, `Earth · ${lugar.pais}`, "Sentinel-2 cloudless 2021 (EOX)"], [refImg, `${s.cuerpo} · ${s.nombre}`, s.credito]].map(([img, t, c]) => (
              <figure key={t}>
                <div className="side-img">
                  <img src={img.src} alt={img.alt} />
                  {s.escala && <span className="esc">{Math.round(ancho / 6)} km<i /></span>}
                </div>
                <figcaption><b>{t}</b><span className="muted">{c}</span></figcaption>
              </figure>
            ))}
          </div>
        ) : (
          <Deslizador tierra={tierra} imagenRef={refImg} etiquetaRef={s.cuerpo} alto="min(70vh, 640px)" />
        )}
        <aside className="expand-side">
          <Puntaje lugar={lugar} nombreRef={s.nombre} cuerpo={s.cuerpo} compacto />
          <h3 className="section-title">Variable by variable <span>this place · {s.nombre}</span></h3>
          <Barras filas={filas} lugar={lugar} referencia={referencia} />
          {tierraNoLlega.length > 0 && (
            <p className="note"><b>Shown, not scored:</b> {tierraNoLlega.map((k) => VARIABLES[k] ?? k).join(", ")}. No place on Earth gets there.</p>
          )}
        </aside>
      </div>
     </div>
    </div>
  );
}

export default function FichaLugar({ lugar, sitio, referencia, vista, setVista, tierraNoLlega, faltan, pesos, cerrar, cambiarSitio, preguntar, siguiente, anterior, posicion, validacion }) {
  const s = SITIOS[sitio];
  const ancho = anchoVistaKm(s.cuerpo);
  const [cerca, setCerca] = useState(null);
  const [robustez, setRobustez] = useState({ estado: "nada" });
  const [grande, setGrande] = useState(false);
  const [alto, setAlto] = useState("40%"); // celular: altura de la ficha (la cambia la línea de arrastre)
  const titulo = useRef(null);

  useEffect(() => {
    titulo.current?.focus();
    setCerca(null);
    setRobustez({ estado: "nada" });
    let vivo = true;
    api.celda(lugar.lat, lugar.lon, sitio).then((c) => vivo && setCerca(c.analogo_cercano)).catch(() => vivo && setCerca({ error: true }));
    return () => { vivo = false; };
  }, [lugar.id, sitio]);

  const filas = Object.entries(lugar.desglose).sort((a, b) => b[1] - a[1]);
  const coincide = filas.filter(([, v]) => v >= 0.75).map(([k]) => k);
  const rompe = filas.filter(([, v]) => v < 0.5).map(([k]) => k);
  const nombre = (k) => (VARIABLES[k] ?? k).toLowerCase();
  const rocaAqui = roca(lugar.valores);
  const valorDe = (k, donde) => (k === "roca" ? roca(donde) : donde[k]);
  const lim = LIMITES[s.cuerpo];

  const bajar = (nombreArchivo, texto, tipo) => {
    const a = document.createElement("a");
    a.href = URL.createObjectURL(new Blob([texto], { type: tipo }));
    a.download = nombreArchivo;
    a.click();
    URL.revokeObjectURL(a.href);
  };
  const base = `analog_atlas_${lugar.lat.toFixed(2)}_${lugar.lon.toFixed(2)}`;
  const datosJson = () => bajar(`${base}.json`, JSON.stringify({ place: { country: lugar.pais, lat: lugar.lat, lon: lugar.lon },
    reference: s.nombre, score: lugar.puntaje, band: tramo(lugar.puntaje), similarity: lugar.desglose, earth_values: lugar.valores,
    reference_values: referencia, earth_never_reaches: tierraNoLlega, sources: "USO_DE_IA_Y_FUENTES.md and datos/FUENTES.md" }, null, 2), "application/json");
  const brief = () => bajar(`${base}_test_brief.txt`, [
    `Analog Atlas test brief: ${lugar.pais} (${coord(lugar.lat, lugar.lon)}) vs ${s.nombre}, ${s.cuerpo}`,
    `Score ${Math.round(lugar.puntaje)} of 100 (${tramo(lugar.puntaje)})`, "",
    ...CHEQUEO.map((k) => `${k === "roca" ? "Rock" : VARIABLES[k]}: here ${k === "roca" ? rocaAqui ?? "n/a" : fmt(k, lugar.valores[k])}, ${s.nombre} ${k === "roca" ? roca(referencia) ?? "n/a" : fmt(k, referencia[k])} ${SIMBOLO[estado(lugar.desglose, k)]}`),
    "", `Not reproduced anywhere on Earth: ${lim.filas.map(([a, b]) => `${a} (${b})`).join("; ")}.`, `Sources: ${lim.fuente}`,
  ].join("\n"), "text/plain");

  const probar = async () => {
    setRobustez({ estado: "cargando" });
    try {
      setRobustez({ estado: "listo", valor: (await api.sensibilidad(sitio, pesos)).retencion });
    } catch (e) {
      setRobustez({ estado: "error", mensaje: e.message });
    }
  };

  const buenoPara = [...new Set(coincide.map((k) => (k === "volcanico" || k === "sedimento" ? "roca" : k)))]
    .filter((k) => BUENO_PARA[k] && !(k === "roca" && !rocaAqui)).map((k) => BUENO_PARA[k](rocaAqui ?? ""));
  const noPara = [...(rompe.some((k) => ["temp_noche", "rango_termico"].includes(k)) || tierraNoLlega.some((k) => ["temp_noche", "rango_termico"].includes(k)) ? ["Deep cold and day–night cycling"] : []),
    ...(rompe.includes("temp_dia") ? ["Matching day temperatures"] : []), `Thin air, ${lim.filas[0][1].split(" ")[0]} gravity, surface radiation`];

  return (
    <>
      <aside className="panel panel-right" aria-labelledby="ficha-t" style={{ "--alto-ficha": alto }}>
        <Asa alto={alto} setAlto={setAlto} cerrado="40%" abierto="100%" variable="--alto-ficha" en=".panel" etiqueta="Drag or tap to resize the place card" />
        <div className="panel-body" style={{ padding: 0, gap: 0 }}>
          <div className="place-hero">
            <div className="side-mini">
              <img src={fotoTierra(lugar.lat, lugar.lon, ancho)} alt={`Earth, ${ancho} km wide around the place`} />
              <img src={s.img} alt={`${s.nombre}, ${s.cuerpo}`} />
              <span className="tagimg l">Earth · {lugar.pais}</span>
              <span className="tagimg r">{s.cuerpo} · {s.nombre}</span>
            </div>
            <button type="button" className="btn btn-secondary expand-btn" onClick={() => setGrande(true)}><Icono nombre="expand" size={16} /> Expand comparison</button>
            <button type="button" className="btn btn-secondary btn-icon close" onClick={cerrar} aria-label="Close place and go back to results"><Cerrar /></button>
          </div>
          <div className="ficha">
            <div className="ficha-top">
              <div style={{ display: "flex", flexDirection: "column", gap: 4, minWidth: 0 }}>
                <h2 id="ficha-t" className="panel-title" tabIndex={-1} ref={titulo}>{lugar.pais}</h2>
                <span className="mono muted">{coord(lugar.lat, lugar.lon)}</span>
              </div>
              <a className="btn btn-secondary" href={enGoogleMaps(lugar.lat, lugar.lon)} target="_blank" rel="noopener noreferrer">
                Google Maps ↗<span className="sr-only"> (new tab)</span>
              </a>
            </div>
            <Puntaje lugar={lugar} nombreRef={s.nombre} cuerpo={s.cuerpo} validacion={validacion} />

            <div className="tabs tabs-4" role="tablist" aria-label="View as">
              {Object.entries(VISTAS).map(([k, v]) => (
                <button key={k} type="button" role="tab" className="tab" aria-selected={vista === k} onClick={() => setVista(k)}>{v}</button>
              ))}
            </div>

            {vista === "educator" && (
              <div className="vista">
                <p><b>Why it looks like {s.nombre}.</b> {coincide.length ? `${coincide.slice(0, 3).map(nombre).join(", ")} ${coincide.length > 1 ? "are" : "is"} close to the real values there.` : "Few variables are close; this is a partial analog."}</p>
                <p><b>Where the analogy breaks.</b> {[...new Set([...rompe, ...tierraNoLlega])].filter((k) => lugar.valores[k] != null && referencia[k] != null).slice(0, 2)
                  .map((k) => `${VARIABLES[k]}: ${fmt(k, lugar.valores[k])} here, ${fmt(k, referencia[k])} on ${s.nombre}.`).join(" ") || `${rompe.map(nombre).join(", ") || "Nothing major in the variables we measure"}.`}</p>
                <div className="limits">{lim.filas.map(([a, b]) => <Fragment key={a}><b>{a}</b><span>{b}</span></Fragment>)}</div>
                <p className="note">{lim.fuente}</p>
                <p className="note" aria-live="polite">{cerca === null ? "Looking for the nearest famous analog…" : cerca.error ? "Nearest famous analog unavailable right now."
                  : `Nearest famous analog: ${cerca.nombre}, ${Math.round(cerca.km).toLocaleString()} km away.`}</p>
                <button type="button" className="btn btn-primary btn-block" onClick={() => setGrande(true)}><Icono nombre="expand" size={16} /> Expand the side-by-side view</button>
              </div>
            )}

            {vista === "researcher" && (
              <div className="vista">
                <h3 className="section-title">Similarity by variable <span>this place · {s.nombre}</span></h3>
                <Barras filas={filas} lugar={lugar} referencia={referencia} />
                {tierraNoLlega.length > 0 && <p className="note"><b>Shown, not scored:</b> {tierraNoLlega.map((k) => VARIABLES[k] ?? k).join(", ")}.</p>}
                {faltan.length > 0 && <p className="note">Not loaded yet: {faltan.map((k) => VARIABLES[k] ?? k).join(", ")}.</p>}
                {sitio === "shackleton" && <p className="note">Shackleton has few reference variables, so many places score high.</p>}
                <details>
                  <summary>Methodology and evidence</summary>
                  <ul>
                    <li>Each 0.25° cell (about 28 km) is compared with the reference variable by variable and combined with a weighted geometric mean, the form of the Earth Similarity Index.</li>
                    <li>Temperatures Earth never reaches are shown but left out of the score.</li>
                    {validacion && <li>Validation: {validacion.top10} of {validacion.total} well-known analog sites rank in Earth's top 10% and {validacion.top20} in the top 20% for at least one reference site. Low scorers are famous for things we do not measure (water chemistry, microbes) or are smaller than our 28 km cells.</li>}
                    <li>Earth: MODIS, ETOPO1, MERRA-2 dust, GLiM rock type. Mars: MEDA, REMS, MOLA, Mastcam. Moon: Diviner, LOLA. Full list: datos/FUENTES.md.</li>
                    <li>28 km cells hide small craters, lava tubes and local terrain; multi-year means hide seasons.</li>
                  </ul>
                </details>
                {robustez.estado !== "nada" && (
                  <p className={robustez.estado === "error" ? "state error" : "state"} role="status">
                    {robustez.estado === "cargando" && "Moving each weight ±20% and re-ranking…"}
                    {robustez.estado === "listo" && `The global top 10 keeps ${Math.round(robustez.valor * 100)}% of its places when each weight moves ±20%.`}
                    {robustez.estado === "error" && robustez.mensaje}
                  </p>
                )}
                <div className="actions">
                  <button type="button" className="btn btn-secondary" onClick={probar} disabled={robustez.estado === "cargando"}>Robustness check</button>
                  <button type="button" className="btn btn-primary" onClick={datosJson}><Icono nombre="download-brief" size={16} /> Data (JSON)</button>
                </div>
              </div>
            )}

            {vista === "testing" && (
              <div className="vista">
                <h3 className="section-title">Ground for your test</h3>
                <div className="check">
                  <span /><span className="note">Here</span><span className="note">{s.nombre.split(" ")[0]}</span><span />
                  {CHEQUEO.map((k) => {
                    const e = estado(lugar.desglose, k);
                    return (
                      <Fragment key={k}>
                        <span className="muted con-icono">
                          <Icono nombre={k === "roca" ? (referencia.sedimento === 1 ? "sedimentary-ground" : "volcanic-rock") : ICONO_VAR[k]} size={16} />
                          {CORTO[k] ?? VARIABLES[k]}
                        </span>
                        <b>{k === "roca" ? rocaAqui?.split(" ")[0] ?? "n/a" : fmt(k, lugar.valores[k])}</b>
                        <span className="muted">{k === "roca" ? roca(referencia)?.split(" ")[0] ?? "n/a" : fmt(k, valorDe(k, referencia))}</span>
                        <span className={`mark ${e}`} aria-label={e === "ok" ? "matches" : e === "ko" ? "does not match" : e === "mid" ? "partly" : "not compared"}>{SIMBOLO[e]}</span>
                      </Fragment>
                    );
                  })}
                </div>
                <div className="verdict">
                  <div><h3 className="ok">Good for</h3><ul>{buenoPara.length ? buenoPara.map(([t, ic]) => <li key={t} className="con-icono"><Icono nombre={ic} size={16} />{t}</li>) : <li className="muted">No strong match</li>}</ul></div>
                  <div><h3 className="ko">Not for</h3><ul>{noPara.map((t) => <li key={t}>{t}</li>)}</ul></div>
                </div>
                <div className="actions">
                  <button type="button" className="btn btn-secondary" onClick={cambiarSitio}><Icono nombre="change-site" size={16} /> Change site</button>
                  <button type="button" className="btn btn-primary" onClick={brief}><Icono nombre="download-brief" size={16} /> Download brief</button>
                </div>
              </div>
            )}

            {vista === "explorer" && (
              <div className="vista">
                <p>{coincide.length ? `Close to ${s.nombre} in ${coincide.slice(0, 2).map(nombre).join(" and ")}.` : `A partial match for ${s.nombre}.`}</p>
                <p className="muted">{rompe.length ? `Different in ${rompe.slice(0, 2).map(nombre).join(" and ")}.` : "No big differences in what we measure."}</p>
                <div className="actions">
                  <button type="button" className="btn btn-secondary" onClick={preguntar}>Refine with Ask</button>
                  <button type="button" className="btn btn-primary" onClick={siguiente} disabled={!siguiente}>Next place</button>
                </div>
              </div>
            )}
          </div>
        </div>
      </aside>
      {/* Portal: el modal va sobre toda la página (también sobre la cabecera), no dentro de la capa del mapa */}
      {grande && createPortal(<Agrandada lugar={lugar} sitio={sitio} referencia={referencia} filas={filas} tierraNoLlega={tierraNoLlega}
        cerrar={() => setGrande(false)} anterior={anterior} siguiente={siguiente} posicion={posicion} />, document.body)}
    </>
  );
}
