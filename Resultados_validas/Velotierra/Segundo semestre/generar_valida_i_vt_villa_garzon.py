"""
Genera la página HTML de la I Válida Nacional Velotierra (2do semestre) - Villa Garzón, Putumayo
reutilizando el generador base de Tuluá para mantener el mismo formato.
Incluye enlaces "Ver vuelta a vuelta" a los PDF de la carpeta homónima.
"""

import os
import re
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PRIMER_SEM = os.path.join(SCRIPT_DIR, "..", "Primer semestre")
sys.path.insert(0, PRIMER_SEM)

import generar_valida_vt_tulua as base  # noqa: E402

OUTPUT_FILE = os.path.join(SCRIPT_DIR, "valida_i_vt_villa_garzon.html")
FILES_DIR = os.path.join(SCRIPT_DIR, "FILES EXPORTED_Villa garzón")
VUELTA_DIR = os.path.join(SCRIPT_DIR, "VUELTA A VUELTA_VILLA GARZÓN")
VUELTA_FOLDER_URL = "VUELTA A VUELTA_VILLA GARZÓN"

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


def generate_html():
    prev_output = base.OUTPUT_FILE
    prev_files = base.FILES_DIR
    base.OUTPUT_FILE = OUTPUT_FILE
    base.FILES_DIR = FILES_DIR
    base.VUELTA_A_VUELTA_FOLDER = VUELTA_FOLDER_URL
    base.VUELTA_A_VUELTA_MAP = base.build_vuelta_a_vuelta_map(VUELTA_DIR)
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
        "I Válida Nacional Velotierra - Tuluá, Valle del Cauca | FEDEMOTO",
        "I Válida Nacional Velotierra - Villa Garzón, Putumayo | FEDEMOTO",
    )
    html_content = html_content.replace(
        "<p>Tuluá, Valle del Cauca - Resultados por categoría</p>",
        "<p>Villa Garzón, Putumayo - Resultados por categoría</p>",
    )

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(html_content)

    print("Página generada:", OUTPUT_FILE)


if __name__ == "__main__":
    generate_html()
