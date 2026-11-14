# Atlas Analog · Casos de uso (equipo Ctrl Z)

> v0.1 · 2026-11-11 · Isabelita
> Va con `ARQUITECTURA.md`. Prioridad: **Demo** = tiene que estar para el domingo · **Extra** = solo si sobra tiempo.

## Quiénes la usan

| Persona | Qué necesita |
|---|---|
| Investigadora científica | Encontrar un lugar en la Tierra para estudiar un proceso de Marte o la Luna (polvo, hielo, biofirmas) |
| Ingeniero de pruebas | Un terreno para probar un rover, un taladro o un hábitat antes de mandarlo |
| Docente o estudiante | Entender por qué un lugar se parece a Marte, sin saber de sensores ni datos |
| Planificador de misión (agencia) | Comparar candidatos y saber dónde falla cada uno |
| Equipo (interno) | Comprobar que el motor da resultados con sentido antes de la demo |

## Casos

### CU-01 · Describir la investigación con palabras — Demo
- **Quién:** cualquiera.
- **Pasos:** escribe su objetivo ("quiero probar un taladro en suelo basáltico, seco y con mucho polvo, como en Jezero") → toca **Buscar lugares** → la IA devuelve un resumen de lo que entendió, el sitio de Luna o Marte de referencia y los criterios con su peso.
- **Si falla:** si el texto es muy corto o ambiguo, la página dice qué falta y muestra un ejemplo. Si la IA no responde, se puede elegir un sitio de referencia a mano (CU-05).
- **Resultado:** criterios listos y lugares en el mapa.

### CU-02 · Ver los mejores lugares en el mapa — Demo
- **Pasos:** el mapa pinta las zonas según su puntaje y la lista muestra los 10 mejores con su puntaje (0–100).
- **Si no hay resultados:** estado vacío con un icono, una frase y un botón para aflojar los criterios.

### CU-03 · Ver la ficha de un lugar — Demo
- **Pasos:** toca un lugar de la lista o del mapa → se abre la ficha.
- **La ficha muestra:** nombre y coordenadas, puntaje total, una barra por cada dimensión, **en qué se parece**, **en qué no**, lo que ningún lugar de la Tierra imita (gravedad, vacío, atmósfera delgada, radiación) y **para qué serviría** (probar equipos, buscar señales de vida, entrenar personas).
- **Es el caso central:** el reto pide explicar por qué un lugar es análogo y dónde deja de serlo.

### CU-04 · Ajustar los criterios a mano — Demo
- **Pasos:** mueve el peso de una dimensión (por ejemplo, sube "polvo") → la lista y el mapa se reordenan al instante, sin volver a llamar a la IA.
- **Para qué:** la persona experta corrige a la IA y la principiante aprende qué pesa cada cosa.

### CU-05 · Elegir un sitio de referencia de la Luna o Marte — Demo
- **Pasos:** elige de una lista (Shackleton, Marius Hills, Jezero, Gale, Utopia Planitia…) → se cargan los criterios de ese sitio sin escribir nada.
- **Para qué:** sirve como respaldo si la IA falla y como camino rápido en la demo.

### CU-06 · Modo descubrimiento — Demo
- **Pasos:** activa "Ocultar análogos conocidos" → desaparecen Atacama, Valle de la Muerte, Haughton, Islandia, Hawái y la Antártida, y suben lugares poco estudiados.
- **Para qué:** el reto pide no repetir los lugares de siempre. Es el momento sorpresa de la demo.

### CU-07 · Validar el motor — Demo (interno)
- **Quién:** la persona de ciencia del equipo.
- **Pasos:** corre 3 búsquedas fijas ("Marte seco", "polo lunar frío", "tubos de lava") y revisa que los análogos conocidos salgan arriba **con el modo descubrimiento apagado**.
- **Resultado:** si no salen, se revisan los datos o las fórmulas antes de seguir.

### CU-08 · Comparar 2 o 3 lugares lado a lado — Extra
- **Pasos:** marca lugares → tabla con las barras de cada dimensión una junto a otra.

### CU-09 · Compartir el resultado — Extra
- **Pasos:** botón **Copiar enlace** que guarda los criterios en la dirección, o **Copiar tabla** para pegarla en un documento.

## Fuera de alcance (hackathon)

Cuentas y login, guardar búsquedas, subir datos propios, procesar mapas de Luna o Marte en vivo.

## Seguridad

- Los textos que escribe la persona solo se mandan a la IA para interpretarlos. No se guardan.
- La página no pide datos personales.
- La clave de la IA vive en el servidor, nunca en la página.
