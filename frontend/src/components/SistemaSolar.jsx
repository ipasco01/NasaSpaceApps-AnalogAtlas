// Analog Atlas · frontend/src/components/SistemaSolar.jsx
// v1.0 · 2026-11-15 · Isabelita (equipo Ctrl Z)
// Escena 3D del paso 2: la Tierra, la Luna y Marte con tamaños relativos reales (distancias no a escala).
// La escena queda fija; la cámara vuela al planeta o al sitio elegido. Planetas y sitios se eligen con botones HTML
// sobre la escena (clic o teclado). Gira despacio sola si no se pidió reducir movimiento.
import { useEffect, useRef, useState } from "react";
import * as THREE from "three";
import { OrbitControls } from "three/examples/jsm/controls/OrbitControls.js";
import { aVector } from "./Globo.jsx";

// Radios relativos a la Tierra: Luna 0.273, Marte 0.532 (NASA Planetary Fact Sheets). Posiciones solo para verlos juntos.
export const CUERPOS = {
  Earth: { textura: "/img/earth_2k.jpg", r: 1, pos: [-2.1, 0, 0], nombre: "Earth" },
  Moon: { textura: "/img/moon_2k.jpg", r: 0.273, pos: [-0.3, 0.7, 0.6], nombre: "Moon" },
  Mars: { textura: "/img/mars_2k.jpg", r: 0.532, pos: [2.3, 0, 0], nombre: "Mars" },
};
const VISTA_GENERAL = { pos: new THREE.Vector3(0, 1.6, 10.5), objetivo: new THREE.Vector3(0, 0, 0) };
const PANEL_PX = 456; // ancho del panel derecho + margen: la escena se centra en el espacio libre

