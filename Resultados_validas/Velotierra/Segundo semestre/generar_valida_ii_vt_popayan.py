"""
Genera la página HTML de la II Válida Nacional Velotierra (2do semestre) - Popayán, Cauca
reutilizando el generador base de Tuluá para mantener el mismo formato.
Normaliza las categorías '200 Expertos' y '200 Novatos' a 'Expertos' y 'Novatos'.
Incluye enlaces "Ver vuelta a vuelta" a los PDF de la carpeta homónima.
"""

import os
import re
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PRIMER_SEM = os.path.join(SCRIPT_DIR, "..", "Primer semestre")
sys.path.insert(0, PRIMER_SEM)

import generar_valida_vt_tulua as base  # noqa: E402

OUTPUT_FILE = os.path.join(SCRIPT_DIR, "valida_ii_vt_popayan.html")
FILES_DIR = os.path.join(SCRIPT_DIR, "FILES EXPORTED_Popayan")
VUELTA_DIR = os.path.join(SCRIPT_DIR, "VUELTA A VUELTA_Popayan")
VUELTA_FOLDER_URL = "VUELTA A VUELTA_Popayan"

THEME_HEAD = """    <link href="https://fonts.googleapis.com/css2?family=Montserrat:wght@500;600;700;800&family=Source+Sans+3:wght@400;500;600;700&family=Barlow+Condensed:wght@500;600;700&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="../../../fedemoto-theme.css">
    
"""


def apply_fedemoto_theme(html_content):
    return re.sub(
        r'    <link href="https://fonts\.googleapis\.com/css2\?family=Bebas.*?</style>\n',
        THEME_HEAD,
        html_content,
        count=1,
        flags=re.DOTALL,
    )


orig_format_categoria_name = base.format_categoria_name


def custom_format_categoria_name(name):
    formatted = orig_format_categoria_name(name)
    low = formatted.lower().strip()
    if low in ("200 expertos", "expertos 200"):
        return "Expertos"
    if low in ("200 novatos", "novatos 200"):
        return "Novatos"
    return formatted


def generate_html():
    prev_output = base.OUTPUT_FILE
    prev_files = base.FILES_DIR
    prev_format_cat = base.format_categoria_name

    base.OUTPUT_FILE = OUTPUT_FILE
    base.FILES_DIR = FILES_DIR
    prev_exclude = getattr(base, 'EXCLUDE_PILOTOS', set())
    base.EXCLUDE_PILOTOS = {'335', '336'}
    base.format_categoria_name = custom_format_categoria_name
    base.VUELTA_A_VUELTA_FOLDER = VUELTA_FOLDER_URL
    base.VUELTA_A_VUELTA_MAP = base.build_vuelta_a_vuelta_map(VUELTA_DIR)
    try:
        base.generate_html()
    finally:
        base.OUTPUT_FILE = prev_output
        base.FILES_DIR = prev_files
        base.EXCLUDE_PILOTOS = prev_exclude
        base.format_categoria_name = prev_format_cat
        base.VUELTA_A_VUELTA_FOLDER = None
        base.VUELTA_A_VUELTA_MAP = None

    with open(OUTPUT_FILE, "r", encoding="utf-8") as f:
        html_content = f.read()

    html_content = apply_fedemoto_theme(html_content)
    html_content = html_content.replace(
        "I Válida Nacional Velotierra - Tuluá, Valle del Cauca | FEDEMOTO",
        "II Válida Nacional Velotierra - Popayán, Cauca | FEDEMOTO",
    )
    html_content = html_content.replace(
        "<h1>I Válida Nacional Velotierra</h1>",
        "<h1>II Válida Nacional Velotierra</h1>",
    )
    html_content = html_content.replace(
        "<p>Tuluá, Valle del Cauca - Resultados por categoría</p>",
        "<p>Popayán, Cauca - Resultados por categoría</p>",
    )

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(html_content)

    print("Página generada:", OUTPUT_FILE)


if __name__ == "__main__":
    generate_html()
