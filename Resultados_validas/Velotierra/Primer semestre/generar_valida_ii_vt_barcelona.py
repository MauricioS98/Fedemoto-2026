"""
Genera la página HTML de la II Válida Nacional Velotierra - Barcelona, Quindío
reutilizando el generador base de Tuluá para mantener el mismo formato.
Incluye enlaces "Ver vuelta a vuelta" a los PDF de la carpeta homónima.
"""

import os

import generar_valida_vt_tulua as base


SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_FILE = os.path.join(SCRIPT_DIR, "valida_ii_vt_barcelona.html")
FILES_DIR = os.path.join(SCRIPT_DIR, "FILES EXPORTED_barcelona")
VUELTA_DIR = os.path.join(SCRIPT_DIR, "VUELTA A VUELTA_barcelona")
VUELTA_FOLDER_URL = "VUELTA A VUELTA_barcelona"


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

    html_content = html_content.replace(
        "I Válida Nacional Velotierra - Tuluá, Valle del Cauca | FEDEMOTO",
        "II Válida Nacional Velotierra - Barcelona, Quindío | FEDEMOTO",
    )
    html_content = html_content.replace(
        "<h1>I Válida Nacional Velotierra</h1>",
        "<h1>II Válida Nacional Velotierra</h1>",
    )
    html_content = html_content.replace(
        "<p>Tuluá, Valle del Cauca - Resultados por categoría</p>",
        "<p>Barcelona, Quindío - Resultados por categoría</p>",
    )

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(html_content)

    print("Página generada:", OUTPUT_FILE)


if __name__ == "__main__":
    generate_html()
