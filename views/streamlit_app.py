# Analog Atlas · views/streamlit_app.py
# v0.6 · 2026-11-14 · Isabelita (equipo Ctrl Z)
# App Streamlit: pide todo a través de views/api_cliente.py (en el mismo proceso, o por HTTP a api/main.py). Flujo aprobado: portada -> rol -> mejores
# regiones del mundo -> explorar una región con filtros -> pantalla del punto con evidencia.
# La versión anterior (cliente de la API) queda en el historial de git, commit 50632a8.
# Uso (desde la raíz del repo): streamlit run views/streamlit_app.py   (con ATLAS_API=http://127.0.0.1:8000 usa la API)

import base64
import json
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
if str(RAIZ) not in sys.path:
    sys.path.insert(0, str(RAIZ))

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
import streamlit.components.v1 as componentes

from views import api_cliente as api
from views.estilos import ASSETS, MODOS, css, data_uri, logo_html
from services.geo import ancho_vista_km, imagen_tierra, pais_de

st.set_page_config(page_title="Analog Atlas", page_icon=str(ASSETS / "logo_a.png"), layout="wide")

# ---------------------------------------------------------------- catálogos
SITIOS = {
    "jezero": {"nombre": "Jezero crater, Mars", "imagen": "r_jezero.jpg", "escala": True,
               "credito": "Viking MDIM 2.1, NASA Mars Trek"},
    "gale": {"nombre": "Gale crater, Mars", "imagen": "r_gale.jpg", "escala": True,
             "credito": "Viking MDIM 2.1, NASA Mars Trek"},
    "shackleton": {"nombre": "Shackleton crater rim, Moon", "imagen": "r_shackleton.jpg", "escala": False,
                   "credito": "LRO shaded relief in false color, NASA (scale not matched)"},
    "marius_hills": {"nombre": "Marius Hills, Moon", "imagen": "r_marius.jpg", "escala": True,
                     "credito": "LRO WAC mosaic, NASA Moon Trek"},
}
ROLES = {
    "educator": {"titulo": "Educator", "desc": "Teaching and learning",
                 "nota": "Famous analogs stay visible because they are useful for teaching.",
                 "descubrimiento": False, "multiplicar": {}, "imprescindibles": ()},
    "researcher": {"titulo": "Researcher", "desc": "Academic and scientific research",
                   "nota": "Known analog sites are hidden so new candidates surface. You can run a robustness check on any place.",
                   "descubrimiento": True, "multiplicar": {}, "imprescindibles": ()},
    "testing": {"titulo": "Mission and equipment testing", "desc": "Rovers, habitats, suits, drills",
                "nota": "Slope and barren ground weigh more, and barren ground is required.",
                "descubrimiento": True, "multiplicar": {"pendiente": 2.0, "arido": 1.5}, "imprescindibles": ("arido",)},
    "other": {"titulo": "Other", "desc": "Just exploring",
              "nota": "Default weights.", "descubrimiento": True, "multiplicar": {}, "imprescindibles": ()},
}
VARIABLES = {
    "ndvi": "No vegetation", "arido": "Barren ground", "rango_termico": "Day–night swing",
    "temp_noche": "Night temperature", "temp_dia": "Day temperature", "pendiente": "Slope",
    "hielo": "Surface ice", "permafrost_proxy": "Frozen ground", "lluvia": "Dryness", "polvo": "Dust",
    "nieve": "Snow", "elevacion": "Elevation", "volcanico": "Volcanic rock", "sedimento": "Sedimentary ground",
}
UNIDADES = {"temp_dia": "°C", "temp_noche": "°C", "rango_termico": "°C", "pendiente": "°", "elevacion": "m",
            "lluvia": "mm/yr", "nieve": "%"}
LIMITES = {
    "marte": [("Gravity", "Mars 0.379 g", "Earth 1 g"), ("Air pressure", "Mars ~0.63%", "of Earth's"),
              ("Surface radiation", "Mars ~0.67 mSv/day", "far above Earth")],
    "luna": [("Gravity", "Moon 0.165 g", "Earth 1 g"), ("Atmosphere", "Moon: none", "exosphere only"),
             ("Surface radiation", "Moon ~1.37 mSv/day", "far above Earth")],
}
FUENTES_LIMITES = {
    "marte": "NASA Mars Fact Sheet; Curiosity RAD (Hassler et al. 2014, Science).",
    "luna": "NASA Moon Fact Sheet; Chang'e 4 LND (Zhang et al. 2020, Science Advances).",
}
TRAMOS = [(75, "Strong analog"), (50, "Good analog"), (25, "Partial analog"), (0, "Weak analog")]
TOP_REGIONES = 3000
CRUDOS = ("temp_dia", "temp_noche", "rango_termico", "pendiente", "ndvi", "nieve", "elevacion")
TARJETA_SITIO = {"jezero": ("Jezero crater", "Mars · Perseverance"), "gale": ("Gale crater", "Mars · Curiosity"),
                 "shackleton": ("Shackleton rim", "Moon · relief, not a photo"),
                 "marius_hills": ("Marius Hills", "Moon · lava tubes")}
