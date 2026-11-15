# Analog Atlas · views/estilos.py
# v0.3 · 2026-11-14 · Isabelita (equipo Ctrl Z)
# Paletas y CSS de la app (mismo sistema que el prototipo aprobado): 1 acento por paleta, Inter,
# espaciado en múltiplos de 4, botones de 44 px, dígitos tabulares.

import base64
from functools import lru_cache
from pathlib import Path

ASSETS = Path(__file__).resolve().parent / "assets"

# Dos modos, 1 solo acento cada uno (morado de los mockups del equipo). Claro por defecto.
MODOS = {
    "light": {"nombre": "Atlas Light", "bg": "#F6F6F8", "surface": "#FFFFFF", "ink": "#111827", "muted": "#4B5563",
              "line": "#E5E7EB", "accent": "#5B4CDB", "accent_ink": "#FFFFFF", "accent_soft": "#EEECFC",
              "bien": "#15803D", "mal": "#B91C1C", "sombra": "0 8px 24px rgba(17,24,39,.08)"},
    "dark": {"nombre": "Lunar Regolith", "bg": "#0B0F17", "surface": "#131A26", "ink": "#F8FAFC", "muted": "#94A3B8",
             "line": "#233044", "accent": "#A29BFE", "accent_ink": "#0B0F17", "accent_soft": "#221F45",
             "bien": "#4ADE80", "mal": "#F87171", "sombra": "0 8px 24px rgba(0,0,0,.45)"},
}

@lru_cache(maxsize=None)
def data_uri(nombre: str) -> str:
    ruta = ASSETS / nombre
    tipo = "image/png" if ruta.suffix == ".png" else "image/jpeg"
    return f"data:{tipo};base64," + base64.b64encode(ruta.read_bytes()).decode()


def logo_html(alto_px: int, color_a: str) -> str:
    """Logo original (A + órbita) recoloreable con la paleta: dos capas usadas como máscara."""
    ancho = round(alto_px * 207 / 150)
    capa = ("position:absolute;inset:0;-webkit-mask-size:contain;mask-size:contain;-webkit-mask-repeat:no-repeat;"
            "mask-repeat:no-repeat;-webkit-mask-position:center;mask-position:center;")
    return (f'<span style="position:relative;display:inline-block;width:{ancho}px;height:{alto_px}px;flex:none" aria-hidden="true">'
            f'<i style="{capa}background:{color_a};-webkit-mask-image:url({data_uri("logo_a.png")});mask-image:url({data_uri("logo_a.png")})"></i>'
            f'<i style="{capa}background:linear-gradient(100deg,var(--accent),color-mix(in srgb,var(--accent) 45%,#fff));'
            f'-webkit-mask-image:url({data_uri("logo_orbita.png")});mask-image:url({data_uri("logo_orbita.png")})"></i></span>')


