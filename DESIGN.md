# Analog Atlas · DESIGN.md
v1.0 · 2026-11-14 · Isabelita (equipo Ctrl Z)

Fuente única de tokens del frontend (React). Solo tokens y su razón en una línea. Nada visible se programa sin
aprobación previa en un artifact con antes y después.

Design Read: app científica para encontrar análogos terrestres de la Luna y Marte, para estudiantes, investigadores
y equipos de prueba de misiones, con estilo de instrumento de datos. Dial: ENERGY 2 / RHYTHM 2 / MOTION 1.

## Tipografía
| Token | Valor | Razón |
|---|---|---|
| font-sans | "IBM Plex Sans", system-ui, sans-serif | Elegida por Isabel: tono técnico y científico, números claros en puntajes y tablas |
| font-mono | "IBM Plex Mono", ui-monospace, monospace | Solo coordenadas y lecturas de instrumento (motivo de identidad), nunca títulos |
| weights | 400 texto · 500 etiquetas · 600 títulos y botones · 700 puntaje | Cuatro pesos bastan para la jerarquía |
| numeric | font-variant-numeric: tabular-nums | Columnas de números alineadas |

Escala (px / interlineado): 12/16 · 14/20 · 16/24 · 20/28 · 24/32 · 32/40 · 48/48 (solo el puntaje del lugar).

## Color
| Token | Claro (por defecto) | Oscuro | Razón |
|---|---|---|---|
| bg | #FFFFFF | #0B0F17 | Fondo limpio; los mockups del equipo son claros |
| surface-2 | #F5F5F7 | #131A26 | Paneles secundarios (filtros), sin sombra |
| ink | #111827 | #F8FAFC | Texto principal, contraste AAA |
| muted | #4B5563 | #94A3B8 | Texto secundario, contraste ≥ 4.5:1 |
| line | #E5E7EB | #233044 | Bordes de 1 px que reemplazan a las sombras |
| accent | #5B4CDB | #A29BFE | Único acento (mockups del equipo): botón principal, paso activo, puntos del mapa |
| accent-hover | #4A3CC4 | #B8B2FF | Hover del botón principal |
| accent-ink | #FFFFFF | #0B0F17 | Texto sobre el acento |
| accent-soft | #EEECFC | #221F45 | Fondo de elemento seleccionado |
| good | #15803D | #4ADE80 | Solo "coincide" en la ficha del lugar |
| bad | #B91C1C | #F87171 | Solo "rompe la analogía" y errores |

## Espaciado (base 4)
4 · 8 · 12 · 16 · 24 · 32 · 48 · 64. Dentro de un componente 8 a 16; entre bloques 24 a 32; entre secciones 48.

## Layout
| Token | Valor | Razón |
|---|---|---|
| content-max | 1200 px, centrado | Todo el contenido alineado al mismo eje |
| gutter | 24 px (16 px bajo 640 px) | Margen lateral constante |
| header-h | 64 px | Logo, pasos y modo en una línea |
| breakpoints | 640 · 1024 px | Teléfono, tableta, escritorio |

## Forma y elevación
| Token | Valor | Razón |
|---|---|---|
| radius-sm | 6 px | Botones, campos, chips |
| radius-md | 12 px | Tarjetas, mapa, imágenes |
| radius-full | 999 px | Solo el buscador de la portada (pedido de Isabel, estilo buscador) |
| border | 1 px solid line | Separa superficies sin sombras |
| shadow-overlay | 0 12px 32px rgba(17,24,39,.16) | Solo lo que flota sobre otra capa: modal y tarjeta emergente del mapa |

## Botones (un solo sistema)
| Variante | Estilo | Uso |
|---|---|---|
| primary | fondo accent, texto accent-ink | Una acción principal por pantalla |
| secondary | fondo bg, borde line, texto ink | Acciones alternativas |
| ghost | sin fondo ni borde, texto accent | Volver, saltar, enlaces de acción |
Alto 44 px (56 px solo el buscador), padding 0 16, radius-sm, 14 px peso 600. Foco: anillo 2 px accent con 2 px de separación.
Presionado: escala 0.98. Deshabilitado: opacidad 0.5 y cursor no permitido.

## Movimiento (MOTION 1)
Transiciones de 150 ms cubic-bezier(.2,.7,.3,1) en hover, foco y presionado. Única excepción con propósito: los globos 3D giran despacio para mostrar que se pueden girar; se detienen al tocarlos y no giran con prefers-reduced-motion.
Con prefers-reduced-motion: ninguna.

## Navegación
Pasos numerados en la cabecera: 1 Search · 2 Compare (globos 3D) · 3 Explore · 4 Place (con "View as" por rol). Paso activo en accent; los pasos ya
recorridos se pueden tocar para volver; los futuros no.
