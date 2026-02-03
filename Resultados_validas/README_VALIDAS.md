# Resultados de Válidas — Guía de creación

Este documento explica cómo crear páginas de resultados para nuevas válidas de motocross (u otras disciplinas). Sirve como guía para desarrolladores y como base para prompts de IA.

**Proyecto de uso interno de FEDEMOTO.**  
*Developed by Mauricio Sánchez Aguilar - Fedemoto*

---

## Elementos obligatorios en todas las páginas de válidas

Todas las páginas generadas **deben incluir**:

1. **Menú de navegación** — Cargado dinámicamente con `load-menu.js` y el contenedor `<div id="menu-container"></div>`. El menú se inyecta desde `menu.html` en la raíz del proyecto.

2. **Footer** — Al final de la página, con el siguiente contenido:
   - *Developed by Mauricio Sánchez Aguilar - Fedemoto*
   - *Este proyecto es de uso interno de FEDEMOTO.*

**Nota sobre el menú:** Si el menú no carga, asegúrate de abrir la página **a través de un servidor web local** (Live Server en VS Code, `python -m http.server 8000`, etc.). Abrir el archivo HTML directamente con `file://` puede bloquear la carga del menú por restricciones de CORS del navegador.

---

## Estructura existente (ejemplo: I Válida MX Girardota)

```
Resultados_validas/
└── Motocross/
    └── Primer semestre/
        ├── FILES EXPORTED/          ← Carpeta con los CSV exportados
        │   ├── 50cc - CLASIFICATORIA - Resultados.csv
        │   ├── 65cc - CARRERA CLASIFICACION - Resultados.csv
        │   ├── 65cc - 1 CARRERA - Resultados.csv
        │   ├── 65cc - FINAL - Resultados.csv
        │   ├── 125cc - CARRERA CLASIFICATORIA - Resultados.csv
        │   ├── 125cc - 1 CARRERA - Resultados.csv
        │   ├── 125cc - 2 CARRERA - Resultados.csv
        │   ├── 125cc - final - resultados.csv
        │   └── ... (más categorías)
        ├── generar_valida_girardota.py   ← Script que genera el HTML
        └── valida_i_mx_girardota.html   ← Página generada
```

---

## Pasos para crear una nueva válida

### 1. Crear la estructura de carpetas

Crea la ruta según disciplina y periodo, por ejemplo:
- `Resultados_validas/Motocross/Segundo semestre/`
- `Resultados_validas/Velotierra/Primer semestre/`

### 2. Colocar los CSV

- Crea una carpeta llamada **`FILES EXPORTED`** dentro de la carpeta de la válida.
- Coloca todos los archivos CSV exportados en esa carpeta.

**Formato esperado de nombres de archivo:**
```
CATEGORIA - TIPO - Resultados.csv
```
- **CATEGORIA**: 50cc, 65cc, 85cc MINI, 85cc Junior, 125cc, femenina a, femenina b, INICIO, MX MASTER, MX PREEXPERTOS, MX PRO, MX2, etc.
- **TIPO**: FINAL, CARRERA CLASIFICATORIA / CARRERA CLASIFICACION, 1 CARRERA, 2 CARRERA

**Ejemplos:**
- `125cc - final - resultados.csv`
- `65cc - CARRERA CLASIFICACION - Resultados.csv`
- `85cc Junior - 1 CARRERA - Resultados.csv`

### 3. Crear el script generador

Copia `generar_valida_girardota.py` como plantilla y adapta:

| Variable / Línea | Qué cambiar |
|------------------|-------------|
| `FILES_DIR` | Ruta a tu carpeta `FILES EXPORTED` |
| `OUTPUT_FILE` | Nombre del HTML de salida (ej: `valida_ii_mx_bogota.html`) |
| Título en HTML | Ej: "II Válida Nacional de Motocross - Bogotá" |
| `get_category_sort_key()` | Añadir nuevas categorías si aplica |
| Rutas relativas (`../../../../`) | Según profundidad de la carpeta respecto a la raíz |

**Importante:** El script debe cargar `load-menu.js` con la ruta correcta. Desde `Resultados_validas/Motocross/Primer semestre/` se usan **3 niveles** hacia arriba hasta la raíz: `../../../load-menu.js`. El `load-menu.js` calcula automáticamente la ruta para cargar `menu.html` y `menu-styles.css` desde la raíz del proyecto.

### 4. Ejecutar el script

```bash
cd "Resultados_validas/Motocross/Primer semestre"
python generar_valida_girardota.py
```

### 5. Agregar enlace en el menú

Edita `menu.html` y añade un `<li>` con el enlace a la nueva página dentro del submenú correspondiente:

```html
<li><a href="Resultados_validas/Motocross/Primer semestre/valida_ii_mx_bogota.html">II Válida MX - Bogotá</a></li>
```

El `load-menu.js` ya ajusta rutas que empiezan con `Resultados_validas/`, no hace falta modificar ese archivo.

---

## Funcionalidades que debe tener la página generada

1. **Menú** — Cargado vía `load-menu.js` (contenedor `#menu-container`)
2. **Encabezado** con título de la válida y ubicación
2. **Barra de búsqueda** por nombre o N° del piloto
3. **Tarjetas índice** que enlazan a cada categoría
4. **Secciones por categoría** con:
   - Título destacado + botón flecha para ir al inicio
   - Resumen de mejores tiempos (clasificatoria y carreras)
   - Tabla Final (principal)
   - Desglose (Clasificatoria, Carrera 1, Carrera 2) solo si hay más de una tabla
5. **Búsqueda**: oculta categorías sin resultados, marca las que sí tienen coincidencias
6. **Exportar a PDF**: modal para elegir categorías, luego abre el diálogo de impresión del navegador
7. **Footer** — "Developed by Mauricio Sánchez Aguilar - Fedemoto" y "Este proyecto es de uso interno de FEDEMOTO."

---

## Estilo visual (Manual de Marca)

Consulta `MANUAL_MARCA.md` en la raíz del proyecto. La página debe usar:
- Colores FCM (azul #123E92, amarillo #F7C31D, etc.)
- Fuentes: Bebas Neue (títulos), Roboto Condensed (subtítulos/botones), Inter (texto)
- `border-radius: 8px` en botones y cards
- `transition: all 0.2s ease` en elementos interactivos

---

## Consideraciones de los CSV

- **Columnas:** El script detecta y usa columnas como Pos., N°, Nombre, Mejor Tm, Puntos, Liga, Club, Moto, Vueltas, etc.
- **Clase:** La columna "Clase" se omite en la visualización.
- **Encabezados:** Se muestran con primera letra mayúscula y resto minúscula.
- **Orden de tablas por categoría:** Final → Clasificatoria → Carrera 1 → Carrera 2
