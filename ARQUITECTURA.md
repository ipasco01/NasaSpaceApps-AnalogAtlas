# Atlas Analog · Arquitectura (NASA Space Apps 2026, equipo Ctrl Z)

> v0.2 · 2026-11-11 · Isabelita
> Reto: *Identify Earth Locations that Analog the Permanent Moon Base Locations and Mars*
> Equipo: 6 personas · Tiempo: 2 días · NASA Space Apps Piura, 14 y 15 de noviembre de 2026, Universidad de Piura

## 0. Lo que dicen las bases de Piura y cómo cambian el plan

| Regla | Qué hacemos |
|---|---|
| **El proyecto se desarrolla durante la hackathon** | Antes del sábado **no se programa**. Se preparan cuentas, herramientas instaladas, este plan y la lista de datos. El prototipo de pantalla sirve **solo como referencia visual**; el código se escribe desde cero el sábado. |
| **No hay pitch ante el jurado:** evalúa solo lo que se envía | La "demo" es **7 diapositivas o un video de 30 s, en inglés**. Se planifica desde el sábado, no al final. |
| **Todo se entrega en inglés** en la pestaña Project | Resumen, detalles, uso de IA y datos NASA, referencias. Una persona se encarga de esto. |
| **Debe usar al menos un dato de la NASA, explicado** (cuál, qué variables, cómo ayudó, enlace) | Núcleo NASA: MODIS (temperatura, vegetación, polvo), SRTM (relieve), GPM (lluvia), LRO y Viking/MOLA (Luna y Marte). Sentinel-2 (EOX) queda solo para las imágenes del comparador. |
| **La IA está permitida, pero hay que declararla** | Declarar Claude dos veces: dentro del producto (traduce texto a criterios) y como ayuda para escribir código y textos. |
| **Enlace público que funcione** (GitHub o Drive) | Repo público. Por eso las claves van solo en `.env`, nunca en el repo (sección 8). |
| **Cierre: domingo 15, 23:59 hora Perú.** Después no se puede cambiar ni el repo | Se puede enviar varias veces: **primer Submit el domingo a mediodía** y luego se actualiza. |
| Jurado: Impacto, Creatividad, **Validez**, Relevancia, Presentación | Validez = el motor explicable, la validación con análogos conocidos y el bloque "en qué falla". Creatividad = modo descubrimiento y comparador. |

## 1. La idea en una frase

La persona escribe qué quiere investigar ("quiero probar un rover en terreno frío, seco y con polvo como en Marte").
La IA lo convierte en criterios con números. Un algoritmo compara esos criterios con una **cuadrícula de toda la Tierra ya calculada de antemano**
y el mapa muestra los mejores lugares, **en qué se parecen y en qué no**.

## 2. La decisión que lo hace posible en 2 días

**No procesamos imágenes satelitales en vivo.** El sábado en la mañana un script divide la Tierra en celdas hexagonales (H3, resolución 4, ≈1.770 km² cada una, ≈85.000 celdas de tierra firme)
y a cada celda le guarda un puñado de números: altura, pendiente, temperatura, lluvia, vegetación, tipo de roca, polvo, hielo.
Queda un solo archivo (`celdas.parquet`, unos MB). Buscar después es una cuenta rápida en memoria, sin esperas.

Luna y Marte **no se procesan como mapas**: se arma a mano una tabla de 8–12 sitios de referencia (Shackleton, Marius Hills, Jezero, Gale, Utopia Planitia, tubos de lava de Arsia…)
con sus valores sacados de LRO, MOLA, THEMIS y artículos, cada uno con su fuente.

## 3. Piezas

```
 ┌──────────────── Navegador ────────────────┐
 │ React + Vite + MapLibre + deck.gl (H3)    │
 │ caja de texto · mapa de calor · ficha     │
 └──────────────┬────────────────────────────┘
                │ JSON
 ┌──────────────▼────────────────────────────┐
 │ API  FastAPI (Python)                     │
 │  /interpretar  → IA: texto → criterios    │
 │  /buscar       → motor de similitud       │
 │  /celda/{id}   → detalle + explicación    │
 └───┬───────────────────────┬───────────────┘
     │                       │
 ┌───▼──────────┐   ┌────────▼─────────────────┐
 │ API de Claude│   │ datos/ (solo lectura)    │
 │ (tool use →  │   │  celdas.parquet          │
 │  JSON fijo)  │   │  referencias_luna_marte  │
 └──────────────┘   │  analogos_conocidos.csv  │
                    └────────▲─────────────────┘
                             │ se genera 1 vez
                 ┌───────────┴──────────────┐
                 │ pipeline/ (scripts)      │
                 │ Google Earth Engine o    │
                 │ GeoTIFF → promedio x celda│
                 └──────────────────────────┘
```

