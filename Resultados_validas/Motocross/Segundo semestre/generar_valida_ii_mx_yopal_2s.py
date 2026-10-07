"""
Genera la página HTML de la II Válida Nacional de Motocross (2do semestre) - Yopal, Casanare
reutilizando el generador base del primer semestre para mantener el mismo formato.
Incluye enlaces "Ver vuelta a vuelta" (incluye PDF compartido Femenina A/B).
"""

import os
import re
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PRIMER_SEM = os.path.abspath(os.path.join(SCRIPT_DIR, "..", "Primer semestre"))
if PRIMER_SEM not in sys.path:
    sys.path.insert(0, PRIMER_SEM)

import generar_valida_girardota as base  # noqa: E402

OUTPUT_FILE = os.path.join(SCRIPT_DIR, "valida_ii_mx_yopal.html")
FILES_DIR = os.path.join(SCRIPT_DIR, "FILES EXPORTED_YOPAL")
VUELTA_DIR = os.path.join(SCRIPT_DIR, "VUELTA A VUELTA_YOPAL")
VUELTA_FOLDER_URL = "VUELTA A VUELTA_YOPAL"

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


def alias_femenina_shared_pdfs(pdf_map):
    """Los PDF vienen como 'FEMENINA A Y B'; enlazarlos también a Femenina A y Femenina B."""
    if not pdf_map:
        return pdf_map
    shared = {
        tipo: fn
        for (cat, tipo), fn in pdf_map.items()
        if cat == "femenina a y b"
    }
    for tipo, fn in shared.items():
        pdf_map.setdefault(("femenina a", tipo), fn)
        pdf_map.setdefault(("femenina b", tipo), fn)
    return pdf_map


def generate_html():
    prev_output = base.OUTPUT_FILE
    prev_files = base.FILES_DIR
    base.OUTPUT_FILE = OUTPUT_FILE
    base.FILES_DIR = FILES_DIR
    base.VUELTA_A_VUELTA_FOLDER = VUELTA_FOLDER_URL
    pdf_map = base.build_vuelta_a_vuelta_map(VUELTA_DIR)
    base.VUELTA_A_VUELTA_MAP = alias_femenina_shared_pdfs(pdf_map)
    try:
        base.generate_html()
    finally:
        base.OUTPUT_FILE = prev_output
        base.FILES_DIR = prev_files
        base.VUELTA_A_VUELTA_FOLDER = None
        base.VUELTA_A_VUELTA_MAP = None

    with open(OUTPUT_FILE, "r", encoding="utf-8") as f:
        html_content = f.read()

    html_content = apply_fedemoto_theme(html_content)
    html_content = html_content.replace(
        "I Válida Nacional de Motocross - Girardota, Antioquia | FEDEMOTO",
        "II Válida Nacional de Motocross (2do semestre) - Yopal, Casanare | FEDEMOTO",
    )
    html_content = html_content.replace(
        "<h1>I Válida Nacional de Motocross</h1>",
        "<h1>II Válida Nacional de Motocross — Segundo semestre</h1>",
    )
    html_content = html_content.replace(
        "<p>Girardota, Antioquia - Resultados por categoría</p>",
        "<p>Yopal, Casanare - Resultados por categoría (2do semestre)</p>",
    )

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(html_content)

    print("Página generada:", OUTPUT_FILE)


if __name__ == "__main__":
    generate_html()
