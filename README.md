# Informe General FEDEMOTO 2025

Sistema de análisis y visualización de datos de participantes y campeonatos de FEDEMOTO para el año 2025.

## Operación actual (válidas, informes y resultados generales)

Además del informe anual, este repositorio ya incluye flujo operativo 2026 para:

- páginas de **Resultados de válidas**
- páginas de **Informes por válida**
- páginas de **Resultados generales por modalidad/campeonato**

### Estructura que se usa hoy

- `Resultados_validas/`: páginas por válida y scripts generadores por modalidad.
- `Informes/`: informes estadísticos por válida.
- `Resultados generales/`: acumulados por categoría (puntos por válida + total).
- `menu.html`: enlaces de navegación para todo el sitio.

### Regenerar todo en un solo comando

En Windows (CMD):

```bat
generar_todo_2026.bat
```

En PowerShell:

```powershell
.\generar_todo_2026.ps1
```

Estos scripts ejecutan, en orden:

1. Generación de páginas de válidas activas:
   - Motocross: Girardota y Barranquilla
   - Velotierra: Tuluá y Barcelona
   - Enduro: I válida 2026
2. Generación de informes por válida:
   - `Informes/generar_informes_validas.py`
   - Regeneración del informe existente de MX Girardota
3. Generación de resultados generales:
   - `Resultados generales/generar_resultados_generales.py`

### Comandos individuales útiles

Resultados de válidas:

```bash
python "Resultados_validas/Motocross/Primer semestre/generar_valida_girardota.py"
python "Resultados_validas/Motocross/Primer semestre/generar_valida_ii_mx_barranquilla.py"
python "Resultados_validas/Velotierra/Primer semestre/generar_valida_vt_tulua.py"
python "Resultados_validas/Velotierra/Primer semestre/generar_valida_ii_vt_barcelona.py"
python "Resultados_validas/Enduro/Primera valida/generar_valida_enduro_2026.py"
```

Informes por válida:

```bash
python "Informes/generar_informes_validas.py"
python "Informes/Motocross/Primer semestre/analizar_valida_csv.py"
python "Informes/Motocross/Primer semestre/generar_informe_html.py"
```

Resultados generales:

```bash
python "Resultados generales/generar_resultados_generales.py"
```

### Reglas implementadas en resultados generales

- Consolidación por piloto usando **N°**, válido **dentro de cada modalidad**.
- Campos por fila: `Nombre`, `Liga`, `Club`, `Moto`, puntos por válida, `Total`.
- Cuando existe tabla final se toma su puntaje; si no existe, se toma la carrera única.
- Orden por categoría respetando el orden de cada modalidad.
- Desempate por la válida más reciente.
- UI alineada a resultados de válidas:
  - barra de búsqueda por `Nombre` o `N°`
  - botón de flecha hacia arriba por categoría
  - resaltado/ocultamiento de categorías e índice según búsqueda
- Resaltado visual de podio por categoría:
  - 1° puesto: dorado/amarillo tenue
  - 2° puesto: plateado/gris tenue
  - 3° puesto: cobre rojizo tenue
- Resumen de ligas por campeonato (debajo del selector de categorías):
  - cuenta solo puestos 1°, 2° y 3° por categoría
  - ordena por: cantidad de 1°; luego 2°; luego 3°
  - aplica también resaltado de podio para las 3 primeras ligas
  - incluye botón `i` en 1ros/2dos/3ros para ver detalle (categoría, piloto y puntaje)
- Mensaje de actualización:
  - antes del buscador se muestra la fecha de última actualización del documento (fecha de generación)

### Cómo ampliar cuando llegue una nueva válida

1. Crear/actualizar la página de resultados en `Resultados_validas/...`.
2. Si aplica informe, agregar configuración en `Informes/generar_informes_validas.py`.
3. Agregar la nueva válida en `CHAMPIONSHIPS` dentro de `Resultados generales/generar_resultados_generales.py`.
4. Ejecutar `generar_todo_2026.bat` (o `.ps1`).
5. Verificar enlaces en `menu.html`.

## 📋 Descripción

Este proyecto genera un informe web interactivo que presenta estadísticas completas sobre:
- Total de licencias únicas participantes
- Total de participaciones (incluyendo repetidos)
- Distribución de pilotos por categoría
- Distribución de deportistas por ligas
- Comparaciones entre semestres (Velotierra y Motocross)
- Detalles por campeonato

## 🎨 Paleta de Colores FEDEMOTO

El proyecto utiliza exclusivamente los colores oficiales de la marca FEDEMOTO:

- **Amarillo**: `#F7C31D` (RGB: 247, 195, 29)
- **Azul**: `#123E92` (RGB: 18, 62, 146)
- **Rojo**: `#E31825` (RGB: 227, 24, 37)
- **Negro**: `#000000`
- **Blanco**: `#FFFFFF`

Todos los elementos visuales utilizan colores sólidos (sin gradientes) para mantener la consistencia de marca.

## 📁 Estructura de Archivos

```
.
├── index.html                      # Página web principal del informe
├── analizar_excel_completo.py      # Script para procesar el Excel y generar datos
├── analizar_colores_logo.py        # Script para extraer colores del logo
├── datos_informe.json              # Datos procesados en formato JSON
├── excel para informe general 2025.xlsx  # Archivo Excel fuente
├── fedemoto-logo.png               # Logo oficial de FEDEMOTO
├── informe_resultados.txt          # Informe en formato texto
└── README.md                       # Este archivo
```

