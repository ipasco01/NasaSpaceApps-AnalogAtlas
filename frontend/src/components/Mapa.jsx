// Analog Atlas · frontend/src/components/Mapa.jsx
// v1.0 · 2026-11-14 · Isabelita (equipo Ctrl Z)
// Mapa satelital a pantalla completa (Sentinel-2 cloudless, EOX) con los lugares como puntos.
// Más opaco = más parecido. Clic en un punto abre su ficha. El teclado usa la lista de resultados.
import { useEffect, useRef } from "react";
import maplibregl from "maplibre-gl";
import "maplibre-gl/dist/maplibre-gl.css";
import { CREDITO_EOX, EOX_TESELAS } from "../lib/atlas.js";

const ESTILO = {
  version: 8,
  sources: { eox: { type: "raster", tiles: [EOX_TESELAS], tileSize: 256, maxzoom: 14 } },
  layers: [{ id: "eox", type: "raster", source: "eox" }],
};

const geojson = (lugares) => ({
  type: "FeatureCollection",
  features: lugares.map((l) => ({
    type: "Feature",
    id: l.id,
    geometry: { type: "Point", coordinates: [l.lon, l.lat] },
    properties: { id: l.id, puntaje: l.puntaje, pais: l.pais },
  })),
});

// Tarjeta al pasar el mouse: condiciones típicas del lugar (medias 2018-2023) junto a las del sitio de referencia.
const esc = (t) => String(t).replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" })[c]);
const FILAS = [["temp_dia", "Day", (v) => `${Math.round(v)} °C`], ["temp_noche", "Night", (v) => `${Math.round(v)} °C`],
  ["pendiente", "Slope", (v) => `${v.toFixed(1)}°`], ["elevacion", "Elevation", (v) => `${Math.round(v).toLocaleString()} m`],
  ["polvo", "Dust", (v) => v.toFixed(2)]];
const roca = (v) => (v?.volcanico === 1 ? "Volcanic" : v?.sedimento === 1 ? "Sediment" : v?.volcanico === 0 ? "Other" : "n/a");
function tarjeta(l, ref) {
  const filas = FILAS.filter(([k]) => l.valores[k] != null)
    .map(([k, n, f]) => `<tr><th>${n}</th><td>${f(l.valores[k])}</td><td>${ref?.valores?.[k] != null ? f(ref.valores[k]) : "n/a"}</td></tr>`).join("");
  return `<div class="hover-card"><div class="hc-top"><b>${esc(l.pais)}</b><strong>${Math.round(l.puntaje)}</strong></div>
    <table><thead><tr><th></th><th>Here</th><th>${esc(ref?.nombre ?? "Reference")}</th></tr></thead><tbody>${filas}
    <tr><th>Rock</th><td>${roca(l.valores)}</td><td>${roca(ref?.valores)}</td></tr></tbody></table>
    <p>Typical values, 2018–2023 means. Click to open.</p></div>`;
}