### 3.1 Datos de la Tierra (una columna por dimensión)

| Dimensión del reto | Dato | De dónde |
|---|---|---|
| Terreno, pendiente, rugosidad | Altura + pendiente + desviación | SRTM / Copernicus DEM 90 m |
| Temperatura extrema | Temperatura de superficie día y noche, rango | MODIS LST (MOD11C3) |
| Aridez | Lluvia anual | GPM IMERG o CHIRPS |
| Vida / vegetación | NDVI promedio | MODIS NDVI (MOD13C2) |
| Geología | Tipo de roca (basalto, sedimentaria, evaporitas…) | GLiM (mapa litológico global) |
| Polvo y viento | Profundidad óptica de aerosoles, viento | MODIS AOD, MERRA-2 / ERA5 |
| Hielo, permafrost | Fracción de permafrost / glaciar | ESA CCI Permafrost, GLIMS |
| Cráteres, cuevas | Distancia al cráter / tubo de lava conocido | Earth Impact Database, listas abiertas |

Mínimo para la demo: **las 5 primeras**. Lo demás se suma si da el tiempo.

**Camino rápido:** Google Earth Engine tiene casi todo esto. Un script por dimensión saca el promedio por celda y exporta un CSV. **Pedir la cuenta de Earth Engine y de NASA Earthdata antes del sábado.**
Plan B si Earth Engine falla: WorldClim (clima) + ETOPO (altura) bajados como GeoTIFF y promediados con `rasterio`.

### 3.2 Motor de similitud (el corazón, y lo que más valora el jurado)

1. Cada columna se pasa a **percentil 0–1 dentro de la Tierra**. Así no importa que Marte esté a −60 °C y ningún lugar de la Tierra llegue: "lo más frío de la Tierra" = percentil 0.
2. Cada criterio dice qué buscar: `minimo`, `maximo` o `objetivo` (un valor).
3. Puntaje por dimensión = qué tan cerca está la celda de eso (0–1).
4. Puntaje final = promedio ponderado con los pesos que dio la IA.
5. Se devuelve **el desglose**: "parecido en aridez 0,94 y en roca 0,90; falla en temperatura 0,35".
6. **Modo descubrimiento** (opcional): baja el puntaje de celdas a menos de X km de análogos ya famosos (Atacama, Haughton, Valle de la Muerte, Islandia, Hawái, Antártida). El reto pide lugares nuevos.
7. Siempre se muestra lo que la Tierra **no** puede imitar: gravedad, vacío, atmósfera delgada, radiación.

Es numpy puro, sin aprendizaje automático. Es explicable y se puede validar: si Atacama no sale arriba para "Marte seco", algo está mal.

### 3.3 La IA (solo traduce y explica, no inventa lugares)

- `/interpretar`: Claude recibe el texto + la lista de dimensiones disponibles + los sitios de referencia, y responde **solo** con un JSON con este formato.
  **Ojo (revisado el 2026-11-11):** los modelos actuales rechazan el "tool use forzado" (`tool_choice` de tipo `any` o `tool` da error 400). Usar **salidas estructuradas**: `client.messages.parse(..., output_format=ModeloPydantic)` en el SDK de Python, que devuelve el JSON ya validado.

```json
{
  "cuerpo": "marte",
  "sitio_referencia": "jezero",
  "criterios": {
    "lluvia_anual":      {"modo": "minimo", "peso": 0.3},
    "ndvi":              {"modo": "minimo", "peso": 0.2},
    "roca":              {"modo": "igual", "valor": "basalto", "peso": 0.2},
    "temp_rango_diario": {"modo": "maximo", "peso": 0.2},
    "pendiente_grados":  {"modo": "objetivo", "valor": 5, "peso": 0.1}
  },
  "modo_descubrimiento": true,
  "resumen": "Buscas un terreno basáltico, muy seco y sin vegetación, con cambios fuertes de temperatura."
}
```

- La persona puede **mover los pesos a mano** después; la IA solo propone el punto de partida.
- Explicación de cada lugar: un texto corto armado con el desglose numérico (la IA redacta, los números salen del motor).
- Modelo: `claude-opus-5-5` con esfuerzo bajo (`output_config={"effort": "low"}`), porque la tarea es corta. Si hay que ahorrar, `claude-sonnet-5-5`. Revisar siempre `stop_reason` antes de leer la respuesta.
- Si la IA falla o no hay clave: el selector "Comparar con" carga los criterios del sitio de referencia sin IA (CU-05). La demo nunca depende solo de la IA.

