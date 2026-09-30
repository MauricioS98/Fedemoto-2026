---
name: integrar-valida-fedemoto
description: >-
  Automatiza el procesamiento e integración de nuevas válidas en FEDEMOTO a partir de carpetas FILES EXPORTED y VUELTA A VUELTA. Genera la página de resultados de la válida, el informe estadístico, actualiza los resultados generales acumulados y el menú de navegación.
---

# Procedimiento de Integración de Válidas FEDEMOTO

Este skill describe el flujo de trabajo exacto y estandarizado para integrar una nueva válida a partir de las carpetas exportadas de cronometraje (`FILES EXPORTED_*`) y de vuelta a vuelta (`VUELTA A VUELTA_*`).

---

## ⚠️ REGLA CRÍTICA: BONIFICACIÓN DE ASISTENCIA FINAL (8 PUNTOS)

> [!IMPORTANT]
> **REGLA ESTRICTA DE BONO FINAL:**
> El bono de asistencia final de **8 puntos** (`final_valida_bonus: 8` / columna `Bono final`) **ÚNICAMENTE** se debe aplicar si el usuario declara **EXPLÍCITA Y TEXTUALMENTE** que la válida que se está procesando es la **VÁLIDA FINAL** del campeonato/semestre (por ejemplo: *"esta es la válida final"*, *"es la última válida"*, *"con esta concluye el campeonato"*).
> 
> Si el usuario **NO** dice textualmente que es la válida final:
> - **NO** se debe aplicar ningún bono de asistencia.
> - En `generar_resultados_generales.py`, la configuración del campeonato **NO** debe tener `final_valida_bonus` (o debe estar en `0`).
> - La tabla general acumulada mostrará únicamente las columnas de las válidas disputadas (`I`, `II`, `III`...) y `Total`.

---

## Flujo de Trabajo Paso a Paso

### Paso 1: Detección e Inspección de Datos
1. Identificar en qué ruta se ubicaron las carpetas:
   - `Resultados_validas/<Modalidad>/<Semestre>/FILES EXPORTED_<Ciudad>`
   - `Resultados_validas/<Modalidad>/<Semestre>/VUELTA A VUELTA_<Ciudad>`
2. Identificar:
   - **Modalidad:** `Velotierra`, `Motocross`, `Velocidad`, `Enduro`, `GP Colombia`.
   - **Semestre:** `Primer semestre`, `Segundo semestre`, `Campeonato 2026`, etc.
   - **Número de válida:** `I`, `II`, `III`, `IV`, etc.
   - **Ciudad y departamento:** Ej. `Popayán, Cauca`, `Villa Garzón, Putumayo`, `Zarzal, Valle del Cauca`.

### Paso 2: Normalización de Categorías por Modalidad
Verificar los nombres de archivo CSV en `FILES EXPORTED`:
- **Velotierra:** 10 categorías oficiales:
  `125cc`, `Infantil Mini`, `Infantil`, `Juvenil`, `Novatos`, `Expertos`, `Femenina`, `Libre Novatos`, `Libre Pro`, `Master`.
  *Nota:* Si el cronometraje exporta `200 EXPERTOS` o `200 NOVATOS`, mapear canónicamente a `Expertos` y `Novatos`.
- **Enduro:** Usar `canonical_enduro_categoria` (`Enduro 1`, `Enduro 2`, `Enduro 3`, `Junior`, `Master A`, etc.).
- **Motocross:** 12 categorías oficiales (`50cc`, `65cc`, `85cc Mini`, `85cc Junior`, `125cc`, `Femenina`, `Inicio`, `MX Master`, `MX Preexpertos`, `MX Pro`, `MX2`).
  *Nota:* Para la categoría `Inicio`, si no hay archivo Final, sumar `Clasificatoria + Carrera 1 + Carrera 2`.
- **Velocidad en Kartódromo:** Categorías de velocidad según el reglamento respectivo.
- **GP Colombia:** Usar el cargador especializado de GP Colombia si aplica.

### Paso 3: Crear Script y HTML de la Válida (`Resultados_validas/`)
1. Crear el script generador `generar_valida_<num_romano>_<prefijo>_<ciudad_slug>.py` en la carpeta correspondiente.
2. Basarse en el generador de la I Válida de esa modalidad (ej. `generar_valida_vt_tulua.py`).
3. Conectar:
   - `FILES_DIR`: Carpeta `FILES EXPORTED_*`.
   - `VUELTA_DIR`: Carpeta `VUELTA A VUELTA_*`.
   - `OUTPUT_FILE`: `valida_<num_romano>_<prefijo>_<ciudad_slug>.html`.
   - Mapear el `VUELTA_A_VUELTA_MAP` con `build_vuelta_a_vuelta_map`.
4. **Cruce de Metadatos de Pilotos (MOTO, LIGA, CLUB):**
   - En `build_data()`, cruzar siempre los datos de `MOTO`, `LIGA` y `CLUB` entre todas las sesiones de cada categoría (ej. entre Clasificatoria y Carrera) para que ninguna fila quede con celdas vacías si la información existe en algún archivo de la válida.
