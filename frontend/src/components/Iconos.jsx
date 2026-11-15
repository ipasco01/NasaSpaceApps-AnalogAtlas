// Analog Atlas · frontend/src/components/Iconos.jsx
// v1.0 · 2026-11-14 · Isabelita (equipo Ctrl Z)
// Íconos de interfaz en trazo de 2 px: sol/luna (modo), lupa (buscar), cerrar, ayuda, enviar.
// Los íconos de datos y acciones del equipo están en IconosAtlas.jsx (generado desde views/assets/icons).

const Base = ({ children, size = 20 }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"
    strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">{children}</svg>
);


export const Sol = () => <Base><circle cx="12" cy="12" r="4" /><path d="M12 2v2M12 20v2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M2 12h2M20 12h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4" /></Base>;
export const Luna = () => <Base><path d="M21 12.8A9 9 0 1 1 11.2 3a7 7 0 0 0 9.8 9.8z" /></Base>;
export const Lupa = () => <Base><circle cx="11" cy="11" r="7" /><path d="m20 20-3.5-3.5" /></Base>;
export const Cerrar = () => <Base><path d="M18 6 6 18M6 6l12 12" /></Base>;
export const Ayuda = () => <Base><circle cx="12" cy="12" r="9" /><path d="M9.5 9a2.5 2.5 0 1 1 3.5 2.3c-.6.3-1 .9-1 1.6V14" /><path d="M12 17h.01" /></Base>;
export const Enviar = () => <Base><path d="M22 2 11 13" /><path d="M22 2 15 22l-4-9-9-4 20-7z" /></Base>;