ICONO_ROL = {"educator": ":material/school:", "researcher": ":material/science:",
             "testing": ":material/rocket_launch:", "other": ":material/explore:"}
# Fondo satelital del mapa. Licencia: uso libre no comercial con esta atribución (cloudless.eox.at, eox.at).
EOX_TESELAS = "https://tiles.maps.eox.at/wmts/1.0.0/s2cloudless-2021_3857/default/g/{z}/{y}/{x}.jpg"
CREDITO_EOX = ("Sentinel-2 cloudless 2021 by EOX IT Services GmbH (s2maps.eu), "
               "contains modified Copernicus Sentinel data 2021")


def tramo(p: float) -> str:
    return next(n for lim, n in TRAMOS if p >= lim)


def coord(lat: float, lon: float) -> str:
    return f"{abs(lat):.2f}° {'N' if lat >= 0 else 'S'}, {abs(lon):.2f}° {'E' if lon >= 0 else 'W'}"


# ---------------------------------------------------------------- datos de la API (cacheados)
@st.cache_data(show_spinner=False, ttl=300)
def salud() -> dict:
    return api.salud()


@st.cache_data(show_spinner=False, ttl=3600)
def referencias() -> dict:
    return {r["sitio"]: r for r in api.referencias()}


def pesos_para(sitio: str, rol: str) -> dict:
    pesos = dict(referencias()[sitio]["pesos_base"])
    for k, f in ROLES[rol]["multiplicar"].items():
        if k in pesos:
            pesos[k] *= f
    return pesos


@st.cache_resource(show_spinner=False)
def resultado(sitio: str, rol: str, descubrimiento: bool):
    """Top de la API con el país de cada lugar. Devuelve (mejores, variables que la Tierra no alcanza)."""
    r = api.buscar(sitio, pesos_para(sitio, rol), list(ROLES[rol]["imprescindibles"]), descubrimiento, TOP_REGIONES)
    mejores = pd.DataFrame([{"id": l["id"], "lat": l["lat"], "lon": l["lon"], "puntaje": l["puntaje"],
                             **{f"s_{k}": v for k, v in l["desglose"].items()}, **l["valores"]}
                            for l in r["lugares"]]).set_index("id")
    mejores["pais"] = pais_de(mejores["lat"].to_numpy(), mejores["lon"].to_numpy())
    return mejores, r["tierra_no_llega"]


def _foto_o_nada(lat: float, lon: float, ancho_km: int):
    try:
        return imagen_tierra(lat, lon, ancho_km)
    except Exception:
        return None


@st.cache_data(show_spinner=False, ttl=3600)
def foto_tierra(lat: float, lon: float, ancho_km: int):
    return _foto_o_nada(lat, lon, ancho_km)


@st.cache_data(show_spinner=False, ttl=3600)
def fotos_tierra(puntos: tuple) -> list:
    """Varias fotos a la vez: EOX tarda ~1.4 s por foto, en paralelo todas tardan lo que una."""
    with ThreadPoolExecutor(max_workers=8) as hilos:
        return list(hilos.map(lambda p: _foto_o_nada(*p), puntos))


# ---------------------------------------------------------------- estado
E = st.session_state
for clave, valor in {"paso": 0, "consulta": "", "rol": None, "sitio": "jezero", "pais": None, "punto": None,
                     "modo": "light", "descubrimiento": True}.items():
    E.setdefault(clave, valor)


def ir(paso: int):
    E.paso = paso
    E.subir = True
    st.rerun()


def subir_si_cambio():
    """Streamlit conserva el scroll de la pantalla anterior; al cambiar de pantalla se vuelve arriba."""
    if E.pop("subir", False):
        componentes.html("<script>const m=window.parent.document.querySelector('[data-testid=\'stMain\']');"
                         "if(m)m.scrollTo({top:0});window.parent.scrollTo({top:0});</script>", height=0)


# ---------------------------------------------------------------- cabecera: logo + volver al inicio + modo
st.markdown(css(E.modo), unsafe_allow_html=True)
PAL = MODOS[E.modo]
logo, espacio, inicio, modo = st.columns([6, 2, 1.2, 0.5], vertical_alignment="center")
logo.markdown(f'<div class="aa-cabecera">{logo_html(32, "var(--ink)")}<b>Analog Atlas</b><span>Space to Earth</span></div>',
              unsafe_allow_html=True)
if E.paso and inicio.button("Start over", width="stretch"):
    for clave in ("paso", "consulta", "rol", "pais", "punto"):
        E.pop(clave, None)
    st.rerun()
otro = "light" if E.modo == "dark" else "dark"
if modo.button("", icon=":material/light_mode:" if E.modo == "dark" else ":material/dark_mode:",
               help=f"Switch to {MODOS[otro]['nombre']} ({otro} mode)", key="btn_modo"):
    E.modo = otro
    st.rerun()

