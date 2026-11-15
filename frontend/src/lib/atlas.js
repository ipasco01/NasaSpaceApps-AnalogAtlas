// Analog Atlas · frontend/src/lib/atlas.js
// v1.1 · 2026-11-15 · Isabelita (equipo Ctrl Z) · enlace a Google Maps en satelital plano
// Catálogos de la interfaz, cliente de la API y utilidades. Los números vienen de la API; aquí solo hay textos y
// las fuentes de los límites físicos (NASA Fact Sheets, Hassler et al. 2014, Zhang et al. 2020).

export const SITIOS = {
  jezero: { nombre: "Jezero crater", cuerpo: "Mars", lat: 18.44, lon: 77.45, sub: "Mars · Perseverance",
    resumen: "18.44° N · river delta on a volcanic crater floor · Perseverance", img: "/img/r_jezero.jpg",
    credito: "Viking MDIM 2.1, NASA Mars Trek", escala: true },
  gale: { nombre: "Gale crater", cuerpo: "Mars", lat: -4.59, lon: 137.44, sub: "Mars · Curiosity",
    resumen: "4.59° S · ancient lake sediments · Curiosity", img: "/img/r_gale.jpg",
    credito: "Viking MDIM 2.1, NASA Mars Trek", escala: true },
  shackleton: { nombre: "Shackleton rim", cuerpo: "Moon", lat: -89.67, lon: 129.78, sub: "Moon · relief, not a photo",
    resumen: "89.67° S · stable ice on 40% of the rim (Diviner)", img: "/img/r_shackleton.jpg",
    credito: "LRO shaded relief in false color, NASA (scale not matched)", escala: false },
  marius_hills: { nombre: "Marius Hills", cuerpo: "Moon", lat: 14.09, lon: -56.78, sub: "Moon · lava tubes",
    resumen: "14.09° N · volcanic domes and a lava tube pit", img: "/img/r_marius.jpg",
    credito: "LRO WAC mosaic, NASA Moon Trek", escala: true },
};

// El rol ya no cambia el puntaje (un solo puntaje para todos): solo qué muestra la ficha del lugar.
export const VISTAS = { educator: "Educator", researcher: "Researcher", testing: "Mission test", explorer: "Explorer" };

export const VARIABLES = {
  ndvi: "No vegetation", arido: "Barren ground", rango_termico: "Day–night swing", temp_noche: "Night temperature",
  temp_dia: "Day temperature", pendiente: "Slope", hielo: "Surface ice", permafrost_proxy: "Frozen ground",
  lluvia: "Dryness", polvo: "Dust in the air", nieve: "Snow", elevacion: "Elevation", volcanico: "Volcanic rock",
  sedimento: "Sedimentary ground",
};

// Ícono de cada variable (views/assets/icons, generados en components/IconosAtlas.jsx)
export const ICONO_VAR = {
  ndvi: "no-vegetation", arido: "barren-ground", rango_termico: "day-night-swing", temp_noche: "night-temperature",
  temp_dia: "day-temperature", pendiente: "slope", hielo: "surface-ice", permafrost_proxy: "frozen-ground", lluvia: "dryness",
  polvo: "dust", elevacion: "elevation", volcanico: "volcanic-rock", sedimento: "sedimentary-ground",
};

export const LIMITES = {
  Mars: { filas: [["Gravity", "0.379 g on Mars vs 1 g"], ["Air pressure", "about 0.6% of Earth's"],
    ["Surface radiation", "about 0.67 mSv per day"]],
    fuente: "NASA Mars Fact Sheet; Curiosity RAD (Hassler et al. 2014, Science)." },
  Moon: { filas: [["Gravity", "0.165 g on the Moon vs 1 g"], ["Atmosphere", "none, exosphere only"],
    ["Surface radiation", "about 1.37 mSv per day"]],
    fuente: "NASA Moon Fact Sheet; Chang'e 4 LND (Zhang et al. 2020, Science Advances)." },
};