export default function SistemaSolar({ sitios, foco, elegido, alPlaneta, alSitio, acento }) {
  const caja = useRef(null);
  const etiquetas = useRef({});
  const api = useRef(null);
  const [listo, setListo] = useState(0);

  useEffect(() => {
    const el = caja.current;
    const quieto = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    el.appendChild(renderer.domElement);
    const scene = new THREE.Scene();
    const camara = new THREE.PerspectiveCamera(35, 1, 0.05, 200);
    camara.position.copy(VISTA_GENERAL.pos);

    scene.add(new THREE.AmbientLight(0xffffff, 0.55));
    const sol = new THREE.DirectionalLight(0xffffff, 2.2);
    sol.position.set(-12, 4, 8);
    scene.add(sol);

    // Estrellas tenues de fondo: dan contexto de espacio, no se mueven
    const estrellas = new THREE.BufferGeometry();
    const pts = new Float32Array(1200 * 3).map(() => (Math.random() - 0.5) * 120);
    estrellas.setAttribute("position", new THREE.BufferAttribute(pts, 3));
    scene.add(new THREE.Points(estrellas, new THREE.PointsMaterial({ color: 0xffffff, size: 0.08, transparent: true, opacity: 0.6 })));

    const cargador = new THREE.TextureLoader();
    const cuerpos = {};
    const marcas = {};
    for (const [clave, c] of Object.entries(CUERPOS)) {
      const tex = cargador.load(c.textura, () => setListo((n) => n + 1));
      tex.colorSpace = THREE.SRGBColorSpace;
      const malla = new THREE.Mesh(new THREE.SphereGeometry(c.r, 96, 64), new THREE.MeshStandardMaterial({ map: tex, roughness: 1 }));
      malla.position.set(...c.pos);
      scene.add(malla);
      cuerpos[clave] = malla;
    }
    for (const s of sitios) {
      const c = CUERPOS[s.cuerpo];
      const m = new THREE.Mesh(new THREE.SphereGeometry(c.r * 0.025, 16, 16), new THREE.MeshBasicMaterial({ color: 0xffffff }));
      m.position.copy(aVector(s.lat, s.lon, c.r * 1.01));
      cuerpos[s.cuerpo].add(m);
      marcas[s.clave] = m;
    }

    const controles = new OrbitControls(camara, renderer.domElement);
    controles.enablePan = false;
    controles.enableZoom = false;
    controles.enableDamping = true;
    controles.rotateSpeed = 0.5;
    controles.target.copy(VISTA_GENERAL.objetivo);

    let ancho = 1;
    let alto = 1;
    const ajustar = () => {
      const r = el.getBoundingClientRect();
      ancho = r.width;
      alto = r.height;
      renderer.setSize(ancho, alto, false);
      renderer.domElement.style.width = "100%";
      renderer.domElement.style.height = "100%";
      camara.aspect = ancho / alto;
      // En pantallas anchas el panel tapa la derecha: se corre la vista para centrar la escena en el espacio libre
      if (ancho > 1024) camara.setViewOffset(ancho, alto, PANEL_PX / 2, 0, ancho, alto);
      else camara.clearViewOffset();
      camara.updateProjectionMatrix();
    };
    const obs = new ResizeObserver(ajustar);
    obs.observe(el);
    ajustar();

    let destino = null; // { pos, objetivo }
    let girando = !quieto;
    let cuadro;
    const tmp = new THREE.Vector3();
    const centro = new THREE.Vector3();
    const animar = () => {
      cuadro = requestAnimationFrame(animar);
      if (girando) for (const m of Object.values(cuerpos)) m.rotation.y += 0.0012;
      if (destino) {
        const k = quieto ? 1 : 0.07;
        camara.position.lerp(destino.pos, k);
        controles.target.lerp(destino.objetivo, k);
        if (camara.position.distanceTo(destino.pos) < 0.005) destino = null;
      }
      controles.update();
      renderer.render(scene, camara);
      // Etiquetas HTML sobre la escena
      const proyectar = (v) => {
        const p = v.clone().project(camara);
        return [((p.x + 1) / 2) * ancho, ((1 - p.y) / 2) * alto];
      };
      for (const [clave, malla] of Object.entries(cuerpos)) {
        const et = etiquetas.current[`p-${clave}`];
        if (!et) continue;
        malla.getWorldPosition(centro);
        const [x, y] = proyectar(centro.clone().add(new THREE.Vector3(0, -CUERPOS[clave].r * 1.25, 0)));
        et.style.transform = `translate(${x}px, ${y}px)`;
      }
      for (const [clave, m] of Object.entries(marcas)) {
        const et = etiquetas.current[`s-${clave}`];
        if (!et) continue;
        m.getWorldPosition(tmp);
        m.parent.getWorldPosition(centro);
        const normal = tmp.clone().sub(centro).normalize();
        const haciaCam = camara.position.clone().sub(tmp).normalize();
        const visible = normal.dot(haciaCam) > 0.2 && et.dataset.activo === "1";
        const [x, y] = proyectar(tmp);
        et.style.transform = `translate(${x}px, ${y}px)`;
        et.style.opacity = visible ? "1" : "0";
        et.style.pointerEvents = visible ? "auto" : "none";
        et.tabIndex = visible ? 0 : -1;
      }
    };
    animar();

    api.current = {
      general: () => {
        girando = !quieto;
        destino = { pos: VISTA_GENERAL.pos.clone(), objetivo: VISTA_GENERAL.objetivo.clone() };
      },
      planeta: (clave) => {
        girando = !quieto;
        const c = cuerpos[clave].position;
        const dir = camara.position.clone().sub(controles.target).normalize();
        destino = { pos: c.clone().add(dir.multiplyScalar(CUERPOS[clave].r * 6)), objetivo: c.clone() };
      },
      sitio: (clave, cuerpo) => {
        girando = false; // quieto para que el cráter quede de frente
        const malla = cuerpos[cuerpo];
        malla.updateMatrixWorld();
        marcas[clave].getWorldPosition(tmp);
        const dir = tmp.clone().sub(malla.position).normalize();
        destino = { pos: malla.position.clone().add(dir.multiplyScalar(CUERPOS[cuerpo].r * 6)), objetivo: malla.position.clone() };
      },
      pintar: (clave, color) => {
        for (const [k, m] of Object.entries(marcas)) {
          m.material.color.set(k === clave ? color : "#ffffff");
          m.scale.setScalar(k === clave ? 1.4 : 1);
        }
      },
    };
    return () => {
      cancelAnimationFrame(cuadro);
      obs.disconnect();
      controles.dispose();
      renderer.dispose();
      el.removeChild(renderer.domElement);
    };
  }, []);

  useEffect(() => {
    const a = api.current;
    if (!a) return;
    a.pintar(elegido, acento);
    if (elegido) a.sitio(elegido, sitios.find((s) => s.clave === elegido).cuerpo);
    else if (foco) a.planeta(foco);
    else a.general();
  }, [foco, elegido, acento]);

  return (
    <div className="solar" ref={caja} role="img" aria-label="Earth, the Moon and Mars. Sizes to scale, distances not. Drag to rotate the view.">
      {listo < 3 && <div className="globe-loading">Loading planet maps…</div>}
      {Object.keys(CUERPOS).map((clave) => (
        <button key={clave} type="button" ref={(n) => { etiquetas.current[`p-${clave}`] = n; }}
          className={`planet-tag${foco === clave ? " on" : ""}`} onClick={() => alPlaneta(clave)}>
          {CUERPOS[clave].nombre}{clave === "Earth" ? " · where we search" : ""}
        </button>
      ))}
      {sitios.map((s) => (
        <button key={s.clave} type="button" ref={(n) => { etiquetas.current[`s-${s.clave}`] = n; }}
          data-activo={foco === s.cuerpo ? "1" : "0"} className={`globe-tag${elegido === s.clave ? " on" : ""}`}
          aria-pressed={elegido === s.clave} onClick={() => alSitio(s.clave)}>
          {s.nombre}
        </button>
      ))}
      <p className="solar-note">Sizes to scale, distances not. Drag to look around.</p>
    </div>
  );
}