try:
    SALUD = salud()
except api.ApiNoDisponible as e:
    st.error(f"The Analog Atlas API is not running ({e}). Start it from the repo root with: python -m api.main, "
             "or unset ATLAS_API to compute inside this app.")
    st.stop()

if SALUD["datos_prueba"]:
    st.markdown('<div class="aa-aviso peligro"><b>Test data in use.</b> The real Earth table (datos/celdas.parquet) '
                'was not found, so every result on screen is made up. Do not use it in the demo.</div>',
                unsafe_allow_html=True)



# ---------------------------------------------------------------- ruta de navegación (reemplaza al indicador de pasos)
def ruta():
    """Referencia › región › lugar, cada tramo lleva a su pantalla; a la derecha, el rol activo."""
    if E.paso < 2:   # portada y modal de rol: sin ruta
        return
    with st.container(horizontal=True, vertical_alignment="center", key="migas"):
        ref = SITIOS[E.sitio]["nombre"]
        if E.paso >= 3:
            if st.button(ref, type="tertiary", key="miga_ref"):
                ir(2)
            st.markdown('<span class="aa-sep">›</span>', unsafe_allow_html=True)
            if E.paso == 4:
                if st.button(E.pais, type="tertiary", key="miga_pais"):
                    ir(3)
                st.markdown(f'<span class="aa-sep">›</span><b class="num">{E.get("punto_txt", "")}</b>', unsafe_allow_html=True)
            else:
                st.markdown(f"<b>{E.pais}</b>", unsafe_allow_html=True)
        else:
            st.markdown(f"<b>{ref}</b>", unsafe_allow_html=True)
        if E.rol:
            st.markdown(f'<span class="aa-sep">·</span><span class="aa-rol">{ROLES[E.rol]["titulo"]} weights</span>', unsafe_allow_html=True)
            if st.button("Change role", type="tertiary", key="cambiar_rol"):
                E.rol = None
                ir(1)


ruta()
subir_si_cambio()


# ---------------------------------------------------------------- 0. Portada a pantalla completa
PORTADA_CSS = f"""<style>
.stApp{{background:radial-gradient(ellipse at center,rgba(6,9,15,.55) 0%,rgba(6,9,15,.25) 70%),linear-gradient(180deg,rgba(6,9,15,.35),rgba(6,9,15,.70)),url({data_uri('portada_sechura.jpg')}) center/cover fixed}}
[data-testid="stMainBlockContainer"]{{min-height:100vh;display:flex;flex-direction:column;justify-content:center;max-width:760px;padding-block:48px}}
.aa-cabecera{{display:none}}
.st-key-q_inicio input::placeholder{{color:#6B7280!important;opacity:1}}
.st-key-btn_modo{{position:fixed;top:16px;right:16px;z-index:100}}
.st-key-btn_modo button{{background:rgba(255,255,255,.16);border:0;color:#fff;backdrop-filter:blur(8px)}}
.aa-portada{{display:flex;flex-direction:column;align-items:center;gap:16px;text-align:center;margin-bottom:24px;text-shadow:0 2px 8px rgba(0,0,0,.65)}}
.aa-portada .marca{{display:flex;align-items:center;gap:16px;padding:16px 24px;border-radius:20px;background:rgba(6,9,15,.38);backdrop-filter:blur(6px)}}
.aa-portada .texto{{display:flex;flex-direction:column;align-items:flex-start;padding-left:16px;border-left:2px solid rgba(255,255,255,.7)}}
.aa-portada strong{{font-size:clamp(36px,6vw,60px);font-weight:600;line-height:1;color:#fff}}
.aa-portada .sub{{font-size:14px;font-weight:600;letter-spacing:.32em;text-transform:uppercase;color:#FFFFFF;margin-top:8px}}
.aa-portada .por{{font-size:14px;color:#fff;align-self:flex-end;margin-top:4px}}
.aa-portada p{{color:#F8FAFC!important;font-size:17px;font-weight:500;max-width:52ch;margin:8px 0 0}}
.st-key-q_inicio input{{min-height:56px;border-radius:999px;font-size:17px;padding-inline:24px;background:#fff!important;color:#111827!important}}
.st-key-q_inicio [data-baseweb="input"]{{border-radius:999px;background:#fff;border:0;box-shadow:0 12px 32px rgba(0,0,0,.30)}}
[data-testid="stForm"] .stFormSubmitButton>button{{min-height:56px;border-radius:999px}}
.st-key-ejemplos button{{background:rgba(6,9,15,.45);color:#fff;border:1px solid rgba(255,255,255,.35);border-radius:999px;backdrop-filter:blur(8px)}}
.st-key-ejemplos button:hover{{background:rgba(6,9,15,.65);border-color:#fff;color:#fff}}
.st-key-ejemplos p{{color:#fff!important}}
.aa-credito{{position:fixed;right:16px;bottom:12px;font-size:12px;color:#fff;text-shadow:0 1px 4px rgba(0,0,0,.8);z-index:100}}
.aa-pie{{display:none}}
</style>"""


