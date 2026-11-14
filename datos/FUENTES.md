# Datos verificados · Analog Atlas (equipo Ctrl Z)

> Revisado el 2026-11-14. Cada archivo: de dónde sale, cómo se generó y qué se comprobó.

## Tierra (`datos/tierra/`, cuadrícula EPSG:4326 de 0,25°, 1441 × 721)

Exportados desde Google Earth Engine con `data-pipeline/earth_engine_tierra.js`. Máscara de tierra firme: MODIS MCD12C1 2022 (clase 0 = agua).

| Archivo | Columnas | Dataset (catálogo Earth Engine) | Comprobado |
|---|---|---|---|
| `atlas_analog_temperatura_v6.tif` | temp_dia, temp_noche, rango_termico, permafrost_proxy | `MODIS/061/MYD11A2` (Aqua, 13:30 y 01:30), media 2018-2023, escala 0,02 K | 334.434 celdas; ambos hemisferios; 89,4° S a 83,4° N; día −60 a 57 °C |
| `atlas_analog_nieve_v6.tif` | nieve (% 0-100) | `MODIS/061/MOD10A1`, media 2018-2023 | 334.615 celdas; 0 a 80 % |
| `atlas_analog_relieve_v6.tif` | elevacion (m) | `NOAA/NGDC/ETOPO1` `ice_surface` | 334.741 celdas; valores < −450 m (fondo marino en costas) se descartan en `tif_a_tabla.py` |
| `atlas_analog_ndvi_v11.tif` | ndvi | `MODIS/061/MOD13A3`, media 2018-2023, escala 0,0001 | 240.690 celdas; −0,19 a 0,90. **No cubre la Antártida** (MODIS no calcula NDVI sobre hielo) |
| `atlas_analog_arido_hielo_v10.tif` | arido, hielo (fracción 0-1 de la celda) | `MODIS/061/MCD12C1` 2022, clases IGBP 16 (árido) y 15 (nieve/hielo permanente) | 334.741 celdas; es la máscara de tierra firme |

**Pendiente:** se calcula en `tif_a_tabla.py` desde la elevación, con la misma fórmula que para la Luna y Marte (sobre 80° de latitud, solo la componente norte-sur).

**Faltan:** `lluvia` (`NASA/GPM_L3/IMERG_MONTHLY_V07`, exportada como `atlas_analog_lluvia_gpm_v9.tif`, por bajar de Drive) y `polvo` (`NASA/GSFC/MERRA/aer/2`, en exportación v12).

**Error de exportación conocido:** las capas en cuadrícula lat/lon de 0,1° y 0,05° (GPM, MOD13C1, ERA5, MCD12C1 como banda) fallaban con `Unable to transform edge`. Se resolvió llevándolas a la proyección sinusoidal de MODIS (5 km) antes de exportar. Detalle en `data-pipeline/earth_engine_tierra.js`.

## Tabla unida (`datos/celdas.parquet`)

`python data-pipeline/tif_a_tabla.py datos/celdas.parquet datos/tierra/atlas_analog_arido_hielo_v10.tif datos/tierra/atlas_analog_ndvi_v11.tif datos/tierra/atlas_analog_temperatura_v6.tif datos/tierra/atlas_analog_nieve_v6.tif datos/tierra/atlas_analog_relieve_v6.tif`

334.741 celdas de tierra firme (92.410 al sur de 60° S). En 92.002 celdas de hielo permanente sin NDVI se pone ndvi = 0 (columna `ndvi_relleno` = True). Pasa el chequeo de cobertura (hemisferio oeste y latitudes altas).

## Luna y Marte (`datos/planetas/`)

| Archivo | Qué es | Fuente | Comprobado |
|---|---|---|---|
| `megt90n000cb.img` + `.lbl` | Relieve global de Marte, 4 px/° | MOLA MEGDR, PDS Geosciences Node | Monte Olimpo 20.009 m, Hellas −6.151 m |
| `ldem_4.img` + `.lbl` | Relieve global de la Luna, 4 px/° | LOLA LDEM_4, PDS Geosciences Node | Escala 0,5 m y radio 1737,4 km según la etiqueta |
| `diviner/marius_96h.tab` | 96 horas locales de temperatura en Marius Hills (celda 0,5°) | Diviner GCP `global_cumul_avg_cyl_10n20n_002`, bajado por rango de bytes | Máx 392 K y mín 96,7 K; coincide con Williams et al. 2017 (387-397 K y ~95 K) |
| `diviner/shackleton_zona.tab` | Recorte de 6.050 filas alrededor de Shackleton | Diviner PRP `dlre_prp_south.tab` | Borde: máx 265 K, media 130 K; fondo: máx 86 K. Centro del cráter según Gazetteer IAU/USGS Feature 5450 |

Los valores por sitio, con su fuente, están en `science/referencias.csv`.
