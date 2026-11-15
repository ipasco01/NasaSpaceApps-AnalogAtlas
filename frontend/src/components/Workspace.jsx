// Analog Atlas · Workspace (mapa + sidebar + AI panel)

import { useEffect, useRef } from "react";
import maplibregl from "maplibre-gl";
import "maplibre-gl/dist/maplibre-gl.css";
import { colorTramo } from "../lib/atlasApi";
import FilterSidebar from "./FilterSidebar";
import AskAIPanel from "./AskAIPanel";

const EOX_STYLE = {
  version: 8,
  glyphs: "https://demotiles.maplibre.org/font/{fontstack}/{range}.pbf",
  sources: {
    eox: {
      type: "raster",
      tiles: ["https://tiles.maps.eox.at/wms?service=wms&version=1.1.1&request=getmap&layers=s2cloudless-2021&format=image/jpeg&transparent=false&width=256&height=256&srs=EPSG:3857&bbox={bbox-epsg-3857}"],
      tileSize: 256,
      attribution: "Contains modified Copernicus Sentinel data 2021",
    },
  },
  layers: [{ id: "eox", type: "raster", source: "eox" }],
};

export default function Workspace({ atlas }) {
  const cont = useRef(null);
  const map = useRef(null);

  useEffect(() => {
    if (!cont.current) return;
    map.current = new maplibregl.Map({ container: cont.current, style: EOX_STYLE, center: [0, 20], zoom: 2 });
    map.current.addControl(new maplibregl.NavigationControl(), "top-right");
    return () => map.current?.remove();
  }, []);

  useEffect(() => {
    if (!map.current || !atlas.result) return;
    const src = map.current.getSource("aa") || null;
    const features = atlas.result.lugares.map((p, i) => ({
      type: "Feature",
      properties: { ...p, id: i },
      geometry: { type: "Point", coordinates: [p.lon, p.lat] },
    }));
    const data = { type: "FeatureCollection", features };
    if (src) src.setData(data);
    else {
      map.current.addSource("aa", { type: "geojson", data });
      map.current.addLayer({ id: "aa-halo", type: "circle", source: "aa",
        paint: { "circle-radius": 14, "circle-color": "#8b5cf6", "circle-opacity": 0.35 } });
      map.current.addLayer({ id: "aa-dot", type: "circle", source: "aa",
        paint: { "circle-radius": 6, "circle-color": "#6d28d9",
          "circle-stroke-color": "#ffffff", "circle-stroke-width": 2 } });
      map.current.on("click", "aa-dot", (e) => atlas.onSelect?.(e.features[0].properties));
    }
  }, [atlas.result]);

  return (
    <div className="aa-workspace">
      <FilterSidebar atlas={atlas} />
      <div className="aa-map-wrap">
        <div ref={cont} className="aa-map" />
        <AskAIPanel atlas={atlas} />
        {atlas.result?.tierra_no_llega?.length > 0 && (
          <div className="aa-limit-note">
            Earth cannot reach the reference value in: {atlas.result.tierra_no_llega.join(", ")}
          </div>
        )}
      </div>
    </div>
  );
}