def pantalla_inicio():
    st.markdown(PORTADA_CSS, unsafe_allow_html=True)
    st.markdown(f"""<div class="aa-portada">
      <div class="marca">{logo_html(96, "#fff")}<div class="texto"><strong>Analog Atlas</strong>
        <span class="sub">Space to Earth</span><span class="por">by <b>Ctrl Z</b></span></div></div>
      <p>There's no Ctrl+Z on Mars. Find where on Earth to rehearse, scored with NASA data and clear about where the analogy breaks.</p>
    </div><span class="aa-credito">Piura and the Sechura Desert · Sentinel-2 cloudless 2021 (EOX)</span>""",
                unsafe_allow_html=True)
    with st.form("busqueda", border=False):
        col1, col2 = st.columns([5, 1], vertical_alignment="center")
        texto = col1.text_input("What would you like to explore?", placeholder="What would you like to explore?",
                                label_visibility="collapsed", key="q_inicio")
        enviar = col2.form_submit_button("Search", type="primary", width="stretch")
    ejemplos = ["Rocky terrain to test rover mobility", "Dry volcanic plains like Jezero",
                "Cold ground for a lunar south pole base"]
    with st.container(key="ejemplos", horizontal=True, horizontal_alignment="center", gap="small"):
        for ej in ejemplos:
            if st.button(ej, width="content"):
                texto, enviar = ej, True
    if enviar and texto.strip():
        E.consulta = texto.strip()
        lectura = api.interpretar(E.consulta)
        E.sitio = lectura["sitio"]
        if "arido" in lectura["imprescindibles"]:   # la API detectó pruebas de equipo
            E.rol = E.rol or "testing"
        ir(1)


# ---------------------------------------------------------------- 1. Rol: modal propio sobre la Tierra satelital
# No se usa st.dialog: es un fragmento aparte y, si la página se recarga con la ventana abierta, el clic
# siguiente se pierde ("fragment does not exist anymore"). Este modal es un contenedor normal fijado con CSS.
def elegir_rol(clave: str):
    E.rol, E.paso, E.subir = clave, 2, True


def elegir_sitio(clave: str):
    E.sitio = clave


def pantalla_rol():
    st.markdown(f"<style>.stApp{{background:url({data_uri('mundo_s2.jpg')}) center/cover fixed}}</style>",
                unsafe_allow_html=True)
    with st.container(key="modal_rol"):
        with st.container(key="modal_tarjeta"):
            st.markdown("### How will you use Analog Atlas?")
            if E.consulta:
                st.caption(f"Your search: “{E.consulta}”")
            st.markdown('<p class="aa-paso">1 · Compare with <span>Picked from your search</span></p>',
                        unsafe_allow_html=True)
            for col, (clave, s) in zip(st.columns(4, gap="small"), SITIOS.items()):
                elegido = clave == E.sitio
                corto, sub = TARJETA_SITIO[clave]
                with col.container(key=f"card_sitio_{clave}_{'on' if elegido else 'off'}"):
                    st.markdown(f'<img class="aa-foto" src="{data_uri(s["imagen"])}" alt="{s["nombre"]}">',
                                unsafe_allow_html=True)
                    st.button(f"**{corto}**  \n{sub}", key=f"sitio_{clave}", width="stretch",
                              type="primary" if elegido else "tertiary", on_click=elegir_sitio, args=(clave,))
            st.markdown('<p class="aa-paso">2 · Your role <span>Tap one to continue</span></p>', unsafe_allow_html=True)
            cols = st.columns(2, gap="small")
            for i, (clave, r) in enumerate(ROLES.items()):   # un clic guarda el rol y lleva a las regiones
                sugerido = " · suggested" if E.rol == clave else ""
                cols[i % 2].button(f"**{r['titulo']}**{sugerido}  \n{r['desc']}", key=f"rol_{clave}", width="stretch",
                                   icon=ICONO_ROL[clave], type="primary" if E.rol == clave else "secondary",
                                   on_click=elegir_rol, args=(clave,))
            st.button("Skip for now", type="tertiary", key="saltar_rol",
                      on_click=elegir_rol, args=(E.rol or "other",))