5. **Estructura Semántica de Bloques de Sesión:**
   - Asignar `class="final-block"` **únicamente** a la sesión principal puntuable (ej. sesión "Final" o "Carrera").
   - Las sesiones complementarias (como "Clasificatoria" o "Entrenamientos") deben llevar `class="session-block"`. Esto permite al motor de exportación a PDF identificar con precisión la tabla oficial de la válida.
6. **Botón y Modal de Exportación a PDF:**
   - El HTML debe incluir el botón `#descargarPDF` ("📄 Descargar resultados en PDF") y el modal `#modalExportar` con selector de categorías.
   - El motor global `exportar-resultados-pdf.js` se inyecta automáticamente mediante `load-menu.js` (o enlazado directo con `<script src="../../exportar-resultados-pdf.js"></script>`).
   - El motor genera un PDF vectorial estilo Excel con:
     - Logo oficial de FEDEMOTO y barra bicromática institucional (#123E92 y #F7C31D).
     - Columnas obligatorias: **Pos.**, **N°**, **Nombre**, **Moto**, **Liga**, **Club**, más métricas de carrera.
     - Resaltado suave de podios (oro, plata y bronce).
7. Inyectar el tema institucional `fedemoto-theme.css` y reemplazar títulos (`<h1>`, `<title>`, `<p>`).
8. Ejecutar el script con Python para generar el HTML de resultados.

### Paso 4: Generar el Informe Estadístico (`Informes/`)
1. Abrir `Informes/generar_informes_validas.py`.
2. Añadir la entrada correspondiente en `REPORT_CONFIGS`:
   ```python
   {
       "output_html": os.path.join(SCRIPT_DIR, "<Modalidad>", "<Semestre>", "informe_valida_<num>_<slug>.html"),
       "files_dir": os.path.join(ROOT_DIR, "Resultados_validas", "<Modalidad>", "<Semestre>", "FILES EXPORTED_<Ciudad>"),
       "title": "Informe <Num> Válida <Mod> - <Ciudad>, <Depto> | FEDEMOTO",
       "heading": "Informe <Num> Válida Nacional <Modalidad> — <Semestre>",
       "subtitle": "<Ciudad>, <Depto> — Estadísticas de la válida",
       "intro": "A continuación se presentan las estadísticas generadas a partir de los resultados de la <Num> Válida Nacional...",
   }
   ```
3. Ejecutar `python Informes/generar_informes_validas.py`.
4. Verificar que se genere `informe_valida_<num>_<slug>.html` con métricas, gráficos de barras y tarjetas.

### Paso 5: Actualizar Resultados Generales Acumulados (`Resultados generales/`)
1. Abrir `Resultados generales/generar_resultados_generales.py`.
2. Localizar el campeonato en `CHAMPIONSHIPS` (ej. `velotierra_2s`, `motocross_1s`, etc.).
3. Añadir la nueva válida al array `validas`:
   ```python
   {
       "label": "<Num> Válida <Mod> - <Ciudad>",
       "files_dir": os.path.join(ROOT_DIR, "Resultados_validas", "<Modalidad>", "<Semestre>", "FILES EXPORTED_<Ciudad>"),
   }
   ```
4. **RECORDAR LA REGLA DEL BONO:**
   - Si el usuario **DECLARÓ EXPLÍCITAMENTE** que es la válida final: incluir `"final_valida_bonus": 8`.
   - Si el usuario **NO** dijo textualmente que es la final: **NO** incluir `final_valida_bonus`.
5. Ejecutar `python "Resultados generales/generar_resultados_generales.py"`.
   - El script cruza automáticamente `Moto`, `Liga` y `Club` de todos los CSVs de la válida para que no queden datos vacíos.
   - La página generada cuenta automáticamente con el botón `📄 Exportar a PDF` para descargar las tablas acumuladas y el resumen de ligas.
6. Si el generador toca las fechas de otros campeonatos que no cambiaron, descartar esos cambios con `git checkout` para mantener limpios solo los archivos pertinentes.

### Paso 6: Actualizar el Menú de Navegación (`menu.html`)
1. Abrir `menu.html`.
2. En la sección `Informes > <Modalidad> > <Semestre>`, añadir:
   ```html
   <li><a href="Informes/<Modalidad>/<Semestre>/informe_valida_<num>_<slug>.html">Informe <Num> Válida <Mod> - <Ciudad>, <Depto></a></li>
   ```
3. En la sección `Resultados de válidas > <Modalidad> > <Semestre>`, añadir:
   ```html
   <li><a href="Resultados_validas/<Modalidad>/<Semestre>/valida_<num>_<slug>.html"><Num> Válida <Mod> - <Ciudad>, <Depto></a></li>
   ```

### Paso 7: Verificación Final
1. Comprobar que los scripts de Python terminen con código 0.
2. Revisar `git status` para confirmar que se generaron los archivos correctos.
3. Verificar que los enlaces "Ver vuelta a vuelta" abran los PDFs correspondientes.
4. **Verificar el botón "Exportar a PDF":**
   - En la página de la válida: comprobar que el botón `#descargarPDF` abra el modal y descargue el PDF vectorial con tablas estilo Excel, logo de FEDEMOTO y las columnas **Moto**, **Liga** y **Club** completas.
   - En los resultados generales: comprobar que el botón `#descargarPDFGeneral` exporte las tablas acumuladas con la misma identidad institucional.
5. Presentar el resumen detallado al usuario.
