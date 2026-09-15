---
name: nuevo-rp
description: >-
  Detecta y vincula automáticamente nuevos Reglamentos Particulares (RP) en "menu.html" a partir de los archivos PDF ubicados en "Reglamentos particulares/". Se activa al invocar "/nuevo RP", "nuevo RP", o al solicitar agregar o sincronizar reglamentos particulares.
---

# Procedimiento para Sincronizar Nuevos Reglamentos Particulares (RP)

Este skill define el flujo de trabajo para detectar automáticamente nuevos archivos PDF de Reglamentos Particulares en la carpeta `Reglamentos particulares/` e integrarlos con sus respectivos enlaces en el menú de navegación (`menu.html`).

---

## Activación del Skill

Este skill se activa cuando el usuario:
- Escribe el comando rápido `/nuevo RP` o `/nuevo-rp`.
- Dice frases como *"nuevo RP"*, *"agrega el RP"*, *"vincula el reglamento particular"*, *"actualiza los reglamentos del menú"*, etc.
- Coloca uno o varios archivos PDF dentro de las carpetas de `Reglamentos particulares/` y pide reflejarlos en la web.

---

## Estructura de Carpetas y Correspondencia con el Menú

La carpeta `Reglamentos particulares/` se organiza por modalidad y (cuando aplica) por semestre. Su correspondencia exacta dentro de `<li class="dropdown"><a href="#">Reglamentos particulares</a>` en `menu.html` es la siguiente:

| Carpeta en Disco (`Reglamentos particulares/`) | Etiqueta en `menu.html` | Estructura en Menú |
| :--- | :--- | :--- |
| `Enduro/*.pdf` | `Enduro` | Lista directa de enlaces |
| `GP Colombia/*.pdf` | `GP Colombia` | Lista directa de enlaces |
| `Motocross/Primer semestre/*.pdf` | `Motocross` &rarr; `Primer semestre` | Submenú por semestre |
| `Motocross/Segundo semestre/*.pdf` | `Motocross` &rarr; `Segundo semestre` | Submenú por semestre |
| `Velotierra/Primer semestre/*.pdf` | `Velotierra` &rarr; `Primer semestre` | Submenú por semestre |
| `Velotierra/Segundo semestre/*.pdf` | `Velotierra` &rarr; `Segundo semestre` | Submenú por semestre |
| `Velocidad/Primer semestre/*.pdf` | `Velocidad en Kartodromo` &rarr; `Primer semestre` | Submenú por semestre |
| `Velocidad/Segundo semestre/*.pdf` | `Velocidad en Kartodromo` &rarr; `Segundo semestre` | Submenú por semestre |

> [!NOTE]
> La carpeta en disco de Velocidad se llama `Velocidad/`, pero en la barra de navegación de `menu.html` el dropdown se titula **`Velocidad en Kartodromo`**.

---

## Formato Estándar del Enlace en `menu.html`

Cada enlace debe cumplir con las siguientes directrices:
```html
<li><a href="Reglamentos particulares/<Ruta_relativa_con_barras_diagonales>" target="_blank"><Nombre_del_archivo_sin_extension></a></li>
```

- **Ruta relativa**: Siempre usar barras inclinadas normales (`/`), nunca contrabarras (`\`).
- **Atributo `target="_blank"`**: Imprescindible para que el PDF se abra en una nueva pestaña sin sacar al usuario del sitio.
- **Texto del enlace**: Por estándar se utiliza el nombre del archivo PDF limpio (sin la extensión `.pdf`).

---

## Flujo de Ejecución Automatizado

Para asegurar una sincronización rápida, limpia y sin errores de sintaxis HTML ni duplicados, se dispone del script utilitario:
`.agents/skills/nuevo-rp/scripts/sincronizar_rp_menu.py`

### Paso a paso:

1. **Ejecutar la sincronización**:
   ```powershell
   python ".agents/skills/nuevo-rp/scripts/sincronizar_rp_menu.py"
   ```
   *(Opcional: usar `--dry-run` para previsualizar los cambios sin alterar el archivo).*

2. **Validar los cambios**:
   - Comprobar con `git diff menu.html` que la indentación (32 espacios para listas directas, 40 espacios para listas con semestre) y la ubicación dentro de la modalidad/semestre sean correctas.
   - Si no habían archivos pendientes, el script informará que todo ya está sincronizado.

3. **Reportar al usuario**:
   - Informar claramente qué reglamento(s) se detectaron y en qué sección del menú quedaron enlazados.