# ---------------------------------------------------------------- mapa satelital y fotos
def mapa(datos: pd.DataFrame, etiquetas: pd.Series, centro=(20.0, 10.0), zoom=0.8, alto=440):
    """Puntos sobre Sentinel-2 cloudless (EOX). Más brillante = más parecido."""
    d = datos[["lat", "lon", "puntaje"]]
    rango = max(float(np.ptp(d["puntaje"])), 1e-9)
    opacidad = (0.35 + (d["puntaje"] - d["puntaje"].min()) / rango * 0.65).to_numpy()
    info = np.column_stack([etiquetas.astype(str), d["puntaje"].round(0).astype(int).astype(str)])
    fig = go.Figure([
        go.Scattermap(lat=d["lat"], lon=d["lon"], mode="markers", hoverinfo="skip",
                      marker=dict(size=14, color="#FFFFFF", opacity=opacidad)),
        go.Scattermap(lat=d["lat"], lon=d["lon"], mode="markers", customdata=info,
                      marker=dict(size=9, color=PAL["accent"], opacity=opacidad),
                      hovertemplate="<b>%{customdata[0]}</b><br>Score %{customdata[1]}<extra></extra>"),
    ])
    fig.update_layout(
        map=dict(style="white-bg", center=dict(lat=centro[0], lon=centro[1]), zoom=zoom,
                 layers=[dict(below="traces", sourcetype="raster", source=[EOX_TESELAS], sourceattribution=CREDITO_EOX)]),
        margin=dict(l=0, r=0, t=0, b=0), height=alto, showlegend=False, paper_bgcolor="rgba(0,0,0,0)",
        hoverlabel=dict(bgcolor=PAL["surface"], font_color=PAL["ink"], bordercolor=PAL["line"]))
    st.plotly_chart(fig, width="stretch", config={"displayModeBar": False, "scrollZoom": True})


def zoom_para(d: pd.DataFrame) -> float:
    lado = max(float(np.ptp(d["lat"])), float(np.ptp(d["lon"])), 0.5)
    return float(np.clip(np.log2(360 / lado) - 0.8, 1.0, 8.0))


def foto_html(img, alt: str, clase: str = "aa-foto") -> str:
    if not img:
        return f'<div class="{clase}" role="img" aria-label="{alt} (image unavailable)"></div>'
    return f'<img class="{clase}" src="data:image/jpeg;base64,{base64.b64encode(img).decode()}" alt="{alt}">'


# ---------------------------------------------------------------- 2. Mejores regiones (amplio primero)
def pantalla_regiones():
    rol = ROLES[E.rol or "other"]
    sitio = SITIOS[E.sitio]
    titulo, interruptor = st.columns([3, 1.2], vertical_alignment="bottom")
    titulo.markdown(f'<h1 class="aa-h1">Best regions on Earth for {sitio["nombre"]}</h1>'
                    f'<p class="aa-nota">{rol["titulo"]}: {rol["nota"]}</p>', unsafe_allow_html=True)
    E.descubrimiento = interruptor.toggle("Hide well-known analog sites", value=rol["descubrimiento"],
                                          help="Hides cells within 150 km of 17 analog sites already studied.",
                                          key=f"desc_{E.rol}")
    with st.spinner("Scoring every land cell on Earth"):
        mejores, saturadas = resultado(E.sitio, E.rol or "other", E.descubrimiento)
    if saturadas:
        st.caption("Earth never reaches the reference value for: " + ", ".join(VARIABLES.get(s, s) for s in saturadas)
                   + ". The closest Earth values are used.")
    top = mejores.head(600)
    mapa(top, top["pais"])
    st.markdown(f'<p class="aa-credito-mapa">{CREDITO_EOX}</p>', unsafe_allow_html=True)
    con_pais = mejores[mejores["pais"] != "Open area"]   # celdas sin país (costas lejanas, islas sin contorno)
    regiones = (con_pais.groupby("pais").agg(mejor=("puntaje", "max"), celdas=("puntaje", "size"))
                .sort_values(["mejor", "celdas"], ascending=False).head(6))
    mejor_celda = con_pais.loc[con_pais.groupby("pais")["puntaje"].idxmax()].set_index("pais")
    st.markdown('<div class="aa-fila-titulo"><h2>Pick a region to explore</h2>'
                '<span>Photo: 120 km around the best place in each region</span></div>', unsafe_allow_html=True)
    fotos = fotos_tierra(tuple((round(float(mejor_celda.loc[p].lat), 2), round(float(mejor_celda.loc[p].lon), 2), 120)
                               for p in regiones.index))
    cols = st.columns(3)
    for i, (pais, fila) in enumerate(regiones.iterrows()):
        with cols[i % 3].container(key=f"card_region_{i}"):
            st.markdown(foto_html(fotos[i], f"Satellite view of the best place in {pais}", "aa-foto ancha")
                        + f'<div class="aa-region"><div><b>{pais}</b><span>{tramo(fila.mejor)} · {int(fila.celdas):,} cells'
                        f'</span></div><strong>{fila.mejor:.0f}</strong></div>', unsafe_allow_html=True)
            if st.button(f"Explore {pais}", key=f"reg_{pais}", width="stretch", type="primary" if i == 0 else "secondary"):
                E.pais, E.punto = pais, None
                ir(3)