export default function Mapa({ lugares, elegido, alElegir, acento, encuadre, referencia, conocidos = [], alConocido }) {
  const conocidoRef = useRef(alConocido);
  conocidoRef.current = alConocido;
  const porId = useRef(new Map());
  porId.current = new Map(lugares.map((l) => [l.id, l]));
  const refRef = useRef(referencia);
  refRef.current = referencia;
  const caja = useRef(null);
  const mapa = useRef(null);
  const listo = useRef(false);
  const ultimoEncuadre = useRef(null); // encuadre = id de la búsqueda: se encuadra una vez por búsqueda nueva
  const elegirRef = useRef(alElegir);
  elegirRef.current = alElegir;

  useEffect(() => {
    const m = new maplibregl.Map({ container: caja.current, style: ESTILO, center: [20, 15], zoom: 1.4,
      attributionControl: false, dragRotate: false, pitchWithRotate: false });
    m.addControl(new maplibregl.NavigationControl({ showCompass: false }), "bottom-right");
    const aviso = new maplibregl.Popup({ closeButton: false, closeOnClick: false, offset: 12 });
    m.on("load", () => {
      m.addSource("lugares", { type: "geojson", data: geojson([]) });
      m.addLayer({ id: "lugares", type: "circle", source: "lugares", paint: {
        "circle-radius": ["interpolate", ["linear"], ["zoom"], 1, 3, 4, 5, 7, 6],
        "circle-color": acento, "circle-stroke-color": "#ffffff", "circle-stroke-width": 1.5,
        "circle-opacity": ["interpolate", ["linear"], ["get", "puntaje"], 0, 0.35, 100, 1],
        "circle-stroke-opacity": ["interpolate", ["linear"], ["get", "puntaje"], 0, 0.35, 100, 1] } });
      m.addLayer({ id: "elegido", type: "circle", source: "lugares", filter: ["==", ["get", "id"], -1], paint: {
        "circle-radius": 12, "circle-color": acento, "circle-stroke-color": "#ffffff", "circle-stroke-width": 3 } });
      m.on("click", "lugares", (e) => elegirRef.current(e.features[0].properties.id));
      m.on("mouseenter", "lugares", (e) => {
        m.getCanvas().style.cursor = "pointer";
        const p = e.features[0].properties;
        const l = porId.current.get(p.id);
        if (l) aviso.setLngLat(e.lngLat).setHTML(tarjeta(l, refRef.current)).addTo(m);
      });
      m.on("mouseleave", "lugares", () => { m.getCanvas().style.cursor = ""; aviso.remove(); });
      // Análogos ya estudiados: siempre visibles como anillo blanco, aunque el modo descubrimiento los saque de la lista
      m.addSource("conocidos", { type: "geojson", data: { type: "FeatureCollection", features: [] } });
      m.addLayer({ id: "conocidos", type: "circle", source: "conocidos", paint: {
        "circle-radius": 8, "circle-color": "#ffffff", "circle-opacity": 0.2, "circle-stroke-color": "#ffffff", "circle-stroke-width": 3 } });
      m.on("click", "conocidos", (e) => { const p = e.features[0].properties; conocidoRef.current?.(p.lat, p.lon); });
      m.on("mouseenter", "conocidos", (e) => {
        m.getCanvas().style.cursor = "pointer";
        const p = e.features[0].properties;
        aviso.setLngLat(e.lngLat).setHTML(`<div class="hover-card"><span class="note">Well-known analog site</span><b>${esc(p.nombre)}</b>`
          + `${p.por_que ? `<p>${esc(p.por_que)}. <i>${esc(p.fuente)}</i></p>` : ""}<p>Click to score it against your reference site.</p></div>`).addTo(m);
      });
      m.on("mouseleave", "conocidos", () => { m.getCanvas().style.cursor = ""; aviso.remove(); });
      listo.current = true;
      m.fire("datos-listos");
    });
    mapa.current = m;
    return () => m.remove();
  }, []);

  useEffect(() => {
    const m = mapa.current;
    const aplicar = () => m.getSource("conocidos").setData({ type: "FeatureCollection", features: conocidos.map((c) => ({
      type: "Feature", geometry: { type: "Point", coordinates: [c.lon, c.lat] }, properties: c })) });
    if (listo.current) aplicar();
    else m.once("datos-listos", aplicar);
  }, [conocidos]);

  // Puntos y encuadre cuando cambian los resultados
  useEffect(() => {
    const m = mapa.current;
    const aplicar = () => {
      m.getSource("lugares").setData(geojson(lugares));
      m.setPaintProperty("lugares", "circle-color", acento);
      m.setPaintProperty("elegido", "circle-color", acento);
      if (encuadre !== ultimoEncuadre.current && lugares.length) {
        ultimoEncuadre.current = encuadre;
        const b = new maplibregl.LngLatBounds();
        lugares.forEach((l) => b.extend([l.lon, l.lat]));
        const ancho = window.innerWidth > 1024;
        // En celular el panel de resultados tapa la mitad de abajo del mapa
        m.fitBounds(b, { padding: { top: 48, bottom: ancho ? 48 : Math.round(window.innerHeight * 0.55), left: ancho ? 420 : 24, right: ancho ? 48 : 24 },
          maxZoom: 6, duration: 600 });
      }
    };
    if (listo.current) aplicar();
    else m.once("datos-listos", aplicar);
  }, [lugares, acento, encuadre]);

  // Punto elegido: resaltado y centrado
  useEffect(() => {
    const m = mapa.current;
    const aplicar = () => {
      m.setFilter("elegido", ["==", ["get", "id"], elegido ? elegido.id : -1]);
      if (elegido) m.easeTo({ center: [elegido.lon, elegido.lat], zoom: Math.max(m.getZoom(), 6),
        padding: { right: window.innerWidth > 1024 ? 460 : 0, left: window.innerWidth > 1024 ? 400 : 0 }, duration: 600 });
    };
    if (listo.current) aplicar();
    else m.once("datos-listos", aplicar);
  }, [elegido]);

  return (
    <>
      <div ref={caja} className="map" role="region" aria-label="Satellite map of matching places" />
      <div className="map-legend" aria-label="Map legend">
        <span><i className="dot" /> Best matches (brighter scores higher)</span>
        <span><i className="ring" /> Well-known analog sites</span>
      </div>
      <p className="map-credit">{CREDITO_EOX}</p>
    </>
  );
}
