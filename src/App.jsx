cat > src/App.jsx << 'EOF'
import { useEffect, useState } from "react";
import Workspace from "./components/Workspace.jsx";
import PlaceCard from "./components/PlaceCard.jsx";
import { useAtlasSearch } from "./hooks/useAtlasSearch.js";

export default function App() {
  const atlas = useAtlasSearch();
  const [selectedCell, setSelectedCell] = useState(null);

  useEffect(() => { atlas.loadReferencias(); }, []);

  return (
    <div className="aa-app">
      <Workspace atlas={{ ...atlas, onSelect: setSelectedCell }} />
      {selectedCell && (
        <PlaceCard
          cell={selectedCell}
          cuerpo={atlas.referencias.find(r => r.sitio === atlas.sitio)?.cuerpo || "marte"}
          sitio={atlas.sitio}
          onClose={() => setSelectedCell(null)}
        />
      )}
    </div>
  );
}
EOF
