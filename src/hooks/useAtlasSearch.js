cat > src/hooks/useAtlasSearch.js << 'EOF'
import { useCallback, useState } from "react";
import { buscar, interpretar, getReferencias } from "../lib/atlasApi.js";

export function useAtlasSearch() {
  const [referencias, setReferencias] = useState([]);
  const [sitio, setSitio] = useState(null);
  const [pesos, setPesos] = useState({});
  const [descubrimiento, setDescubrimiento] = useState(false);
  const [resumen, setResumen] = useState("");
  const [result, setResult] = useState(null);
  const [status, setStatus] = useState("idle");

  const loadReferencias = useCallback(async () => {
    const refs = await getReferencias();
    setReferencias(refs);
    setSitio(refs[0]?.sitio || "jezero");
    return refs;
  }, []);

  const desdeTexto = useCallback(async (texto) => {
    setStatus("loading");
    try {
      const c = await interpretar(texto);
      setSitio(c.sitio);
      setPesos(c.pesos || {});
      setDescubrimiento(Boolean(c.descubrimiento));
      setResumen(c.resumen || "");
      const res = await buscar({ sitio: c.sitio, pesos: c.pesos, descubrimiento: c.descubrimiento });
      setResult(res);
      setStatus("ok");
    } catch {
      const res = await buscar({ sitio, pesos: {}, descubrimiento });
      setResult(res);
      setResumen("IA no disponible. Mostrando criterios base del sitio.");
      setStatus("ok");
    }
  }, [sitio, descubrimiento]);

  const setPeso = useCallback(async (clave, valor) => {
    const nuevos = { ...pesos, [clave]: valor };
    setPesos(nuevos);
    setStatus("loading");
    const res = await buscar({ sitio, pesos: nuevos, descubrimiento });
    setResult(res);
    setStatus("ok");
  }, [sitio, pesos, descubrimiento]);

  return {
    referencias, sitio, setSitio, pesos, setPeso, descubrimiento, setDescubrimiento,
    resumen, result, status, loadReferencias, desdeTexto,
  };
}
EOF
