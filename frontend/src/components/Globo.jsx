// Analog Atlas · frontend/src/components/Globo.jsx
// v1.0 · 2026-11-14 · Isabelita (equipo Ctrl Z)
// Globo 3D (three.js) con la textura global real de NASA Trek y los sitios marcados.
// Se gira arrastrando; gira solo y despacio para que se note que es 3D (se detiene al tocarlo y con
// prefers-reduced-motion). Las etiquetas son botones HTML encima del globo: clic o teclado eligen el sitio.
import { useEffect, useRef, useState } from "react";
import * as THREE from "three";
import { OrbitControls } from "three/examples/jsm/controls/OrbitControls.js";

const RADIO = 1;

// lat/lon a la esfera de three.js con textura equirectangular (u = 0 en lon = −180°)
export function aVector(lat, lon, r = RADIO) {
  const phi = ((90 - lat) * Math.PI) / 180;
  const theta = ((lon + 180) * Math.PI) / 180;
  return new THREE.Vector3(-r * Math.sin(phi) * Math.cos(theta), r * Math.cos(phi), r * Math.sin(phi) * Math.sin(theta));
}

export default function Globo({ textura, nombre, sitios, elegido, alElegir, acento, compacto = false }) {
  const caja = useRef(null);
  const etiquetas = useRef({});
  const escena = useRef(null);
  const [listo, setListo] = useState(false);

  useEffect(() => {
    const el = caja.current;
    const quieto = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    el.appendChild(renderer.domElement);
    const scene = new THREE.Scene();
    const camara = new THREE.PerspectiveCamera(35, 1, 0.1, 100);
    camara.position.set(0, 0, 3.6);

    const tex = new THREE.TextureLoader().load(textura, () => setListo(true));
    tex.colorSpace = THREE.SRGBColorSpace;
    tex.anisotropy = 4;
    const globo = new THREE.Mesh(new THREE.SphereGeometry(RADIO, 96, 64), new THREE.MeshStandardMaterial({ map: tex, roughness: 1 }));
    scene.add(globo);
    scene.add(new THREE.AmbientLight(0xffffff, 1.6));
    const sol = new THREE.DirectionalLight(0xffffff, 1.4);
    sol.position.set(-3, 2, 4);
    scene.add(sol);

    const marcas = {};
    for (const s of sitios) {
      const m = new THREE.Mesh(new THREE.SphereGeometry(0.03, 16, 16), new THREE.MeshBasicMaterial({ color: 0xffffff }));
      m.position.copy(aVector(s.lat, s.lon, RADIO * 1.005));
      globo.add(m);
      marcas[s.clave] = m;
    }

    const controles = new OrbitControls(camara, renderer.domElement);
    controles.enablePan = false;
    controles.enableZoom = false;
    controles.enableDamping = true;
    controles.rotateSpeed = 0.6;
    controles.autoRotate = !quieto && !compacto;
    controles.autoRotateSpeed = 0.4;
    controles.addEventListener("start", () => { controles.autoRotate = false; });

    const ajustar = () => {
      const { width, height } = el.getBoundingClientRect();
      renderer.setSize(width, height, false);
      renderer.domElement.style.width = "100%";
      renderer.domElement.style.height = "100%";
      camara.aspect = width / height;
      camara.updateProjectionMatrix();
    };
    const obs = new ResizeObserver(ajustar);
    obs.observe(el);
    ajustar();

    const tmp = new THREE.Vector3();
    const haciaCam = new THREE.Vector3();
    let destino = null;
    let cuadro;
    const animar = () => {
      cuadro = requestAnimationFrame(animar);
      if (destino) {
        camara.position.lerp(destino, quieto ? 1 : 0.08);
        if (camara.position.distanceTo(destino) < 0.01) destino = null;
      }
      controles.update();
      renderer.render(scene, camara);
      const { width, height } = el.getBoundingClientRect();
      for (const [clave, m] of Object.entries(marcas)) {
        const et = etiquetas.current[clave];
        if (!et) continue;
        m.getWorldPosition(tmp);
        haciaCam.copy(camara.position).sub(tmp);
        const visible = tmp.clone().normalize().dot(haciaCam.normalize()) > 0.15;
        const p = tmp.project(camara);
        et.style.transform = `translate(${((p.x + 1) / 2) * width}px, ${((1 - p.y) / 2) * height}px)`;
        et.style.opacity = visible ? "1" : "0";
        et.style.pointerEvents = visible ? "auto" : "none";
        et.tabIndex = visible ? 0 : -1;
      }
    };
    animar();

    escena.current = {
      mirar: (s) => {
        controles.autoRotate = false;
        destino = aVector(s.lat, s.lon, 3.6);
      },
      pintar: (claveElegida, color) => {
        for (const [clave, m] of Object.entries(marcas)) {
          m.material.color.set(clave === claveElegida ? color : "#ffffff");
          m.scale.setScalar(clave === claveElegida ? 1.6 : 1);
        }
      },
    };
    return () => {
      cancelAnimationFrame(cuadro);
      obs.disconnect();
      controles.dispose();
      renderer.dispose();
      tex.dispose();
      el.removeChild(renderer.domElement);
    };
  }, [textura]);

  useEffect(() => {
    escena.current?.pintar(elegido, acento);
    const s = sitios.find((x) => x.clave === elegido);
    if (s) escena.current?.mirar(s);
  }, [elegido, acento]);

  return (
    <div className={`globe${compacto ? " globe-sm" : ""}`} ref={caja} aria-label={`3D globe of ${nombre}. Drag to rotate.`} role="img">
      {!listo && <div className="globe-loading">Loading {nombre} map…</div>}
      {sitios.map((s) => (
        <button key={s.clave} type="button" ref={(n) => { etiquetas.current[s.clave] = n; }}
          className={`globe-tag${elegido === s.clave ? " on" : ""}`} aria-pressed={elegido === s.clave}
          onClick={() => alElegir(s.clave)}>
          {s.nombre}
        </button>
      ))}
    </div>
  );
}
