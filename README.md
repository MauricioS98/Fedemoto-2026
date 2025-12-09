# Informe General FEDEMOTO 2025

Sistema de análisis y visualización de datos de participantes y campeonatos de FEDEMOTO para el año 2025.

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

