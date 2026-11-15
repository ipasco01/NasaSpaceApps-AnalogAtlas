// Analog Atlas · frontend/src/App.jsx
// v2.2 · 2026-11-15 · Isabelita (equipo Ctrl Z) · capa de tubos de lava conocidos en el mapa
// Flujo de 4 pasos: 1 Search (portada) · 2 Compare (globos 3D de Marte y la Luna) · 3 Explore (mapa satelital a
// pantalla completa con filtros, resultados, Ask y "Check a place") · 4 Place (ficha con "View as").
// Un solo puntaje para todos (pesos base del cuerpo); el rol solo cambia qué muestra la ficha. Todo lo calcula la API.
import { useEffect, useMemo, useState } from "react";
import Asa from "./components/Asa.jsx";
import Cabecera from "./components/Cabecera.jsx";
import FichaLugar from "./components/FichaLugar.jsx";
import Globo from "./components/Globo.jsx";
import Icono from "./components/IconosAtlas.jsx";
import Mapa from "./components/Mapa.jsx";
import PanelAsk from "./components/PanelAsk.jsx";
import PanelFiltros from "./components/PanelFiltros.jsx";
import PasoCompare from "./components/PasoCompare.jsx";
import Portada from "./components/Portada.jsx";
import Recorrido, { recorridoVisto } from "./components/Recorrido.jsx";
import { SITIOS, api } from "./lib/atlas.js";

const TOP = 3000;
const TEXTURA = { Mars: "/img/mars_2k.jpg", Moon: "/img/moon_2k.jpg" };
const POR_PAGINA = 20;

function leer(clave, defecto) {
  try {
    return localStorage.getItem(clave) || defecto;
  } catch {
    return defecto;
  }
}
function guardar(clave, valor) {
  try { localStorage.setItem(clave, valor); } catch { /* sin almacenamiento: dura la sesión */ }
}

function limitesDe(lugares) {
  const lim = {};
  for (const [k, paso] of [["temp_dia", 1], ["elevacion", 50], ["pendiente", 0.1]]) {
    const v = lugares.map((l) => l.valores[k]).filter((x) => x != null);
    if (v.length) lim[k] = [Math.floor(Math.min(...v) / paso) * paso, Math.ceil(Math.max(...v) / paso) * paso].map((x) => +x.toFixed(1));
  }
  return lim;
}
const filtrosDe = (lim) => ({ ...Object.fromEntries(Object.entries(lim).map(([k, v]) => [k, [...v]])), roca: "any" });
function pasa(l, f) {
  for (const k of ["temp_dia", "elevacion", "pendiente"]) {
    const v = l.valores[k];
    if (f[k] && v != null && (v < f[k][0] || v > f[k][1])) return false;
  }
  return f.roca === "any" || l.valores[f.roca] === 1;
}

