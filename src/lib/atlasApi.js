cat > src/lib/atlasApi.js << 'EOF'
const API_BASE = import.meta.env.VITE_API_BASE || "http://localhost:8000";

export async function getReferencias() {
  const r = await fetch(`${API_BASE}/api/referencias`);
  if (!r.ok) throw new Error("GET /api/referencias fallo: " + r.status);
  return r.json();
}

export async function interpretar(texto) {
  const r = await fetch(`${API_BASE}/api/interpretar`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ texto }),
  });
  if (!r.ok) throw new Error("POST /api/interpretar fallo: " + r.status);
  return r.json();
}

export async function buscar({ sitio, pesos = {}, imprescindibles = [], descubrimiento = false, top = 10 }) {
  const r = await fetch(`${API_BASE}/api/buscar`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ sitio, pesos, imprescindibles, descubrimiento, top }),
  });
  if (!r.ok) throw new Error("POST /api/buscar fallo: " + r.status);
  return r.json();
}

export function colorTramo(tramo) {
  switch (tramo) {
    case "Muy buen análogo":
    case "Strong analog":
      return "var(--aa-tramo-alto)";
    case "Bueno":
    case "Good analog":
      return "var(--aa-tramo-medio)";
    case "Parcial":
    case "Partial analog":
      return "var(--aa-tramo-bajo)";
    default:
      return "var(--aa-tramo-debil)";
  }
}
EOF
