"""
Módulo de Extracción V2 (Aislado).
Exporta variables de viento y SWIR desde Google Earth Engine a Google Drive.
"""

import ee
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO, format='%(asctime)s | %(levelname)s | %(message)s')
logger = logging.getLogger(__name__)

def init_gee():
    """Inicializa la API de Google Earth Engine."""
    try:
        # Si tienes un ID de proyecto de Google Cloud, pásalo aquí: ee.Initialize(project='tu-proyecto')
        ee.Initialize() 
        logger.info("Google Earth Engine inicializado correctamente.")
    except Exception as e:
        logger.error(f"Error al inicializar GEE. Asegúrate de haber ejecutado 'earthengine authenticate'. Detalle: {e}")
        raise

def export_features_to_drive():
    # 1. Definir el Área de Interés (AOI) - Ejemplo: Sechura
    aoi = ee.Geometry.Rectangle([-81.5, -6.5, -79.5, -4.5])

    # 2. MERRA-2 (Viento)
    logger.info("Procesando MERRA-2 (Viento)...")
    merra = (ee.ImageCollection('NASA/GSFC/MERRA/slv/2')
             .filterDate('2024-01-01', '2024-01-31')
             .filterBounds(aoi)
             .select(['U10M', 'V10M'])
             .mean())
    
    wind_speed = merra.expression(
        'sqrt(U10M*U10M + V10M*V10M)', {
            'U10M': merra.select('U10M'),
            'V10M': merra.select('V10M')
        }).rename('wind_speed')

    # 3. Sentinel-2 (SWIR)
    logger.info("Procesando Sentinel-2 (SWIR)...")
    s2 = (ee.ImageCollection('COPERNICUS/S2_SR_HARMONIZED')
          .filterDate('2024-01-01', '2024-01-31')
          .filterBounds(aoi)
          .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 20))
          .median()
          .select(['B11', 'B12'], ['swir1', 'swir2']))

    # 4. Alinear resolución (Remuestrear viento a 20m de Sentinel-2)
    wind_aligned = wind_speed.resample('bilinear').reproject(
        crs=s2.projection(), scale=20
    )
    
    # 5. Combinar bandas
    combined = s2.addBands(wind_aligned).clip(aoi)

    # 6. Muestrear en una cuadrícula (cada 100 metros para no saturar el CSV)
    # Usamos un espaciado para que no haya millones de puntos
    sample = combined.sample(
        region=aoi,
        scale=100,  # Ajusta esto según tu dataset actual (ej. 1000m para 1km)
        geometries=True,
        dropNulls=True
    )

    # 7. Exportar a Google Drive
    task = ee.batch.Export.table.toDrive(
        collection=sample,
        description='nuevas_variables_viento_swir',
        folder='NASA_App_Data',
        fileFormat='CSV'
    )
    
    task.start()
    logger.info("Tarea de exportación iniciada. Revisa tu Google Drive en unos minutos (Carpeta: NASA_App_Data).")

if __name__ == "__main__":
    init_gee()
    export_features_to_drive()