export const TRAMOS = [[75, "Strong analog"], [50, "Good analog"], [25, "Partial analog"], [0, "Weak analog"]];
export const tramo = (p) => TRAMOS.find(([min]) => p >= min)[1];

export const coord = (lat, lon) =>
  `${Math.abs(lat).toFixed(2)}° ${lat >= 0 ? "N" : "S"}, ${Math.abs(lon).toFixed(2)}° ${lon >= 0 ? "E" : "W"}`;


// Mismo cálculo que services/geo.py: foto Sentinel-2 cloudless (EOX) centrada, con el ancho real en km.
const EOX_WMS = "https://tiles.maps.eox.at/wms?SERVICE=WMS&VERSION=1.1.1&REQUEST=GetMap&LAYERS=s2cloudless-2021" +
  "&SRS=EPSG:4326&FORMAT=image/jpeg&STYLES=";
export function fotoTierra(lat, lon, anchoKm, anchoPx = 480, altoPx = 360) {
  const dlon = anchoKm / (111.32 * Math.max(Math.cos((lat * Math.PI) / 180), 0.05));
  const dlat = (anchoKm * altoPx) / anchoPx / 111.2;
  const bbox = [lon - dlon / 2, lat - dlat / 2, lon + dlon / 2, lat + dlat / 2].map((v) => v.toFixed(4)).join(",");
  return `${EOX_WMS}&BBOX=${bbox}&WIDTH=${anchoPx}&HEIGHT=${altoPx}`;
}
// Google Maps con un pin en el lugar (URL pública documentada de Maps; solo lleva las coordenadas)
// Vista satelital plana desde arriba (la búsqueda abría el 3D de Google, con el relieve deformado)
export const enGoogleMaps = (lat, lon) => `https://www.google.com/maps/@?api=1&map_action=map&center=${lat.toFixed(4)},${lon.toFixed(4)}&zoom=11&basemap=satellite`;
export const anchoVistaKm = (cuerpo) => (cuerpo === "Mars" ? 120 : 60);

export const EOX_TESELAS = "https://tiles.maps.eox.at/wmts/1.0.0/s2cloudless-2021_3857/default/g/{z}/{y}/{x}.jpg";
export const CREDITO_EOX = "Sentinel-2 cloudless 2021 by EOX IT Services GmbH (s2maps.eu), contains modified Copernicus Sentinel data 2021";
export const RELIEVE_TESELAS = "https://elevation-tiles-prod.s3.amazonaws.com/terrarium/{z}/{x}/{y}.png";
export const CREDITO_RELIEVE = "3D terrain: Terrain Tiles (Mapzen, AWS Open Data), from SRTM, ETOPO1 and other sources";

// ---------------------------------------------------------------- API (misma dirección que la página)
async function pedir(ruta, opciones) {
  let r;
  try {
    r = await fetch(ruta, opciones);
  } catch {
    throw new Error("The Analog Atlas server is not reachable. Check that it is running and try again.");
  }
  if (!r.ok) {
    const detalle = await r.text();
    throw new Error(`The server answered ${r.status}. ${detalle.slice(0, 160)}`);
  }
  return r.json();
}
const post = (ruta, cuerpo) =>
  pedir(ruta, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(cuerpo) });

export const api = {
  salud: () => pedir("/health"),
  referencias: () => pedir("/api/referencias"),
  interpretar: (texto) => post("/api/interpretar", { texto }),
  buscar: (cuerpo) => post("/api/buscar", cuerpo),
  conocidos: () => pedir("/api/conocidos"),
  validacion: () => pedir("/api/validacion"),
  celda: (lat, lon, sitio) => pedir(`/api/celda?lat=${lat}&lon=${lon}&sitio=${encodeURIComponent(sitio)}`),
  sensibilidad: (sitio, pesos) => post("/api/sensibilidad", { sitio, pesos, n_top: 10 }),
};
