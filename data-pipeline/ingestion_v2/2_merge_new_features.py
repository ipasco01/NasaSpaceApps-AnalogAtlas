"""
Módulo de Integración V2 (Aislado).
Fusiona las nuevas variables (viento, swir) con el dataset original.
"""

import pandas as pd
import geopandas as gpd
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s | %(levelname)s | %(message)s')
logger = logging.getLogger(__name__)

# --- RUTAS (Ajusta según tus nombres de archivo reales) ---
ORIGINAL_DATASET = Path("../datos/tu_dataset_original.parquet") # Tu archivo actual
NEW_FEATURES_CSV = Path("../datos/nuevas_variables_viento_swir.csv") # El descargado de Drive
OUTPUT_V2 = Path("../datos/earth_grid_v2.parquet")

def merge_datasets():
    if not ORIGINAL_DATASET.exists() or not NEW_FEATURES_CSV.exists():
        logger.error("No se encuentran los archivos de entrada. Verifica las rutas.")
        return

    logger.info("Cargando datasets...")
    df_original = pd.read_parquet(ORIGINAL_DATASET)
    df_nuevo = pd.read_csv(NEW_FEATURES_CSV)

    # GEE devuelve las coordenadas en una columna llamada '.geo' (string JSON) o 'longitude'/'latitude'
    # Dependiendo de la exportación. Lo estandarizamos aquí:
    if '.geo' in df_nuevo.columns:
        # Extraer coordenadas si vienen en el formato por defecto de GEE
        import json
        coords = df_nuevo['.geo'].apply(lambda x: json.loads(x)['coordinates'])
        df_nuevo['longitude'] = coords.apply(lambda x: x[0])
        df_nuevo['latitude'] = coords.apply(lambda x: x[1])
        df_nuevo = df_nuevo.drop(columns=['.geo'])

    # Crear GeoDataFrames para cruce espacial
    logger.info("Realizando cruce espacial (Nearest Neighbor)...")
    gdf_orig = gpd.GeoDataFrame(
        df_original, 
        geometry=gpd.points_from_xy(df_original.longitude, df_original.latitude),
        crs="EPSG:4326"
    )
    gdf_nuevo = gpd.GeoDataFrame(
        df_nuevo, 
        geometry=gpd.points_from_xy(df_nuevo.longitude, df_nuevo.latitude),
        crs="EPSG:4326"
    )

    # Hacer un join espacial buscando el punto más cercano
    # Esto es robusto sin importar si las resoluciones son distintas
    merged = gpd.sjoin_nearest(
        gdf_orig, 
        gdf_nuevo[['geometry', 'wind_speed', 'swir1', 'swir2']], 
        how="left", 
        distance_col="distancia_metros"
    )

    # Limpieza final
    merged = merged.drop(columns=['geometry', 'index_right', 'distancia_metros'])
    
    # Guardar el nuevo dataset
    merged.to_parquet(OUTPUT_V2, index=False)
    logger.info(f"Dataset V2 generado con éxito en: {OUTPUT_V2}")
    logger.info(f"Columnas finales: {list(merged.columns)}")

if __name__ == "__main__":
    merge_datasets()
