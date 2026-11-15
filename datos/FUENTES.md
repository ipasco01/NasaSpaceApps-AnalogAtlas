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

| `atlas_analog_polvo_v12.tif` | polvo (profundidad óptica del polvo a 550 nm) | `NASA/GSFC/MERRA/aer/2` banda `DUEXTTAU`, media 2022 | 331.835 celdas (99,1 %); p5 0,002, mediana 0,016, p95 0,231, máx 0,579 (Taklamakán 0,51, Bodélé 0,47, Sechura 0,05). Agregada con `data-pipeline/agregar_columna.py` |

**Roca de la superficie (no NASA):** GLiM, Hartmann & Moosdorf 2012, grilla de 0,5° (PANGAEA doi:10.1594/PANGAEA.788537, CC BY 3.0, archivo `hartmann-moosdorf_2012.zip` de 38 kB). `data-pipeline/glim_a_columnas.py` crea `volcanico` (clases vb, vi, py: basaltos, andesitas, piroclastos; 4,8 % de las celdas) y `sedimento` (su, ss, sm; 44 %). 98,7 % de las celdas con dato. Comprobado: Deccan e Islandia vb, valle de Andagua (Arequipa) vi y py, Sechura su.

**Sales y carbonatos (GLiM):** `evaporita` (clase ev, 635 celdas: Salar de Uyuni, salares de Atacama, Chott el Djerid) y `carbonato` (clase sc, 18.668 celdas: Yucatán, Nullarbor, Guilin, Alpes calizos), agregadas el 2026-11-15 con `data-pipeline/glim_a_columnas.py` v0.2. Solo filtran, no entran al puntaje. Ojo: GLiM pone Dallol, Qaidam, Makgadikgadi, Death Valley y el lago Eyre como sedimento, no como sal.

**Tubos de lava:** `science/tubos_lava.csv`, 6 tubos con coordenadas y fuente; solo se muestran en el mapa.

**Lluvia:** `lluvia` de `NASA/GPM_L3/IMERG_MONTHLY_V07` (mediana mensual 2018-2023 × 24 × 365, mm/año), archivo `atlas_analog_lluvia_gpm_v9.tif`, agregada el 2026-11-15 con `data-pipeline/agregar_columna.py`. 334.741 celdas (100 %); p5 0, mediana 219, p95 1.682. Comprobado: Amazonas 2.342, Londres 784, Atacama 26, Sahara 0. Ojo: el 29 % de las celdas da 0, incluida la Antártida (posible falta de dato cerca del polo).

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