# ---------------------------------------------------------------- 3. Explorar una región: filtros + resultados | mapa
def rango_slider(region: pd.DataFrame, col: str, nombre: str, paso: float, formato: str):
    if col not in region or region[col].isna().all():
        return None
    lo, hi = float(np.floor(region[col].min())), float(np.ceil(region[col].max()))
    if lo == hi:
        return None
    return st.slider(nombre, lo, hi, (lo, hi), step=paso, format=formato, key=f"f_{E.pais}_{col}")


def pantalla_explorar():
    mejores, _ = resultado(E.sitio, E.rol or "other", E.descubrimiento)
    region = mejores[mejores["pais"] == E.pais]
    panel, derecha = st.columns([1, 1.8], gap="medium")
    with panel:
        with st.container(key="card_filtros"):
            st.markdown(f'<h1 class="aa-h1 chico">Places in {E.pais}</h1><p class="aa-paso">Filters</p>',
                        unsafe_allow_html=True)
            rangos = {"temp_dia": rango_slider(region, "temp_dia", "Day temperature", 1.0, "%d °C"),
                      "elevacion": rango_slider(region, "elevacion", "Elevation", 50.0, "%d m"),
                      "pendiente": rango_slider(region, "pendiente", "Slope", 0.1, "%.1f°")}
            ndvi_max = st.slider("Vegetation (NDVI) at most", 0.0, 1.0, 1.0, 0.05, format="%.2f", key=f"f_{E.pais}_ndvi")
        f = region
        for col, r in rangos.items():
            if r:
                f = f[f[col].between(r[0], r[1]) | f[col].isna()]
        if "ndvi" in f:
            f = f[f["ndvi"].fillna(0) <= ndvi_max]
        f = f.sort_values("puntaje", ascending=False)
        st.markdown(f'<p class="aa-paso">Results <span class="num">{len(f)} of {len(region)} places</span></p>',
                    unsafe_allow_html=True)
        if f.empty:
            st.info("No places fit these filters. Widen a slider to see results again.")
        primeros = f.head(6)
        fotos = fotos_tierra(tuple((round(float(a), 2), round(float(b), 2), 30) for a, b in zip(primeros.lat, primeros.lon)))
        for n, (idx, fila) in enumerate(primeros.iterrows()):
            with st.container(key=f"card_lugar_{idx}"):
                foto, texto = st.columns([1, 1.6], vertical_alignment="center", gap="small")
                foto.markdown(foto_html(fotos[n], f"Satellite view at {coord(fila.lat, fila.lon)}"),
                              unsafe_allow_html=True)
                extra = " · ".join(x for x in [
                    f"{fila.elevacion:,.0f} m" if pd.notna(fila.get("elevacion")) else "",
                    f"slope {fila.pendiente:.1f}°" if pd.notna(fila.get("pendiente")) else "",
                    f"{fila.temp_dia:.0f} °C by day" if pd.notna(fila.get("temp_dia")) else ""] if x)
                texto.markdown(f'<div class="aa-lugar"><b><strong>{fila.puntaje:.0f}</strong> · {tramo(fila.puntaje)}</b>'
                               f'<span>{coord(fila.lat, fila.lon)}</span><span>{extra}</span></div>', unsafe_allow_html=True)
                if texto.button("Open", key=f"abrir_{idx}", width="stretch"):
                    E.punto, E.punto_txt = int(idx), coord(fila.lat, fila.lon)
                    ir(4)
    with derecha:
        if not f.empty:
            mapa(f, f["lat"].round(2).astype(str) + ", " + f["lon"].round(2).astype(str),
                 centro=(float(f["lat"].mean()), float(f["lon"].mean())), zoom=zoom_para(f), alto=720)
            st.markdown(f'<p class="aa-credito-mapa">{CREDITO_EOX}</p>', unsafe_allow_html=True)