## 🚀 Requisitos

### Para ejecutar el análisis de datos:
- Python 3.7 o superior
- Librerías Python:
  - `pandas`
  - `openpyxl`
  - `Pillow` (solo para análisis de colores)

### Para visualizar el informe:
- Cualquier navegador web moderno (Chrome, Firefox, Edge, Safari)
- No se requiere servidor web (funciona abriendo el archivo directamente)

## 📦 Instalación

1. Clonar o descargar el proyecto
2. Instalar las dependencias de Python:

```bash
pip install pandas openpyxl Pillow
```

## 🔧 Uso

### 1. Procesar datos del Excel

Ejecutar el script de análisis para procesar el archivo Excel:

```bash
python analizar_excel_completo.py
```

Este script:
- Lee el archivo `excel para informe general 2025.xlsx`
- Procesa cada hoja como una modalidad/campeonato
- Normaliza nombres de ligas (elimina acentos)
- Genera `datos_informe.json` con todos los datos procesados
- Genera `informe_resultados.txt` con un resumen en texto

### 2. Visualizar el informe web

Abrir el archivo `index.html` en cualquier navegador web. El archivo contiene los datos incrustados, por lo que no requiere servidor web.

### 3. Análisis de colores del logo (opcional)

Para extraer los colores RGB del logo:

```bash
python analizar_colores_logo.py
```

## 📊 Funcionalidades del Informe Web

### Secciones principales:

1. **🌎 Deportistas por Ligas Totales**
   - Gráfico de barras horizontal
   - Búsqueda y filtrado por nombre de liga
   - Ordenamiento por cantidad o nombre

2. **🎯 Detalle por Campeonato**
   - Selector de campeonato
   - Estadísticas de licencias únicas y total de participaciones
   - Gráficos de columnas para categorías y ligas

3. **📊 Comparación entre Semestres**
   - Comparación Velotierra (1er vs 2do semestre)
   - Comparación Motocross (1er vs 2do semestre)
   - Gráficos de columnas agrupadas
   - Estadísticas de diferencia

4. **📈 Deportistas por Ligas por Categoría**
   - Filtros en cascada: Campeonato → Categoría
   - Gráfico de barras por liga

5. **🏆 Pilotos por Categoría**
   - Filtro por campeonato
   - Gráfico de columnas con cantidad de pilotos

### Características técnicas:

- **Diseño responsive**: Se adapta a diferentes tamaños de pantalla
- **Interactividad**: Filtros, búsquedas y ordenamiento en tiempo real
- **Visualización**: Gráficos de barras y columnas generados con HTML/CSS
- **Datos incrustados**: Los datos JSON están incluidos en el HTML para evitar problemas de CORS
- **Sin dependencias externas**: No requiere librerías JavaScript externas

## 📝 Formato del Excel

El archivo Excel debe tener:
- **Cada hoja** representa una modalidad/campeonato
- **Columnas requeridas**:
  - Columna con nombres de pilotos
  - Columna con categorías
  - Columna con ligas/departamentos

El script normaliza automáticamente:
- Nombres de ligas (elimina acentos: "Bogotá" y "Bogota" se cuentan como uno)
- Nombres de pilotos (para contar únicos)

## 🎯 Datos Generados

El script genera las siguientes métricas:

- `total_pilotos_unicos`: Total de licencias únicas en todos los campeonatos
- `total_participaciones`: Total de participaciones (incluyendo repetidos)
- `pilotos_por_categoria`: Conteo de pilotos por cada categoría
- `deportistas_por_liga_total`: Conteo de deportistas únicos por liga (todas las modalidades)
- `deportistas_por_liga_categoria`: Conteo por liga y categoría
- `modalidades`: Objeto con datos detallados por cada campeonato:
  - `pilotos_unicos`
  - `total_participaciones`
  - `pilotos_por_categoria`
  - `deportistas_por_liga`
  - `deportistas_por_liga_categoria`

## 🔍 Notas Importantes

1. **Categorías únicas**: Las categorías se consideran únicas cuando incluyen la modalidad. Por ejemplo, "115 cc infantil de Moto GP" es diferente de "115 cc de Velocidad".

2. **Normalización de ligas**: Los nombres de ligas se normalizan eliminando acentos para evitar duplicados. En el frontend se muestran con la ortografía correcta.

3. **Datos incrustados**: Los datos JSON están incluidos directamente en el HTML para evitar problemas de CORS al abrir el archivo localmente.

4. **Colores de marca**: Todos los colores utilizados pertenecen a la paleta oficial de FEDEMOTO. No se utilizan gradientes, solo colores sólidos.

## 🛠️ Mantenimiento

### Actualizar datos:

1. Actualizar el archivo Excel con nuevos datos
2. Ejecutar `analizar_excel_completo.py`
3. El archivo `index.html` se actualiza automáticamente con los nuevos datos (si se usa el script de actualización)

### Personalizar colores:

Los colores están definidos en el CSS dentro de `index.html`. Buscar y reemplazar los valores hexadecimales según la paleta de FEDEMOTO.

## 📄 Licencia

Este proyecto es de uso interno de FEDEMOTO.

## 👥 Autor

Developed by Mauricio Sánchez Aguilar - Fedemoto

---

**Versión**: 1.0  
**Año**: 2025

