// Analog Atlas · frontend/src/components/PanelAsk.jsx
// v1.0 · 2026-11-14 · Isabelita (equipo Ctrl Z)
// Conversación con /api/interpretar. Hoy lee por palabras clave (la conexión con Claude está pendiente y se dice).
// Las opciones de la pregunta aplican filtros reales de pendiente y muestran cuántos lugares quedan.
import { useEffect, useRef, useState } from "react";
import { SITIOS, api } from "../lib/atlas.js";
import { Enviar } from "./Iconos.jsx";

// Mismo orden que OPCIONES en services/interpretar_service.py (pendiente media de celdas de 28 km)
const RANGOS_PENDIENTE = [[0, 0.2], [0.2, 1], [1, null]];

export default function PanelAsk({ consulta, lectura, sitio, aplicarPendiente, cuantos, cambiarSitio }) {
  const [mensajes, setMensajes] = useState(() => [
    { de: "user", texto: consulta },
    { de: "bot", lectura },
  ]);
  const [texto, setTexto] = useState("");
  const [esperando, setEsperando] = useState(false);
  const [elegida, setElegida] = useState(null);
  const fin = useRef(null);
  useEffect(() => fin.current?.scrollIntoView({ block: "end" }), [mensajes, elegida]);

  const elegir = (i, opcion) => {
    setElegida(i);
    const n = aplicarPendiente(RANGOS_PENDIENTE[i]);
    setMensajes((m) => [...m, { de: "user", texto: opcion }, { de: "bot", aplicado: n }]);
  };

  const enviar = async (e) => {
    e.preventDefault();
    const t = texto.trim();
    if (!t || esperando) return;
    setTexto("");
    setElegida(null);
    setMensajes((m) => [...m, { de: "user", texto: t }]);
    setEsperando(true);
    try {
      const l = await api.interpretar(t);
      setMensajes((m) => [...m, { de: "bot", lectura: l }]);
    } catch (err) {
      setMensajes((m) => [...m, { de: "bot", error: err.message }]);
    } finally {
      setEsperando(false);
    }
  };

  return (
    <>
      <div className="panel-body" id="panel-ask">
        <p className="note">Keyword assistant. The Claude connection is not set up yet, so answers come from fixed rules.</p>
        <div className="chat" aria-live="polite">
          {mensajes.map((m, i) => {
            if (m.de === "user") return <p key={i} className="msg user">{m.texto}</p>;
            if (m.error) return <p key={i} className="msg bot" role="alert">{m.error}</p>;
            if (m.aplicado != null) return (
              <p key={i} className="msg bot"><b>Filters applied.</b> {m.aplicado.toLocaleString()} matching places on the map.</p>
            );
            const l = m.lectura;
            const ultimo = i === mensajes.length - 1 || mensajes.slice(i + 1).every((x) => x.de !== "bot" || x.aplicado != null);
            return (
              <div key={i} className="chat">
                <p className="msg bot">{l.resumen}{l.pregunta ? ` ${l.pregunta}` : ""}</p>
                {l.sitio !== sitio && (
                  <button type="button" className="btn btn-secondary" onClick={() => cambiarSitio(l.sitio)}>
                    Compare with {SITIOS[l.sitio].nombre} instead
                  </button>
                )}
                {ultimo && l.opciones?.length > 0 && (
                  <div className="choices">
                    {l.opciones.map((o, k) => (
                      <button key={o} type="button" className="btn btn-secondary" aria-pressed={elegida === k} onClick={() => elegir(k, o)}>{o}</button>
                    ))}
                  </div>
                )}
              </div>
            );
          })}
          {esperando && <div className="bar-loading" aria-label="Reading your message" />}
          <span ref={fin} />
        </div>
        <p className="note num">{cuantos.toLocaleString()} places match the current filters.</p>
      </div>
      <form className="ask-form" onSubmit={enviar}>
        <label htmlFor="ask" className="sr-only">Ask a follow-up</label>
        <input id="ask" className="input" value={texto} onChange={(e) => setTexto(e.target.value)} placeholder="Ask a follow-up…" maxLength={500} />
        <button type="submit" className="btn btn-primary btn-icon" aria-label="Send" disabled={!texto.trim() || esperando}><Enviar /></button>
      </form>
    </>
  );
}
