// Analog Atlas · App root

import { useEffect, useState } from "react";
import Workspace from "./components/Workspace";
import PlaceCard from "./components/PlaceCard";
import { useAtlasSearch } from "./hooks/useAtlasSearch";
import "./styles/tokens.css";
import "./styles/app.css";

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