### 3.4 Pantalla (una sola)

- Izquierda: caja de texto, criterios con pesos editables y la lista del top 10.
- Centro: mapa del mundo con hexágonos coloreados por puntaje.
- Clic en un lugar → ficha: **comparador de imágenes** (Tierra y Marte/Luna con una barra que se arrastra), puntaje por dimensión (barras), "se parece en / no se parece en", sitio de Luna/Marte comparado y para qué serviría (probar rovers, buscar biofirmas, construir…).
- Prototipo aprobado (2026-11-11): https://claude.ai/artifact/TFWYU49VJLWwkoMzt9ENPW. Es la referencia visual para programar el sábado.

**Requisitos aprobados para la versión en React:**
1. **Rigor científico visible:** el bloque "En qué se parece / En qué falla (límites como análogo)" pesa **lo mismo** visualmente que el comparador de imágenes. Siempre incluye lo que la Tierra no imita: gravedad, radiación, atmósfera o vacío.
2. **Botones "Copiar ficha científica" y "Exportar JSON"** en la ficha. Cierran el caso de uso de quien investiga.
3. **Las dos imágenes del comparador al mismo ancho real** (Marte 120 km, Luna 60 km) y con barra de escala. Si no se conoce la escala, se dice.
4. **Movimiento:** el Top 10 se reordena animado al mover pesos o el interruptor (`layout` de Framer Motion, 200 ms, ease-in-out). Al elegir un lugar en el mapa o en la lista se marcan los dos con un pulso suave, y la ficha entra en 200 ms con ease-out y se puede interrumpir.
5. **Cifras:** `tabular-nums` en todos los puntajes y porcentajes. Botones de 44 px como mínimo. Espacios en múltiplos de 4.

### 3.5 Imágenes para comparar (probadas el 2026-11-11, sin clave)

| Qué | Fuente | Cómo se pide |
|---|---|---|
| Tierra, color real sin nubes | Sentinel-2 cloudless 2021 (EOX, licencia CC BY-NC-SA, citar "Contains modified Copernicus Sentinel data") | WMS `tiles.maps.eox.at/wms`, capa `s2cloudless-2021`, con un recuadro en grados |
| Tierra, opción NASA | NASA GIBS (MODIS, Blue Marble) | `wvs.earthdata.nasa.gov/api/v1/snapshot`. Se ve borrosa a menos de 100 km |
| Marte | Viking MDIM 2.1 en NASA Mars Trek | Teselas `trek.nasa.gov/tiles/Mars/EQ/Mars_Viking_MDIM21_ClrMosaic_global_232m/...` (zoom máximo 7) |
| Luna | LRO WAC en NASA Moon Trek | Teselas `trek.nasa.gov/tiles/Moon/EQ/LRO_WAC_Mosaic_Global_303ppd_v02/...` |
| Polos (Antártida, polo sur lunar) | Las anteriores fallan o deforman: usar imágenes fijas de NASA/USGS de dominio público | Archivo guardado en `datos/imagenes/` |

Para la demo basta con **descargarlas una vez** y guardarlas como archivos. No hace falta pedirlas en vivo.

## 4. Contrato entre equipos (se fija en la primera hora y no se cambia)

Se escribe el sábado en `contrato/schema.json` (fuente única; el frontend copia los tipos en `tipos.ts` desde ahí).

1. **Nombres de columnas y unidades** de `celdas.parquet`: `h3, lat, lon, altura_m, pendiente_grados, rugosidad_m, temp_dia_c, temp_noche_c, temp_rango_diario, lluvia_anual, ndvi, roca, aod, permafrost`.
2. **JSON de criterios** (el de arriba).
3. **Respuesta de `/buscar`:** `[{h3, lat, lon, puntaje, desglose:{dimension: 0..1}}]` (top 200 para el mapa).

Con eso cada quien trabaja con **datos falsos** desde la hora 1 y se conecta al final.

## 5. Quién hace qué (6 personas)

| # | Rol | Entrega |
|---|---|---|
| 1 | Datos Tierra A | Altura, pendiente, rugosidad, temperatura en la cuadrícula |
| 2 | Datos Tierra B | Lluvia, NDVI, roca, polvo, permafrost. Une todo en `celdas.parquet` |
| 3 | Ciencia Luna/Marte + validación | Tabla de sitios de referencia con fuentes. Revisa que salgan bien los análogos conocidos. Elige los 2–3 "descubrimientos" |
| 4 | Motor + API | Percentiles, puntaje, desglose, modo descubrimiento, FastAPI |
| 5 | IA + explicaciones | Prompt, salidas estructuradas, `/interpretar`, texto de la ficha |
| 6 | Pantalla + entrega | Mapa, ficha y despliegue el sábado. Desde el domingo a mediodía: demo en inglés (7 diapositivas o video de 30 s) y textos de la pestaña Project |