def css(modo: str) -> str:
    p = MODOS[modo]
    return f"""
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
<style>
:root{{--bg:{p['bg']};--surface:{p['surface']};--ink:{p['ink']};--muted:{p['muted']};--line:{p['line']};
  --accent:{p['accent']};--accent-ink:{p['accent_ink']};--accent-soft:{p['accent_soft']};--bien:{p['bien']};--mal:{p['mal']};
  --r:12px;--sombra:{p['sombra']};color-scheme:{'dark' if modo == 'dark' else 'light'}}}
html,body,.stApp,[class*="css"]{{font-family:"Inter","Segoe UI",system-ui,sans-serif}}
.stApp{{background:var(--bg);color:var(--ink);animation:cambio-{modo} 200ms cubic-bezier(.2,.7,.3,1)}}
@keyframes cambio-{modo}{{from{{opacity:.6;filter:blur(4px)}}to{{opacity:1;filter:none}}}}
[data-testid="stSidebar"],[data-testid="stSidebarCollapsedControl"]{{display:none}}
.stApp p,.stApp li,.stApp label,.stApp h1,.stApp h2,.stApp h3,.stApp h4,.stApp [data-testid="stMarkdownContainer"]{{color:var(--ink)}}
[data-testid="stExpander"]{{background:var(--surface);border-color:var(--line);border-radius:var(--r)}}
[data-testid="stExpander"] summary{{color:var(--ink)}}
[data-baseweb="input"] input,[data-baseweb="select"] *{{background:var(--surface);color:var(--ink)}}
[data-testid="stSlider"] [data-testid="stTickBarMin"],[data-testid="stSlider"] [data-testid="stTickBarMax"],[data-testid="stSliderThumbValue"]{{color:var(--muted)}}
.aa-tabla{{width:100%;border-collapse:collapse;font-size:14px;color:var(--ink);font-variant-numeric:tabular-nums}}
.aa-tabla th,.aa-tabla td{{padding:8px 12px;text-align:left;border-bottom:1px solid var(--line)}}
.aa-tabla th{{color:var(--muted);font-weight:500}}
.aa-cabecera{{display:flex;align-items:center;gap:12px;min-height:44px}}
.aa-cabecera b{{font-size:18px;color:var(--ink)}} .aa-cabecera span{{color:var(--muted);font-size:14px}}
.aa-pie{{color:var(--muted);font-size:13px;margin-top:32px}}
[data-testid="stHeader"]{{background:transparent}}
[data-testid="stSidebar"]{{background:var(--surface);border-right:1px solid var(--line)}}
h1,h2,h3,h4{{color:var(--ink);text-wrap:balance;letter-spacing:0;font-weight:600}}
p,li,label,span,div{{color:inherit}}
.stMarkdown,.stCaption,[data-testid="stWidgetLabel"] p{{color:var(--ink)}}
[data-testid="stCaptionContainer"]{{color:var(--muted)}}
.num,[data-testid="stMetricValue"]{{font-variant-numeric:tabular-nums}}
/* Botones: 44 px, presión 0.97, un solo acento */
.stButton>button,.stDownloadButton>button,.stFormSubmitButton>button{{min-height:44px;border-radius:var(--r);font-weight:600;
  border:1px solid var(--line);background:var(--surface);color:var(--ink);transition:transform 150ms cubic-bezier(.2,.7,.3,1),background-color 150ms}}
.stButton>button:active,.stDownloadButton>button:active,.stFormSubmitButton>button:active{{transform:scale(.97)}}
.stButton>button[kind^="primary"],.stFormSubmitButton>button[kind^="primary"],.stDownloadButton>button[kind^="primary"]{{background:var(--accent);color:var(--accent-ink);border-color:var(--accent)}}
.stButton>button:hover{{border-color:var(--accent);color:var(--ink)}}
.stButton>button[kind^="primary"]:hover,.stFormSubmitButton>button[kind^="primary"]:hover{{filter:brightness(1.08);color:var(--accent-ink)}}
.stButton>button:focus-visible{{outline:2px solid var(--accent);outline-offset:2px}}
[data-baseweb="slider"] [role="slider"]{{background:var(--accent);box-shadow:none}}
[data-baseweb="input"],[data-baseweb="select"]>div,[data-baseweb="textarea"]{{background:var(--surface);border-color:var(--line);border-radius:var(--r)}}
input,textarea{{color:var(--ink)!important}}
/* Bloques propios */
.st-key-migas{{margin:0 0 16px;font-size:15px;flex-wrap:wrap;row-gap:0}}
.st-key-migas p{{margin:0}}
.st-key-migas button{{min-height:44px;padding:0 4px;color:var(--accent);font-weight:500}}
.st-key-migas button:hover{{text-decoration:underline;text-underline-offset:4px}}
.aa-sep{{color:var(--muted);padding:0 4px}} .aa-rol{{color:var(--muted)}}
.aa-hero{{position:relative;border-radius:20px;overflow:hidden;min-height:340px;display:flex;flex-direction:column;align-items:center;
  justify-content:center;gap:16px;padding:32px 24px;text-align:center;color:#fff;
  background:linear-gradient(180deg,rgba(10,14,22,.25),rgba(10,14,22,.6)),url({data_uri('portada_sechura.jpg')}) center/cover}}
.aa-hero .marca{{display:flex;align-items:center;gap:16px}}
.aa-hero strong{{font-size:clamp(32px,5vw,52px);font-weight:600;line-height:1;color:#fff}}
.aa-hero .sub{{font-size:13px;letter-spacing:.32em;text-transform:uppercase;color:color-mix(in srgb,var(--accent) 35%,#fff)}}
.aa-hero p{{color:#fff;opacity:.92;max-width:56ch;margin:0}}
.aa-hero small{{position:absolute;right:12px;bottom:8px;font-size:12px;opacity:.8;color:#fff}}
.aa-barra{{display:flex;align-items:center;gap:12px;margin-bottom:8px}}
.aa-barra b{{font-size:18px;color:var(--ink)}} .aa-barra span{{color:var(--muted);font-size:14px}}
.aa-aviso{{border-radius:var(--r);padding:12px 16px;background:var(--accent-soft);color:var(--ink);font-size:14px;margin-bottom:12px}}
.aa-aviso.peligro{{background:color-mix(in srgb,var(--mal) 14%,var(--surface));border-left:4px solid var(--mal)}}
.aa-total{{display:flex;align-items:baseline;gap:8px;flex-wrap:wrap}}
.aa-total strong{{font-size:48px;font-weight:700;line-height:1;color:var(--ink);font-variant-numeric:tabular-nums}}
.aa-total span{{font-weight:600;color:var(--ink)}} .aa-total small{{color:var(--muted)}}
.aa-barras{{display:flex;flex-direction:column;gap:8px}}
.aa-fila{{display:grid;grid-template-columns:minmax(0,1fr) 120px 40px;gap:12px;align-items:center;font-size:14px;color:var(--ink)}}
.aa-fila .pista{{height:8px;border-radius:4px;background:var(--line);overflow:hidden}}
.aa-fila .pista i{{display:block;height:100%;background:var(--accent);border-radius:4px}}
.aa-fila output{{text-align:right;color:var(--muted);font-variant-numeric:tabular-nums}}
.aa-lista{{list-style:none;margin:0;padding:0;display:flex;flex-direction:column;gap:8px;font-size:14px;color:var(--ink)}}
.aa-lista li{{display:flex;justify-content:space-between;gap:8px}}
.aa-lista b{{font-variant-numeric:tabular-nums}}
.aa-si{{color:var(--bien);font-weight:600;margin:0 0 8px}} .aa-no{{color:var(--mal);font-weight:600;margin:0 0 8px}}
.aa-limites{{display:grid;grid-template-columns:1fr auto auto;gap:8px 16px;font-size:14px;color:var(--ink)}}
.aa-limites span{{color:var(--muted);font-variant-numeric:tabular-nums}}
/* Mockups: contenido centrado, tarjetas blancas, fotos reales, mapa satelital */
[data-testid="stMainBlockContainer"]{{max-width:1168px;padding-inline:24px}}
.aa-h1{{font-size:32px;font-weight:600;line-height:1.2;margin:0 0 8px;color:var(--ink)}}
.aa-h1.chico{{font-size:24px}}
.aa-nota{{color:var(--muted)!important;font-size:14px;margin:0}}
.aa-paso{{display:flex;justify-content:space-between;align-items:baseline;gap:8px;margin:8px 0 0;font-size:12px;font-weight:600;
  letter-spacing:.04em;text-transform:uppercase;color:var(--muted)!important}}
.aa-paso span{{text-transform:none;letter-spacing:0;font-weight:400}}
[class*="st-key-card_"]{{background:var(--surface);border:1px solid var(--line);border-radius:16px;padding:8px;gap:8px;box-shadow:var(--sombra)}}
[class*="st-key-card_sitio_"][class*="_on"]{{border:2px solid var(--accent);box-shadow:0 0 0 4px var(--accent-soft)}}
.st-key-card_filtros{{padding:16px;gap:12px}}
.st-key-card_ficha{{padding:24px;gap:12px}}
.aa-foto{{display:block;width:100%;aspect-ratio:4/3;object-fit:cover;border-radius:12px;background:var(--line)}}
.aa-foto.ancha{{aspect-ratio:16/9}}
.aa-region{{display:flex;justify-content:space-between;align-items:center;gap:12px;padding:4px 8px 0}}
.aa-region div{{display:flex;flex-direction:column;gap:4px}}
.aa-region b{{color:var(--ink);font-size:16px}} .aa-region span{{color:var(--muted);font-size:12px;font-variant-numeric:tabular-nums}}
.aa-region strong{{font-size:28px;font-weight:700;color:var(--accent);font-variant-numeric:tabular-nums}}
.aa-lugar{{display:flex;flex-direction:column;gap:4px;font-size:12px;color:var(--muted);font-variant-numeric:tabular-nums}}
.aa-lugar b{{font-size:14px;color:var(--ink)}} .aa-lugar strong{{color:var(--accent)}}
.aa-fila-titulo{{display:flex;justify-content:space-between;align-items:baseline;gap:16px;margin-top:8px}}
.aa-fila-titulo h2{{font-size:20px;margin:0;padding:0}} .aa-fila-titulo span{{color:var(--muted);font-size:12px}}
.aa-dato{{display:flex;justify-content:space-between;gap:12px;padding:8px 0;border-bottom:1px solid var(--line);font-size:14px}}
.aa-dato span{{color:var(--muted)}}
.aa-credito-mapa{{font-size:12px;color:var(--muted);margin:-8px 0 0}}
[data-testid="stPlotlyChart"]{{border-radius:16px;overflow:hidden;border:1px solid var(--line)}}
.st-key-modal_tarjeta [class*="st-key-sitio_"] button{{min-height:56px;padding:8px 12px}}
.st-key-modal_tarjeta [class*="st-key-rol_"] button::after{{content:"›";margin-left:auto;padding-left:12px;font-size:24px;line-height:1;color:var(--muted)}}
[data-testid="stToolbar"]{{display:none}}
[data-testid="stMainBlockContainer"]{{padding-top:24px;padding-bottom:48px}}
.stButton>button[kind="tertiary"]{{border:0!important;background:none!important;box-shadow:none;color:var(--accent);padding:0 4px;min-height:44px}}
.stButton>button[kind="tertiary"]:hover{{text-decoration:underline;text-underline-offset:4px;color:var(--accent)}}
.st-key-migas{{gap:4px!important;align-items:center}}
.aa-total{{margin-bottom:16px}}
.aa-lista{{padding-left:0!important;margin:0!important}} .aa-lista li{{margin:0!important}}
.aa-si,.aa-no{{margin:16px 0 8px!important}}
.st-key-modal_rol{{position:fixed;inset:0;z-index:999990;display:flex!important;align-items:center;justify-content:center;padding:16px;background:rgba(6,9,15,.62);backdrop-filter:blur(2px);animation:entra-modal 200ms cubic-bezier(.2,.7,.3,1)}}
.st-key-modal_tarjeta{{margin:auto;width:min(720px,100%);max-height:calc(100vh - 32px);overflow-y:auto;background:var(--surface);border:1px solid var(--line);border-radius:20px;padding:24px;gap:16px;box-shadow:var(--sombra)}}
.st-key-modal_tarjeta h3{{margin:0;font-size:20px}}
.st-key-modal_tarjeta .stButton>button{{min-height:64px;text-align:left;justify-content:flex-start;padding:12px 16px}}
.st-key-modal_tarjeta .stButton>button>div,.st-key-modal_tarjeta .stButton>button p{{width:100%;text-align:left;margin:0}}
@keyframes entra-modal{{from{{opacity:0}}to{{opacity:1}}}}
@media (prefers-reduced-motion:reduce){{*{{transition:none!important;animation:none!important}}}}
</style>"""
