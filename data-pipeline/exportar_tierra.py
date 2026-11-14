# Atlas Analog · exportar_tierra.py
# v0.3 · 2026-11-14 · Isabelita (equipo Ctrl Z)
# Junta las capas de la Tierra en Google Earth Engine y lanza la exportación global a Google Drive.
# Uso: python exportar_tierra.py --proyecto TU_PROYECTO_DE_GOOGLE_CLOUD
# Requiere haber iniciado sesión una vez: earthengine authenticate

import argparse
import ee

INICIO, FIN = "2018-01-01", "2023-12-31"
CARPETA_DRIVE = "AtlasAnalog"
# Celdas de 0,25° (~28 km): 1440 x 720 para toda la Tierra
CUADRICULA = [0.25, 0, -180, 0, -0.25, 90]


def capas_tierra() -> ee.Image:
    # Relieve global con polos: ETOPO1 (NOAA), ~1,8 km. NASADEM solo cubre de 60° N a 56° S
    # y recortaba la exportación a esa franja.
    elevacion = ee.Image("NOAA/NGDC/ETOPO1").select("ice_surface").rename("elevacion")
    # La pendiente NO se calcula aquí: ee.Terrain.slope sobre ETOPO1 falla en los bordes de bloque
    # de la exportación. tif_a_tabla.py la calcula desde la elevación, igual que para la Luna y Marte.

    # Temperatura de superficie: MODIS en Aqua (NASA), 1 km, °C. Aqua pasa a las 13:30 y 01:30,
    # más cerca del máximo y del mínimo del día que Terra (10:30 y 22:30). Las referencias de la Luna
    # y Marte son máximos y mínimos, así que esto reduce el desfase. Sigue siendo una aproximación:
    # el mínimo real ocurre antes del amanecer.
    lst = ee.ImageCollection("MODIS/061/MYD11A2").filterDate(INICIO, FIN)
    temp_dia = lst.select("LST_Day_1km").mean().multiply(0.02).subtract(273.15).rename("temp_dia")
    temp_noche = lst.select("LST_Night_1km").mean().multiply(0.02).subtract(273.15).rename("temp_noche")
    rango = temp_dia.subtract(temp_noche).rename("rango_termico")
    # Indicador de permafrost: temperatura media anual de superficie bajo 0 °C (aproximación, no medición directa)
    permafrost = temp_dia.add(temp_noche).divide(2).lt(0).rename("permafrost_proxy")

    # Lluvia: GPM IMERG (NASA), mm/año. Mediana para no inflar con años de El Niño
    lluvia = (ee.ImageCollection("NASA/GPM_L3/IMERG_MONTHLY_V07").filterDate(INICIO, FIN)
              .select("precipitation").median().multiply(24 * 365).rename("lluvia"))

    # Vegetación: MODIS NDVI (NASA)
    ndvi = (ee.ImageCollection("MODIS/061/MOD13A3").filterDate(INICIO, FIN)
            .select("NDVI").mean().multiply(0.0001).rename("ndvi"))

    # Nieve: MODIS (NASA), porcentaje medio de cobertura de nieve (0-100)
    nieve = (ee.ImageCollection("MODIS/061/MOD10A1").filterDate(INICIO, FIN)
             .select("NDSI_Snow_Cover").mean().rename("nieve"))

    # Polvo: MERRA-2 (NASA), espesor óptico del polvo a 550 nm. Se usa un año para que el cálculo sea liviano
    polvo = (ee.ImageCollection("NASA/GSFC/MERRA/aer/2").filterDate("2022-01-01", "2023-01-01")
             .select("DUEXTTAU").mean().rename("polvo"))

    # Cobertura del suelo: MODIS, año fijo 2022. El año más reciente estaba incompleto
    # y su máscara borró todo el hemisferio oeste.
    cobertura = (ee.ImageCollection("MODIS/061/MCD12Q1").filterDate("2022-01-01", "2023-01-01")
                 .first().select("LC_Type1"))
    arido = cobertura.eq(16).rename("arido")    # 16 = terreno árido o desnudo
    hielo = cobertura.eq(15).rename("hielo")    # 15 = nieve y hielo permanentes
    tierra_firme = cobertura.neq(17)            # 17 = agua

    return (ee.Image.cat([elevacion, temp_dia, temp_noche, rango, lluvia, ndvi,
                          arido, nieve, hielo, permafrost, polvo])
            .toFloat().updateMask(tierra_firme))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--proyecto", required=True, help="ID del proyecto de Google Cloud con Earth Engine")
    parser.add_argument("--nombre", default="atlas_analog_global_025_v2")
    args = parser.parse_args()

    ee.Initialize(project=args.proyecto)
    tarea = ee.batch.Export.image.toDrive(
        image=capas_tierra(),
        description=args.nombre,
        folder=CARPETA_DRIVE,
        fileNamePrefix=args.nombre,
        region=ee.Geometry.Rectangle([-180, -90, 180, 90], None, False),
        crs="EPSG:4326",
        crsTransform=CUADRICULA,
        maxPixels=1e9,
    )
    tarea.start()
    print("Exportación lanzada:", args.nombre, "· id", tarea.id)
    print("Sigue su avance en la pestaña Tasks de code.earthengine.google.com")


if __name__ == "__main__":
    main()
