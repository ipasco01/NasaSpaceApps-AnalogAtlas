// src/components/AskAIPanel.jsx
// Panel flotante de la IA. Soporta la rama de pregunta aclaratoria (brecha C, campo "pregunta").
// Si la IA devuelve opciones, se muestran como chips; al elegir, se re-llama /interpretar con el texto
// enriquecido. Nunca se depende solo de la IA: si falla, el fallback sin IA ya viene en el backend.

import { useState } from "react";
import { interpretar, buscar } from "../lib/atlasApi";

export default function AskAIPanel({ atlas }) {
  const [msg, setMsg] = useState("");
  const [chat, setChat] = useState([]);

  const send = async (texto) => {
    setChat((c) => [...c, { role: "user", texto }]);
    const out = await interpretar(texto);
    setChat((c) => [...c, { role: "ai", ...out }]);
    atlas.setSitio(out.sitio);
    atlas.setPesos(out.pesos);
    atlas.setDescubrimiento(out.descubrimiento);
    const res = await buscar({ sitio: out.sitio, pesos: out.pesos, descubrimiento: out.descubrimiento, top: 10 });
    atlas.setResult(res);
  };

  return (
    <div className="aa-ai">
      <div className="aa-ai-head">Ask AI</div>
      <div className="aa-ai-body">
        {chat.map((m, i) => (
          <div key={i} className={m.role === "user" ? "aa-ai-user" : "aa-ai-ai"}>
            {m.role === "user" ? m.texto : m.resumen}
            {/* Follow-up: chips de opciones (captura 6) */}
            {m.pregunta && (
              <div className="aa-chips">
                <p className="aa-chips-q">{m.pregunta}</p>
                {m.opciones.map((op) => (
                  <button key={op} className="aa-chip" onClick={() => send(op)}>{op}</button>
                ))}
              </div>
            )}
          </div>
        ))}
      </div>
      <form className="aa-ai-form" onSubmit={(e) => { e.preventDefault(); if (msg.trim()) { send(msg); setMsg(""); } }}>
        <input value={msg} onChange={(e) => setMsg(e.target.value)} placeholder="Ask a follow-up..." />
        <button type="submit" aria-label="Send">Send</button>
      </form>
    </div>
  );
}