export default function App() {
  const [tema, setTema] = useState(() => leer("aa-tema", "light"));
  const [vista, setVista] = useState(() => leer("aa-vista", "educator"));
  const [paso, setPaso] = useState(1);
  const [consulta, setConsulta] = useState("");
  const [lectura, setLectura] = useState(null);
  const [sitio, setSitio] = useState("jezero");
  const [descubrimiento, setDescubrimiento] = useState(true);
  const [refs, setRefs] = useState(null);
  const [conocidos, setConocidos] = useState([]);
  const [tubos, setTubos] = useState([]);
  const [validacion, setValidacion] = useState(null);
  const [res, setRes] = useState(null);
  const [faltan, setFaltan] = useState([]);
  const [cargando, setCargando] = useState(false);
  const [error, setError] = useState("");
  const [filtros, setFiltros] = useState({ roca: "any" });
  const [elegidoId, setElegidoId] = useState(null);
  const [externo, setExterno] = useState(null);
  const [pestana, setPestana] = useState("filtros");
  const [altoRes, setAltoRes] = useState("25%"); // celular: altura del panel de resultados
  const [mostrar, setMostrar] = useState(POR_PAGINA);
  const [recorrido, setRecorrido] = useState(false);
  const [guia, setGuia] = useState(false); // recorrido centrado, abierto a pedido
  const [acento, setAcento] = useState("#5b4cdb");

  useEffect(() => {
    document.documentElement.dataset.theme = tema;
    guardar("aa-tema", tema);
    setAcento(getComputedStyle(document.documentElement).getPropertyValue("--accent").trim());
  }, [tema]);
  useEffect(() => guardar("aa-vista", vista), [vista]);
  // Celular: al abrir un lugar la lista baja, para que no queden dos hojas apiladas sobre el mapa
  useEffect(() => { if (paso === 4) setAltoRes("25%"); }, [paso, elegidoId]);
  useEffect(() => {
    if (paso >= 3 && !conocidos.length) api.conocidos().then(setConocidos).catch(() => {});
    if (paso >= 3 && !tubos.length) api.tubos().then(setTubos).catch(() => {});
    if (!validacion) api.validacion().then(setValidacion).catch(() => {});
  }, [paso, conocidos.length, tubos.length, validacion]);

  // Datos de referencia (valores medidos de cada sitio) para el panel del paso 2 y la ficha
  useEffect(() => {
    if (paso === 2 && !refs) {
      api.referencias().then((r) => setRefs(Object.fromEntries(r.map((x) => [x.sitio, x])))).catch((e) => setError(e.message));
    }
  }, [paso, refs]);

  const limites = useMemo(() => (res ? limitesDe(res.lugares) : {}), [res]);
  const filtrados = useMemo(() => (res ? res.lugares.filter((l) => pasa(l, filtros)) : []), [res, filtros]);
  const elegido = useMemo(() => res?.lugares.find((l) => l.id === elegidoId) ?? (externo?.id === elegidoId ? externo : null), [res, elegidoId, externo]);
  const cambiarTema = () => setTema(tema === "light" ? "dark" : "light");

  const inicio = () => { setPaso(1); setRes(null); setElegidoId(null); setExterno(null); setError(""); setRecorrido(false); };

  const leerTexto = async (texto) => {
    setCargando(true); setError("");
    try {
      const l = await api.interpretar(texto);
      setConsulta(texto); setLectura(l); setSitio(l.sitio); setPaso(2);
    } catch (e) {
      setError(e.message);
    } finally {
      setCargando(false);
    }
  };

  const buscar = async (s, desc = descubrimiento) => {
    setCargando(true); setError("");
    try {
      const referencias = refs ?? Object.fromEntries((await api.referencias()).map((x) => [x.sitio, x]));
      if (!refs) setRefs(referencias);
      if (!faltan.length) api.salud().then((h) => setFaltan(h.faltan)).catch(() => {});
      const datos = await api.buscar({ sitio: s, pesos: referencias[s].pesos_base, imprescindibles: [], descubrimiento: desc, top: TOP });
      setSitio(s); setDescubrimiento(desc); setRes({ ...datos, clave: Date.now() });
      setFiltros(filtrosDe(limitesDe(datos.lugares)));
      setElegidoId(null); setExterno(null); setMostrar(POR_PAGINA); setPestana("filtros");
      setPaso(3);
      setRecorrido(!recorridoVisto());
    } catch (e) {
      setError(e.message);
    } finally {
      setCargando(false);
    }
  };

  const elegir = (id) => { setElegidoId(id); setPaso(4); setRecorrido(false); };
  const cerrarFicha = () => { setElegidoId(null); setPaso(3); };
  const irA = (n) => (n === 1 ? inicio() : n === 2 ? (setElegidoId(null), setPaso(2)) : cerrarFicha());

  const revisarLugar = async (lat, lon) => {
    const l = await api.celda(lat, lon, sitio);
    setExterno(l); setElegidoId(l.id); setPaso(4); setRecorrido(false);
  };

  const aplicarPendiente = ([a, b]) => {
    const lim = limites.pendiente ?? [0, 10];
    const nuevo = { ...filtros, pendiente: [Math.max(a, lim[0]), b == null ? lim[1] : Math.min(b, lim[1])] };
    setFiltros(nuevo);
    return res.lugares.filter((l) => pasa(l, nuevo)).length;
  };

  const indice = filtrados.findIndex((l) => l.id === elegidoId);
  const siguiente = indice >= 0 && indice < filtrados.length - 1 ? () => elegir(filtrados[indice + 1].id) : null;
  const anterior = indice > 0 ? () => elegir(filtrados[indice - 1].id) : null;
  const posicion = indice >= 0 ? `${indice + 1} of ${filtrados.length.toLocaleString()}` : null;

  const verGuia = () => { setRecorrido(false); setGuia(true); };
  const guiaAbierta = guia && <Recorrido centrado validacion={validacion} cerrar={() => setGuia(false)} />;

  if (paso === 1) {
    return (
      <>
        <Portada buscar={leerTexto} cargando={cargando} error={error} tema={tema} cambiarTema={cambiarTema} verGuia={verGuia} />
        {guiaAbierta}
      </>
    );
  }

  return (
    <>
      <Cabecera paso={paso} irA={irA} alInicio={inicio} tema={tema} cambiarTema={cambiarTema} verRecorrido={verGuia} />
      {guiaAbierta}
      {paso === 2 ? (
        <PasoCompare consulta={consulta} sitioSugerido={sitio} referencias={refs} continuar={(s) => buscar(s)}
          cargando={cargando} error={error} acento={acento} />
      ) : (
        <main className="stage" style={{ "--alto-res": altoRes }}>
          <Mapa lugares={filtrados} elegido={elegido} alElegir={elegir} acento={acento} encuadre={res?.clave}
            referencia={refs ? { nombre: SITIOS[sitio].nombre, valores: refs[sitio].valores } : null}
            conocidos={conocidos} tubos={tubos} alConocido={revisarLugar} />
          {res && (
            <aside className="panel panel-left" aria-labelledby="panel-t">
              <Asa alto={altoRes} setAlto={setAltoRes} cerrado="25%" abierto="75%" variable="--alto-res" en=".stage" etiqueta="Drag or tap to resize the results" />
              {altoRes === "25%" && (
                <button type="button" className="btn btn-primary solo-movil ver-top" onClick={() => setAltoRes("75%")}>See top 10 results</button>
              )}
              <div className="panel-head">
                <div className="ref-card">
                  <Globo compacto textura={TEXTURA[SITIOS[sitio].cuerpo]} nombre={SITIOS[sitio].cuerpo} acento={acento} elegido={sitio}
                    sitios={Object.entries(SITIOS).filter(([, x]) => x.cuerpo === SITIOS[sitio].cuerpo).map(([clave, x]) => ({ clave, ...x }))}
                    alElegir={(s) => s !== sitio && !cargando && buscar(s)} />
                  <div style={{ display: "flex", flexDirection: "column", gap: 4, minWidth: 0 }}>
                    <span className="note">Comparing with</span>
                    <h1 id="panel-t" className="panel-title">{SITIOS[sitio].nombre}, {SITIOS[sitio].cuerpo}</h1>
                    <p className="note num">{res.total_match.toLocaleString()} land cells score 50 or more</p>
                    <button type="button" className="btn btn-ghost" style={{ alignSelf: "flex-start", height: 32, padding: 0 }}
                      onClick={() => { setElegidoId(null); setPaso(2); }}><Icono nombre="change-site" size={16} /> Change site</button>
                  </div>
                </div>
                <div className="tabs" role="tablist" aria-label="Panel">
                  <button type="button" role="tab" className="tab" aria-selected={pestana === "filtros"} aria-controls="panel-filtros" onClick={() => setPestana("filtros")}>Results</button>
                  <button type="button" role="tab" className="tab" aria-selected={pestana === "ask"} aria-controls="panel-ask" onClick={() => setPestana("ask")}>Ask</button>
                </div>
              </div>
              {error && <p role="alert" className="state error" style={{ margin: 16 }}>{error}</p>}
              {cargando && <div className="bar-loading" style={{ margin: "0 16px" }} aria-label="Scoring land cells" />}
              {pestana === "filtros" ? (
                <PanelFiltros limites={limites} filtros={filtros} setFiltros={setFiltros} filtrados={filtrados} total={res.lugares.length}
                  elegido={elegido} alElegir={elegir} mostrar={mostrar} setMostrar={setMostrar} limpiar={() => setFiltros(filtrosDe(limites))}
                  descubrimiento={descubrimiento} cambiarDescubrimiento={(v) => buscar(sitio, v)} cargando={cargando} revisarLugar={revisarLugar} conocidos={conocidos} />
              ) : (
                <PanelAsk consulta={consulta} lectura={lectura} sitio={sitio} aplicarPendiente={aplicarPendiente} cuantos={filtrados.length}
                  cambiarSitio={(s) => buscar(s)} />
              )}
            </aside>
          )}
          {paso === 3 && recorrido && <Recorrido validacion={validacion} cerrar={() => setRecorrido(false)} />}
          {paso === 4 && elegido && refs && (
            <FichaLugar lugar={elegido} sitio={sitio} referencia={refs[sitio].valores} vista={vista} setVista={setVista}
              tierraNoLlega={res.tierra_no_llega} faltan={faltan} pesos={refs[sitio].pesos_base} cerrar={cerrarFicha}
              cambiarSitio={() => { setElegidoId(null); setPaso(2); }} preguntar={() => { setPestana("ask"); cerrarFicha(); }} siguiente={siguiente} anterior={anterior} posicion={posicion} validacion={validacion} />
          )}
        </main>
      )}
    </>
  );
}