# ---------------------------------------------------------------- 4. Pantalla del punto
def comparador_html(img_tierra: bytes, sitio: dict, ancho_km: int) -> str:
    tierra = "data:image/jpeg;base64," + base64.b64encode(img_tierra).decode()
    tramo_km = ancho_km // 6
    escala = (f'<span class="esc izq">{tramo_km} km<i></i></span>' +
              (f'<span class="esc der">{tramo_km} km<i></i></span>' if sitio["escala"] else ""))
    cuerpo = sitio["nombre"].split(", ")[1]
    return f"""<div id="c" style="--corte:50%"><img src="{tierra}" alt="Earth">
      <img class="arriba" src="{data_uri(sitio['imagen'])}" alt="{cuerpo}">{escala}
      <span class="linea"></span><span class="rot izq">Earth</span><span class="rot der">{cuerpo}</span>
      <button id="a" aria-label="Drag to compare Earth and {cuerpo}" role="slider" aria-valuemin="0" aria-valuemax="100" aria-valuenow="50">&#8596;</button></div>
    <style>body{{margin:0;font-family:Inter,system-ui,sans-serif}}
    #c{{position:relative;aspect-ratio:4/3;max-height:380px;border-radius:12px;overflow:hidden;touch-action:none;user-select:none;cursor:ew-resize;background:#222}}
    #c img{{position:absolute;inset:0;width:100%;height:100%;object-fit:cover;pointer-events:none}}
    .arriba{{clip-path:inset(0 0 0 var(--corte))}}
    .linea{{position:absolute;top:0;bottom:0;left:var(--corte);width:2px;margin-left:-1px;background:#fff}}
    #a{{position:absolute;top:50%;left:var(--corte);width:44px;height:44px;margin:-22px 0 0 -22px;border-radius:50%;border:0;background:#fff;color:#111827;font-size:18px;cursor:ew-resize}}
    .rot{{position:absolute;bottom:8px;padding:4px 8px;border-radius:4px;background:rgba(17,24,39,.75);color:#fff;font-size:12px}}
    .rot.izq{{left:8px}} .rot.der{{right:8px}}
    .esc{{position:absolute;top:8px;width:50%;display:flex;flex-direction:column;gap:4px;color:#fff;font-size:12px;font-weight:600;text-shadow:0 1px 2px #000}}
    .esc i{{display:block;width:33.3%;height:4px;border-radius:2px;background:#fff}}
    .esc.izq{{left:8px}} .esc.der{{right:8px;align-items:flex-end}}</style>
    <script>const c=document.getElementById('c'),a=document.getElementById('a');
    const f=x=>{{const p=Math.max(0,Math.min(100,(x-c.getBoundingClientRect().left)/c.offsetWidth*100));c.style.setProperty('--corte',p+'%');a.setAttribute('aria-valuenow',Math.round(p));}};
    c.onpointerdown=e=>{{c.setPointerCapture(e.pointerId);f(e.clientX)}};
    c.onpointermove=e=>{{if(c.hasPointerCapture(e.pointerId))f(e.clientX)}};
    a.onkeydown=e=>{{const r=c.getBoundingClientRect(),v=+a.getAttribute('aria-valuenow');
      if(e.key==='ArrowLeft')f(r.left+(v-5)/100*r.width);if(e.key==='ArrowRight')f(r.left+(v+5)/100*r.width)}};</script>"""


