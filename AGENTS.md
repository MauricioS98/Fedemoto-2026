# Reglas de Proyecto: FEDEMOTO

Este repositorio gestiona los informes estadísticos, resultados de válidas, clasificaciones generales acumuladas y reglamentos de la Federación Colombiana de Motociclismo (FEDEMOTO).

---

## 1. Regla de Oro: Bonificación de Asistencia Final (8 Puntos)

> [!CRITICAL]
> **REGLA ESTRICTA DE BONO FINAL:**
> El bono de asistencia final de **8 puntos** (`final_valida_bonus: 8` / columna `Bono final`) en `Resultados generales/generar_resultados_generales.py` **ÚNICAMENTE** se debe aplicar si el usuario indica **EXPLÍCITA Y TEXTUALMENTE** que la válida procesada es la **VÁLIDA FINAL** del campeonato o semestre (ej. *"esta es la válida final"*, *"es la última válida"*, *"con esta concluye el campeonato"*).
>
> Si el usuario **NO** dice textualmente que es la válida final:
> - **NO** se debe aplicar ningún bono de asistencia.
> - La configuración del campeonato en `generar_resultados_generales.py` **NO** debe incluir `final_valida_bonus`.
> - Las tablas acumuladas mostrarán solo las columnas de las válidas disputadas (`I`, `II`, `III`...) y `Total`.

---

## 2. Flujo Automatizado al Añadir una Nueva Válida

Siempre que el usuario añada o mencione carpetas `FILES EXPORTED_*` y `VUELTA A VUELTA_*`, se debe ejecutar el flujo completo documentado en el skill `integrar-valida-fedemoto`:

1. **Resultados de la válida (`Resultados_validas/`)**:
   - Generar el script `generar_valida_*.py` y el HTML `valida_*.html`.
   - Normalizar nombres de categorías no estándar según la modalidad (ej. en Velotierra `200 EXPERTOS` y `200 NOVATOS` pasan a `Expertos` y `Novatos`).
   - Asociar vuelta a vuelta (`VUELTA A VUELTA_*`) a cada sesión con el botón "Ver vuelta a vuelta".
   - Aplicar el tema institucional `fedemoto-theme.css`.

2. **Informe estadístico (`Informes/`)**:
   - Registrar la válida en `Informes/generar_informes_validas.py` (`REPORT_CONFIGS`).
   - Ejecutar el script y generar `informe_valida_*.html` con métricas, gráficos de barras y tarjetas resumen.

3. **Resultados generales acumulados (`Resultados generales/`)**:
   - Agregar la nueva válida al campeonato en `Resultados generales/generar_resultados_generales.py` (`CHAMPIONSHIPS`).
   - Respetar la **Regla de Oro del Bono Final** descrita arriba.
   - Regenerar el HTML `resultado_general_*.html`.
   - Mantener limpios los demás campeonatos no modificados descartando fechas tocadas por el script.

4. **Menú de navegación (`menu.html`)**:
   - Agregar el enlace del informe en `Informes > [Modalidad] > [Semestre]`.
   - Agregar el enlace de la válida en `Resultados de válidas > [Modalidad] > [Semestre]`.

---

## 3. Comando Rápido: `/nuevo RP` (Reglamentos Particulares)

Cuando el usuario use el comando `/nuevo RP` o pida incorporar reglamentos particulares:
- Activar el skill `nuevo-rp`.
- Ejecutar el script automatizado `.agents/skills/nuevo-rp/scripts/sincronizar_rp_menu.py`.
- Escaneará automáticamente los PDFs en `Reglamentos particulares/` y agregará cualquier archivo faltante al submenú correspondiente en `menu.html` con `target="_blank"`.

