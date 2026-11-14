"""
Interfaz gráfica Streamlit para Atlas Analog.
Se comunica con la API interna para renderizar mapas y análisis.
"""

import logging
import requests
import streamlit as st
import folium
from streamlit_folium import st_folium
import plotly.graph_objects as go

from config.settings import API_HOST, API_PORT

# Configuración
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

API_BASE_URL = f"http://{API_HOST}:{API_PORT}"


def main():
    """Función principal de la aplicación Streamlit."""
    st.set_page_config(
        page_title="Atlas Analog - Análogos Terrestres para Bases Espaciales",
        layout="wide",
    )
    
    st.title("Atlas Analog")
    st.subheader("Identificación de Análogos Terrestres para Bases Lunares y Marcianas")
    st.markdown("---")
    
    # Sidebar: Configuración de búsqueda
    st.sidebar.header("Configuración de Búsqueda")
    
    sitio = st.sidebar.selectbox(
        "Sitio de Referencia:",
        ["jezero", "gale", "shackleton", "marius_hills"],
        help="Seleccione un sitio de la Luna o Marte como referencia"
    )
    
    descubrimiento = st.sidebar.checkbox(
        "Modo Descubrimiento",
        value=False,
        help="Ocultar análogos conocidos (Atacama, Valle de la Muerte, etc.)"
    )
    
    top_n = st.sidebar.slider(
        "Número de resultados:",
        min_value=5,
        max_value=50,
        value=10,
        step=5
    )
    
    # Botón de búsqueda
    if st.sidebar.button("Buscar Análogos", type="primary"):
        with st.spinner("Calculando similitud..."):
            try:
                # Llamar a la API
                response = requests.post(
                    f"{API_BASE_URL}/api/buscar",
                    json={
                        "sitio": sitio,
                        "pesos": {},  # Usar pesos por defecto del servidor
                        "imprescindibles": [],
                        "descubrimiento": descubrimiento,
                        "top": top_n,
                    },
                    timeout=30,
                )
                response.raise_for_status()
                data = response.json()
                
                # Mostrar resultados
                mostrar_resultados(data)
                
            except requests.exceptions.ConnectionError:
                st.error("No se pudo conectar con la API. Verifique que el servidor esté corriendo.")
            except Exception as e:
                st.error(f"Error en la búsqueda: {str(e)}")
                logger.error("Error en búsqueda: %s", str(e), exc_info=True)


def mostrar_resultados(data: dict):
    """Muestra los resultados de la búsqueda en la interfaz."""
    st.header(f"Resultados para: {data['sitio']}")
    
    if data["tierra_no_llega"]:
        st.warning(
            f"La Tierra no alcanza los valores de referencia en: {', '.join(data['tierra_no_llega'])}"
        )
    
    # Mapa
    st.subheader("Mapa de Análogos")
    mostrar_mapa(data["lugares"])
    
    # Tabla de resultados
    st.subheader("Top Análogos Terrestres")
    mostrar_tabla(data["lugares"])
    
    # Gráfico de radar para el mejor análogo
    if data["lugares"]:
        st.subheader("Análisis Comparativo del Mejor Análogo")
        mostrar_radar(data["lugares"][0], data["sitio"])


def mostrar_mapa(lugares: list):
    """Renderiza el mapa interactivo con los análogos."""
    if not lugares:
        st.info("No se encontraron análogos con los criterios seleccionados.")
        return
    
    # Centro del mapa
    lat_center = sum(l["lat"] for l in lugares) / len(lugares)
    lon_center = sum(l["lon"] for l in lugares) / len(lugares)
    
    m = folium.Map(location=[lat_center, lon_center], zoom_start=3)
    
    for lugar in lugares:
        # Color según puntaje
        if lugar["puntaje"] >= 75:
            color = "green"
        elif lugar["puntaje"] >= 50:
            color = "orange"
        else:
            color = "red"
        
        folium.Marker(
            location=[lugar["lat"], lugar["lon"]],
            popup=f"Puntaje: {lugar['puntaje']:.1f}<br>Tramo: {lugar['tramo']}",
            icon=folium.Icon(color=color),
        ).add_to(m)
    
    st_folium(m, width=None, height=500)


def mostrar_tabla(lugares: list):
    """Muestra la tabla de resultados."""
    import pandas as pd
    
    df = pd.DataFrame(lugares)
    df = df[["lat", "lon", "puntaje", "tramo"]]
    df.columns = ["Latitud", "Longitud", "Puntaje", "Tramo"]
    
    st.dataframe(df, use_container_width=True)


def mostrar_radar(lugar: dict, sitio: str):
    """Muestra el gráfico de radar comparativo."""
    desglose = lugar["desglose"]
    variables = list(desglose.keys())
    valores = list(desglose.values())
    
    # Cerrar el gráfico
    variables_closed = variables + [variables[0]]
    valores_closed = valores + [valores[0]]
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatterpolar(
        r=valores_closed,
        theta=variables_closed,
        fill="toself",
        name=f"Análogo Terrestre (Puntaje: {lugar['puntaje']:.1f})",
    ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, range=[0, 1]),
        ),
        showlegend=True,
        title=f"Desglose de Similitud - {lugar['lat']:.2f}, {lugar['lon']:.2f}",
    )
    
    st.plotly_chart(fig, use_container_width=True)


if __name__ == "__main__":
    main()