def pantalla_punto():
    mejores, saturadas = resultado(E.sitio, E.rol or "other", E.descubrimiento)
    if E.punto not in mejores.index:
        st.info("Pick a place first.")
        if st.button("Go to best regions", type="primary"):
            ir(2)
        return
    p = mejores.loc[E.punto]
    ref_api = referencias()[E.sitio]
    ref = ref_api["valores"]
    sitio, cuerpo = SITIOS[E.sitio], ref_api["cuerpo"]
    st.markdown(f'<div class="aa-total"><strong>{p.puntaje:.0f}</strong><span>{tramo(p.puntaje)}</span>'
                f'<small>vs {sitio["nombre"]} · {ROLES[E.rol or "other"]["titulo"]} weights</small></div>', unsafe_allow_html=True)

    izq, der = st.columns([1.1, 1])
    with izq:
        ancho = ancho_vista_km(cuerpo)
        img = foto_tierra(float(p.lat), float(p.lon), ancho)
        if img:
            componentes.html(comparador_html(img, sitio, ancho), height=390)
            st.caption(f"Earth view {ancho} km wide: Sentinel-2 cloudless 2021 (EOX). Reference: {sitio['credito']}.")
        else:
            st.info("Satellite view unavailable right now. Check the internet connection and reopen this place.")
    with der.container(key="card_ficha"):
        filas = sorted(((c[2:], float(p[c])) for c in p.index if c.startswith("s_") and pd.notna(p[c])), key=lambda x: -x[1])
        datos_lugar = [(VARIABLES[k], f"{p[k]:,.1f} {UNIDADES.get(k, '')}".strip())
                       for k in ("pendiente", "elevacion", "temp_dia", "temp_noche") if k in p.index and pd.notna(p[k])]
        st.markdown(f'<p class="aa-paso">Site preview <span>{p.pais}</span></p>' + "".join(
            f'<div class="aa-dato"><span>{a}</span><b class="num">{b}</b></div>' for a, b in datos_lugar),
            unsafe_allow_html=True)
        st.markdown("**Similarity by variable**")
        st.markdown('<div class="aa-barras">' + "".join(
            f'<div class="aa-fila"><span>{VARIABLES.get(k, k)}</span><span class="pista"><i style="width:{v * 100:.0f}%"></i></span>'
            f'<output>{v * 100:.0f}</output></div>' for k, v in filas) + "</div>", unsafe_allow_html=True)
        lista = lambda xs: '<ul class="aa-lista">' + ("".join(
            f"<li><span>{VARIABLES.get(k, k)}</span><b>{v * 100:.0f}</b></li>" for k, v in xs) or "<li>None</li>") + "</ul>"
        a, b = st.columns(2)
        a.markdown('<p class="aa-si">Matches</p>' + lista([x for x in filas if x[1] >= 0.75]), unsafe_allow_html=True)
        b.markdown('<p class="aa-no">Breaks the analogy</p>' + lista([x for x in filas if x[1] < 0.5]), unsafe_allow_html=True)

    st.markdown("#### What no place on Earth reproduces")
    st.markdown('<div class="aa-limites">' + "".join(f"<b>{a}</b><span>{b}</span><span>{c}</span>" for a, b, c in LIMITES[cuerpo]) + "</div>",
                unsafe_allow_html=True)
    st.caption(FUENTES_LIMITES[cuerpo])

    st.markdown("#### Earth values next to the reference")
    tabla = []
    for k in CRUDOS:
        if k in p.index and pd.notna(p[k]):
            v_ref = ref.get(k)
            tiene_ref = v_ref is not None and pd.notna(v_ref)
            tabla.append({"Variable": VARIABLES.get(k, k),
                          "This place": f"{p[k]:,.1f} {UNIDADES.get(k, '')}".strip(),
                          sitio["nombre"]: f"{float(v_ref):,.1f} {UNIDADES.get(k, '')}".strip() if tiene_ref else "Not used",
                          "Earth reaches it": "No" if k in saturadas else ("Yes" if tiene_ref else "")})
    if tabla:
        cab = list(tabla[0])
        st.markdown('<div style="overflow-x:auto"><table class="aa-tabla"><thead><tr>' + "".join(f"<th>{c}</th>" for c in cab)
                    + "</tr></thead><tbody>" + "".join("<tr>" + "".join(f"<td>{f[c]}</td>" for c in cab) + "</tr>" for f in tabla)
                    + "</tbody></table></div>", unsafe_allow_html=True)

    cerca = api.celda(float(p.lat), float(p.lon), E.sitio)["analogo_cercano"]
    st.caption(f"Nearest well-known analog: {cerca['nombre']}, {cerca['km']:,.0f} km away.")

    with st.expander("Methodology and evidence"):
        st.markdown(
            "- Each 0.25° cell (~28 km) is compared with the reference site variable by variable, then combined with a "
            "weighted geometric mean (the form of the Earth Similarity Index). A required variable below 0.5 caps the score at 49.\n"
            "- Earth: MODIS Aqua surface temperature (13:30 and 01:30, 2018–2023), MODIS NDVI, land cover and snow, ETOPO1 relief.\n"
            "- Mars references: MEDA and REMS ground temperature (Atri et al. 2022), MOLA slope. Moon: Diviner temperature, LOLA slope.\n"
            "- Full source list: USO_DE_IA_Y_FUENTES.md and datos/FUENTES.md in the repository.")
    with st.expander("Limitations"):
        falt = SALUD["faltan"]
        st.markdown(
            "- 28 km cells hide small craters, lava tubes and local terrain.\n"
            "- Multi-year means hide seasons and El Niño years.\n"
            "- Similarity is relative to Earth: the coldest place on Earth is still warmer than a lunar night.\n"
            + (f"- Not loaded yet: {', '.join(VARIABLES.get(x, x) for x in falt)}.\n" if falt else "")
            + ("- Shackleton has few reference variables, so scores can saturate at 100.\n" if E.sitio == "shackleton" else ""))
    c1, c2 = st.columns(2)
    datos = {"place": {"country": p.pais, "lat": float(p.lat), "lon": float(p.lon)}, "reference": sitio["nombre"],
             "role": E.rol, "score": round(float(p.puntaje), 1), "band": tramo(p.puntaje),
             "similarity": {VARIABLES.get(k, k): round(v, 3) for k, v in filas},
             "earth_values": {k: (None if pd.isna(p[k]) else float(p[k])) for k in CRUDOS if k in p.index},
             "earth_never_reaches": list(saturadas), "sources": "USO_DE_IA_Y_FUENTES.md"}
    c1.download_button("Download place data (JSON)", json.dumps(datos, indent=2, ensure_ascii=False),
                       file_name=f"analog_atlas_{p.lat:.2f}_{p.lon:.2f}.json", mime="application/json",
                       width="stretch")
    if E.rol == "researcher" and c2.button("Run robustness check", width="stretch"):
        with st.spinner("Moving each weight ±20% and re-ranking"):
            r = api.sensibilidad(E.sitio, pesos_para(E.sitio, E.rol), n_top=10)
        st.success(f"The global top 10 keeps {r:.0%} of its places when each weight moves ±20%.")


[pantalla_inicio, pantalla_rol, pantalla_regiones, pantalla_explorar, pantalla_punto][E.paso]()

_faltan = SALUD["faltan"]
st.markdown(f'<p class="aa-pie num">Earth grid: {SALUD["celdas"]:,} land cells of 0.25° (~28 km)'
            + (f" · Not loaded yet: {', '.join(VARIABLES.get(f, f) for f in _faltan)} (the engine skips them)" if _faltan else "")
            + " · by Ctrl Z · NASA Space Apps 2026</p>", unsafe_allow_html=True)
