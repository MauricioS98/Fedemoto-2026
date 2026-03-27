"""
Vuelta a vuelta (PDF tipo * - Laptimes.pdf) para páginas de resultados de válidas.

Convención de archivos (misma idea que los CSV):
  CATEGORIA - TIPO_SESION - Laptimes.pdf

En cada script generador:
  1. Tras .final-block h3 { ... } en el <style>, insertar el comentario CSS_PLACEHOLDER.
  2. Variables de módulo (por defecto None):
       VUELTA_A_VUELTA_FOLDER = "carpeta_relativa_al_html"  # sin barras inicial/final
       VUELTA_A_VUELTA_MAP = build_laptimes_pdf_map(ruta_absoluta_carpeta_pdf, format_categoria_name, tipo_fn)
  3. Donde hoy va <h3>salida</h3> antes de cada tabla de sesión, usar:
       session_title_block(categoria, tipo_sesion, escape_html, pdf_map, folder_url)
     (no añadir botón al título "Desglose por sesión" ni a modales).
  4. Antes de escribir el HTML:
       html_content = inject_vuelta_css(html_content, bool(VUELTA_A_VUELTA_MAP and VUELTA_A_VUELTA_FOLDER))
  5. Tras generar, limpiar: VUELTA_A_VUELTA_MAP = None; VUELTA_A_VUELTA_FOLDER = None

tipo_fn: función (ultimo_segmento_pdf: str) -> str que coincida con el texto de sesión
en la página (p. ej. "Final", "Clasificatoria", "Carrera 1"). Usar los resolutores
tipo_motocross_velotierra, tipo_velotierra, tipo_enduro, tipo_velocidad o un lambda.
"""

from __future__ import annotations

import os
import re
from urllib.parse import quote

VUELTA_CSS = """
        .session-title-row { display: flex; flex-wrap: wrap; align-items: center; justify-content: space-between; gap: 12px; margin: 25px 0 15px; padding-bottom: 8px; border-bottom: 3px solid #F7C31D; }
        .session-title-row h3 { margin: 0; padding: 0; border: none; font-family: 'Bebas Neue', sans-serif; font-size: 1.8em; color: #123E92; letter-spacing: 1px; }
        .btn-vuelta-a-vuelta { display: inline-block; padding: 8px 16px; background: #123E92; color: white; text-decoration: none; border-radius: 8px; font-family: 'Roboto Condensed', sans-serif; font-weight: 700; font-size: 0.9em; white-space: nowrap; transition: all 0.2s ease; }
        .btn-vuelta-a-vuelta:hover { background: #0f3377; color: white; }
        .desglose-block .session-title-row { margin: 20px 0 12px; padding-bottom: 6px; border-bottom: 1px solid #C0C0C0; }
        .desglose-block .session-title-row h3 { font-family: 'Roboto Condensed', sans-serif; font-size: 1.2em; color: #666; font-weight: 700; }
"""

CSS_PLACEHOLDER = "        /*__VUELTA_CSS__*/\n"


def inject_vuelta_css(html_content: str, enabled: bool) -> str:
    return html_content.replace(CSS_PLACEHOLDER, VUELTA_CSS if enabled else "")


def tipo_velotierra(last_part: str, format_categoria_name) -> str:
    """Velotierra: práctica en CSV se etiqueta como Clasificatoria."""
    s = str(last_part).lower().strip()
    if "practica" in s or "práctica" in s:
        return "Clasificatoria"
    return tipo_motocross_velotierra(last_part, format_categoria_name)


def tipo_motocross_velotierra(last_part: str, format_categoria_name) -> str:
    """Alineado con parse_filename de Motocross."""
    s = str(last_part).lower().strip()
    if "final" in s and "1 carrera" not in s and "2 carrera" not in s:
        return "Final"
    if "clasificatoria" in s or "clasificacion" in s:
        return "Clasificatoria"
    if "1 carrera" in s:
        return "Carrera 1"
    if "2 carrera" in s:
        return "Carrera 2"
    return format_categoria_name(last_part)


def tipo_enduro(last_part: str, format_categoria_name) -> str:
    """Alineado con parse_filename de Enduro (Carrera suelta vs Carrera 1/2)."""
    s = str(last_part).lower().strip()
    if "final" in s:
        return "Final"
    if "carrera 1" in s:
        return "Carrera 1"
    if "carrera 2" in s:
        return "Carrera 2"
    if "carrera" in s:
        return "Carrera"
    return format_categoria_name(last_part)


def tipo_velocidad(last_part: str, format_categoria_name) -> str:
    """Alineado con sesiones típicas en Velocidad (Carrera, Clasificatoria, Final, C1/C2)."""
    s = str(last_part).lower().strip()
    if "final" in s and "1 carrera" not in s and "2 carrera" not in s:
        return "Final"
    if "clasific" in s:
        return "Clasificatoria"
    if "carrera 1" in s or re.search(r"^1\s*carrera", s):
        return "Carrera 1"
    if "carrera 2" in s or re.search(r"^2\s*carrera", s):
        return "Carrera 2"
    if "carrera" in s:
        return "Carrera"
    return format_categoria_name(last_part)


def build_laptimes_pdf_map(pdf_dir, format_categoria_name, tipo_from_last_part_fn):
    """
    tipo_from_last_part_fn: (str) -> str  (recibe último segmento del nombre sin Laptimes)
    """
    m = {}
    if not pdf_dir or not os.path.isdir(pdf_dir):
        return m
    for fn in os.listdir(pdf_dir):
        if not fn.lower().endswith(".pdf"):
            continue
        stem = fn[:-4]
        stem = re.sub(r"\s*-\s*Laptimes\s*$", "", stem, flags=re.I).strip()
        parts = [p.strip() for p in re.split(r"\s+-\s+", stem, flags=re.I) if p.strip()]
        if len(parts) < 2:
            continue
        cat_part = " - ".join(parts[:-1])
        categoria = format_categoria_name(cat_part)
        tipo = tipo_from_last_part_fn(parts[-1])
        key = (categoria.lower(), tipo)
        if key in m and m[key] != fn:
            print("Aviso: clave duplicada vuelta a vuelta", key, m[key], "->", fn)
        m[key] = fn
    return m


def session_title_block(categoria, tipo_sesion, escape_html_fn, pdf_map, folder_url):
    if pdf_map and folder_url:
        fn = pdf_map.get((categoria.lower(), tipo_sesion))
        btn = ""
        if fn:
            href = quote(folder_url, safe="") + "/" + quote(fn, safe="")
            btn = (
                f'<a class="btn-vuelta-a-vuelta" href="{escape_html_fn(href)}" '
                f'target="_blank" rel="noopener noreferrer">Ver vuelta a vuelta</a>'
            )
        return (
            f'<div class="session-title-row">'
            f'<h3>{escape_html_fn(tipo_sesion)}</h3>{btn}</div>'
        )
    return f'<h3>{escape_html_fn(tipo_sesion)}</h3>'
