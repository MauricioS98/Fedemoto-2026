# Prompt para crear una nueva página de resultados de válida

Copia y pega el siguiente prompt, **reemplazando los valores entre corchetes** con la información de tu válida. Úsalo con un asistente de IA (Cursor, ChatGPT, etc.) o con un desarrollador.

---

## Prompt

```
Necesito crear una nueva página de resultados para una válida de motocross (o [DISCIPLINA]).

Contexto:
- Los CSV ya están en: Resultados_validas/[DISCIPLINA]/[PERIODO]/FILES EXPORTED/
- El formato de archivos es: CATEGORIA - TIPO - Resultados.csv
  (ej: 125cc - final - resultados.csv, 65cc - 1 CARRERA - Resultados.csv)
- Hay un ejemplo funcionando en: Resultados_validas/Motocross/Primer semestre/
  con el script generar_valida_girardota.py y la página valida_i_mx_girardota.html

Datos de mi válida:
- Nombre: [ej: II Válida Nacional de Motocross]
- Ubicación: [ej: Bogotá, Cundinamarca]
- Archivo HTML de salida: [ej: valida_ii_mx_bogota.html]

Tareas:
1. Crear un script Python (o adaptar el existente) que:
   - Lea todos los CSV de FILES EXPORTED
   - Genere un HTML con la misma estructura y funcionalidades que valida_i_mx_girardota.html
   - Use las rutas relativas correctas para load-menu.js, fedemoto-logo.png, etc.
   - Siga el Manual de Marca (MANUAL_MARCA.md)

2. La página debe incluir:
   - Menú de navegación (load-menu.js + contenedor #menu-container)
   - Footer: "Developed by Mauricio Sánchez Aguilar - Fedemoto" y "Este proyecto es de uso interno de FEDEMOTO."
   - Buscador por nombre o N° del piloto
   - Tarjetas índice por categoría
   - Secciones por categoría con Final y desglose (Clasificatoria, Carrera 1, Carrera 2)
   - Resumen de mejores tiempos (solo el mejor en clasificatoria y el mejor en carreras, indicando en cuál carrera)
   - Botón "Exportar a PDF" que abra un modal para seleccionar categorías, luego el diálogo de impresión del navegador
   - Botón flecha en cada categoría para volver al inicio
   - Ocultar categorías sin resultados al buscar
   - No mostrar desglose si la categoría solo tiene una tabla (ej: 50cc)
   - Quitar la columna "Clase" de las tablas
   - Encabezados con formato "Xxxxxxx" (primera mayúscula, resto minúscula)

3. Agregar el enlace en menu.html bajo:
   Resultados de válidas > [DISCIPLINA] > [PERIODO]
   Texto del enlace: [ej: II Válida MX - Bogotá, Cundinamarca]
   Ruta: Resultados_validas/[DISCIPLINA]/[PERIODO]/[archivo].html

4. Ejecutar el script y verificar que la página se genera correctamente.
```

---

## Variantes según la situación

### Si la carpeta ya existe pero está vacía

```
La carpeta Resultados_validas/Motocross/Segundo semestre/ ya existe.
Acabo de agregar los CSV en FILES EXPORTED.
Necesito el script generador y la página HTML para la "II Válida MX - [Ubicación]".
Usa como referencia generar_valida_girardota.py y valida_i_mx_girardota.html.
```

### Si cambia la disciplina (Velotierra, Enduro, etc.)

```
Necesito lo mismo pero para [DISCIPLINA], no Motocross.
La estructura de carpetas será: Resultados_validas/[DISCIPLINA]/[PERIODO]/
Los CSV pueden tener un formato similar o diferente — revisa los archivos en FILES EXPORTED y adapta el script.
```

### Si los nombres de categorías son distintos

```
Las categorías en mis CSV son: [listar categorías].
Ajusta get_category_sort_key() en el script para ordenarlas correctamente.
```

---

## Referencias rápidas

- **README completo:** `Resultados_validas/README_VALIDAS.md`
- **Manual de marca:** `MANUAL_MARCA.md` (raíz del proyecto)
- **Ejemplo de menú:** `menu.html` líneas 67-70
- **load-menu.js:** Ajusta rutas que empiezan con `Resultados_validas/` automáticamente
