// Analog Atlas · frontend/src/main.jsx
// v1.0 · 2026-11-14 · Isabelita (equipo Ctrl Z)
import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import App from "./App.jsx";
import "./styles/tokens.css";
import "./styles/app.css";

createRoot(document.getElementById("root")).render(
  <StrictMode>
    <App />
  </StrictMode>,
);