La persona 3 (ciencia) escribe además, en inglés, la parte "NASA Data" de la entrega: cada dato con sus variables, cómo se usó y el enlace.

## 6. Calendario

**Día 1 (sábado 14, desde las 9:00)**
- 9:00–10:00: todos juntos. Crear el repo público, fijar el contrato (`contrato/schema.json`) y los datos falsos.
- 10:00–18:00: cada quien en su pieza con datos falsos.
- Fin del día: `celdas.parquet` real con al menos 5 columnas · motor responde · mapa pinta hexágonos · IA devuelve el JSON · guion de la demo escrito.

**Día 2 (domingo 15)**
- Mañana: unir todo. Validar: "Marte seco" debe sacar Atacama y el Valle de la Muerte arriba; "polo lunar frío" debe sacar zonas polares.
- 12:00: con el modo descubrimiento, escoger 2–3 lugares nuevos y escribir por qué sirven y dónde falla la analogía. **Primer Submit** con lo que haya.
- **18:00: se congela el código.** Solo arreglos, capturas, demo en inglés, textos y despliegue.
- 22:00: Submit final y checklist de las bases (sección 9). **Margen hasta las 23:59.**

## 7. Estructura del repo (se crea el sábado)

```
nasa/
├─ README.md          # en inglés: qué es, cómo correrlo, datos NASA, uso de IA, referencias
├─ contrato/          # schema.json: columnas, unidades y formato de la API (fuente única)
├─ data-pipeline/     # scripts que generan datos/ (personas 1 y 2)
├─ science/           # referencias_luna_marte.json, analogos_conocidos.csv, FUENTES.md (persona 3)
├─ backend/           # FastAPI: motor, IA, rutas (personas 4 y 5)
├─ frontend/          # React + Vite + Framer Motion (persona 6)
├─ datos/             # celdas.parquet, imagenes/ (salida del pipeline)
├─ .env.example       # ANTHROPIC_API_KEY=   (vacío)
└─ .gitignore         # .env, datos crudos pesados, node_modules
```

El mapa del prototipo es un SVG propio (sin servicios externos). MapLibre + deck.gl solo si sobra tiempo.

Despliegue: front en Vercel, API en Render o Railway. Plan B para la demo: todo corriendo en una laptop.

## 8. Seguridad

- La clave de Claude y la de Earth Engine **solo en `.env`** (fuera del repo) y en las variables del servicio donde se despliegue. Nunca en el código, el chat del equipo ni en commits.
- Una sola clave de API con límite de gasto para el evento. Se borra al terminar.
- No se guardan datos de las personas que usan la página; los textos que escriben no se almacenan.
- Cada dato usado lleva su fuente y licencia en `datos/FUENTES.md` (también suma puntos con el jurado).

## 9. Antes del sábado (sin programar)

- [ ] **Los 6 registrados** en spaceappschallenge.org, en el evento de Piura, en la pestaña Members del equipo y **nadie en lista de espera**.
- [ ] Equipo inscrito en el reto *Permanent Moon Base Locations and Mars*.
- [ ] Cuentas: GitHub (las 6), Google Earth Engine, NASA Earthdata, clave de Claude con límite de gasto (la guarda una sola persona).
- [ ] Software instalado en cada laptop: Node 20+, Python 3.11+, Git, editor. Las personas 1 y 2 también: `earthengine-api` o `rasterio`.
- [ ] Persona 3: leer la pestaña **Resources** del reto y anotar qué datos NASA propone. Hacer la lista de sitios de referencia (Jezero, Gale, Shackleton, Marius Hills…) con sus fuentes.
- [ ] Persona 6: preparar la estructura vacía de las 7 diapositivas en inglés (portada, problema, reto, datos NASA, solución, cómo funciona, demo, impacto).
- [ ] Todos: leer este documento, `CASOS_DE_USO.md` y mirar el prototipo.
- [ ] Laptops, cargadores y audífonos.

**En la entrega (domingo), según el checklist de las bases:** reto oficial · todos en Piura · datos NASA explicados · resumen y detalles · demo lista · todo en inglés · enlace público que funciona · IA y referencias declaradas · Submit registrado.

## 10. Lo que NO hacemos (para llegar)

Usuarios y login, base de datos, aprendizaje automático entrenado, procesar mapas de Luna/Marte en vivo, más de una pantalla.
