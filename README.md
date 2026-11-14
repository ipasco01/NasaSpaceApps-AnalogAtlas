# Atlas Analog · equipo Ctrl Z

> NASA Space Apps Piura 2026 · Reto: *Identify Earth Locations that Analog the Permanent Moon Base Locations and Mars*
> *There's no Ctrl+Z on Mars. Atlas Analog finds where to rehearse on Earth.*

Busca lugares de la Tierra parecidos a un sitio de la Luna o Marte, con datos de la NASA, y explica en qué se parecen y en qué fallan.

## Qué hay en esta carpeta

| Carpeta o archivo | Qué es | Quién lo usa |
|---|---|---|
| `ARQUITECTURA.md` | Plan técnico, reglas de las bases, calendario, roles | Todos |
| `CASOS_DE_USO.md` | Qué tiene que poder hacer cada persona en la app | Todos |
| `science/referencias.csv` | Valores de cada sitio de la Luna y Marte, con su fuente | Ciencia, motor |
| `science/analogos_conocidos.csv` | 17 análogos ya estudiados (para el modo descubrimiento) | Motor |
| `data-pipeline/earth_engine_tierra.js` | Exporta las capas de la Tierra desde el Code Editor de Google Earth Engine | Datos |
| `data-pipeline/tif_a_tabla.py` | Convierte el .tif exportado en tabla (`datos/celdas.parquet`) | Datos |
| `data-pipeline/planetas.py` | Pendiente de la Luna y Marte desde el relieve de MOLA y LOLA | Datos, ciencia |
| `data-pipeline/diviner.py` | Temperaturas de la Luna desde Diviner (baja solo las filas necesarias) | Datos, ciencia |
| `backend/motor.py` | Puntaje de parecido por celda, Top 10, modo descubrimiento y prueba de sensibilidad | Motor, backend |
| `datos/planetas/` | Relieve global de Marte (MOLA) y la Luna (LOLA) y recortes de Diviner, ya descargados | Todos |

## Estado al 14 de noviembre, 15:30

- **Luna y Marte:** listos. Jezero, Gale, Marius Hills y Shackleton (borde) con pendiente y temperaturas reales de la NASA.
- **Tierra:** lista en `datos/celdas.parquet` (334.741 celdas, todo el planeta) desde los archivos verificados de `datos/tierra/`. Faltan lluvia y polvo. Ver `datos/FUENTES.md`.
- **Motor:** funciona con la tabla de prueba; falta correrlo con la tabla real de la Tierra.

## Cómo correrlo

```bash
pip install pandas pyarrow numpy rasterio earthengine-api

# 1. Tierra: pegar data-pipeline/earth_engine_tierra.js en el Code Editor de Earth Engine, bajar los .tif y luego
python data-pipeline/tif_a_tabla.py datos/celdas.parquet datos/tierra/atlas_analog_arido_hielo_v10.tif datos/tierra/atlas_analog_ndvi_v11.tif datos/tierra/atlas_analog_temperatura_v6.tif datos/tierra/atlas_analog_nieve_v6.tif datos/tierra/atlas_analog_relieve_v6.tif

# 2. Luna y Marte (ya corrido; solo si cambian los sitios)
python data-pipeline/planetas.py
python data-pipeline/diviner.py

# 3. Top 10 para un sitio
python backend/motor.py --celdas datos/celdas.parquet --sitio gale --descubrimiento --sensibilidad
```

## Para backend: cómo arrancar ya

1. **Contrato:** `contrato/schema.json` define las columnas, las unidades y las 4 rutas de la API (`/api/referencias`, `/api/interpretar`, `/api/buscar`, `/api/celda`) con ejemplos de pedido y respuesta.
2. **Datos mientras llega la Tierra real:** usen `datos/celdas_PRUEBA_no_reales.parquet`. Tiene las mismas columnas que la tabla real, pero **los valores son inventados**: sirve para programar, nunca para la demo. Cuando esté `datos/celdas.parquet`, solo cambia la ruta.
3. **El motor ya está hecho** (`backend/motor.py`). La API solo tiene que llamarlo:
   - `cargar_referencia(sitio)` devuelve la fila de `science/referencias.csv`.
   - `puntuar(celdas, ref, pesos, imprescindibles)` devuelve una tabla con `lat`, `lon`, `puntaje` y una columna `s_<variable>` por variable (el desglose de 0 a 1), más la lista de variables donde «la Tierra no llega».
   - `lejos_de_conocidos(salida)` es el filtro del modo descubrimiento.
   - `sensibilidad(celdas, ref, pesos)` dice qué parte del Top 10 se mantiene al mover cada peso ±20 %.
   - `PESOS_BASE["marte"]` y `PESOS_BASE["luna"]` son los pesos de partida.
4. **Cargar `celdas` una sola vez** al iniciar el servidor (FastAPI `lifespan`), no en cada pedido.
5. **Para la IA** (`/api/interpretar`): usar salidas estructuradas (`client.messages.parse`) y la clave solo en `.env`.

Probar el motor desde la terminal:

```bash
cd backend
python motor.py --celdas ../datos/celdas_PRUEBA_no_reales.parquet --sitio jezero --top 5 --descubrimiento --sensibilidad
```

## Columnas (no cambiar los nombres sin avisar a todo el equipo)

`elevacion, pendiente, temp_dia, temp_noche, rango_termico, lluvia, ndvi, arido, nieve, hielo, permafrost_proxy, polvo`, más `lat` y `lon`. Temperaturas en °C, pendiente en grados, lluvia en mm/año.

## Reglas

- Las claves (Claude, Earth Engine) van solo en un archivo `.env` que **nunca** se sube ni se comparte por chat.
- Cada dato nuevo lleva su fuente en `science/referencias.csv` o en `ARQUITECTURA.md`.
- No inventar valores: si no hay fuente, la celda queda vacía y el motor la ignora.
