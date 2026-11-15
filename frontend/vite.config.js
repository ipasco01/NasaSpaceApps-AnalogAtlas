// Analog Atlas · frontend/vite.config.js
// v1.0 · 2026-11-14 · Isabelita (equipo Ctrl Z)
// En desarrollo, /api y /health van a la API local (python -m api.main). En producción FastAPI sirve dist/.
import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

const API = "http://127.0.0.1:8000";

export default defineConfig({
  plugins: [react()],
  server: { host: "127.0.0.1", port: 5173, proxy: { "/api": API, "/health": API } },
});
