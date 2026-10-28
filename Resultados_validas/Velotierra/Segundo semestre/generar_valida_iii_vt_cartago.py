"""
Genera la página HTML de la III Válida Nacional Velotierra (2do semestre) - Cartago, Valle del Cauca
reutilizando el generador base de Tuluá para mantener el mismo formato.
Normaliza las categorías '200 Expertos' y '200 Novatos' a 'Expertos' y 'Novatos'.
Incluye enlaces "Ver vuelta a vuelta" a los PDF de la carpeta homónima.
Asegura identidad institucional FEDEMOTO, datos completos de Moto, Liga y Club,
y soporte para exportación a PDF vectorial.
"""

import os
import re
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PRIMER_SEM = os.path.join(SCRIPT_DIR, "..", "Primer semestre")
sys.path.insert(0, PRIMER_SEM)

import generar_valida_vt_tulua as base  # noqa: E402

OUTPUT_FILE = os.path.join(SCRIPT_DIR, "valida_iii_vt_cartago.html")
FILES_DIR = os.path.join(SCRIPT_DIR, "FILES EXPORTED_Cartago")
VUELTA_DIR = os.path.join(SCRIPT_DIR, "VUELTA A VUELTA_CARTAGO")
VUELTA_FOLDER_URL = "VUELTA A VUELTA_CARTAGO"

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


def clean_metadata(html_content):
    """
    Normaliza y completa los metadatos de pilotos para que no queden celdas vacías:
    - Jerónimo Álvarez Durango (N° 209): Liga Valle del Cauca, Club Club VALLE.
    - Oscar Rodríguez (N° 729): Liga Valle del Cauca, Moto Husqvarna, Club Sin Club.
    """
    html_content = html_content.replace(
        '<td>VALLE</td><td></td><td>GASGAS</td>',
        '<td>Valle del Cauca</td><td>Club VALLE</td><td>GASGAS</td>'
    )
    html_content = html_content.replace(
        '<td>GASGAS</td><td>VALLE</td><td></td>',
        '<td>GASGAS</td><td>Valle del Cauca</td><td>Club VALLE</td>'
    )
    html_content = html_content.replace(
        '<td>VALLE</td><td></td><td>HUSQ</td>',
        '<td>Valle del Cauca</td><td>Sin Club</td><td>Husqvarna</td>'
    )
    html_content = html_content.replace(
        '<td>HUSQ</td><td>VALLE</td><td></td>',
        '<td>Husqvarna</td><td>Valle del Cauca</td><td>Sin Club</td>'
    )
    return html_content


def generate_html():
    prev_output = base.OUTPUT_FILE
    prev_files = base.FILES_DIR
    prev_format_cat = base.format_categoria_name

    base.OUTPUT_FILE = OUTPUT_FILE
    base.FILES_DIR = FILES_DIR
    base.format_categoria_name = custom_format_categoria_name
    base.VUELTA_A_VUELTA_FOLDER = VUELTA_FOLDER_URL
    base.VUELTA_A_VUELTA_MAP = base.build_vuelta_a_vuelta_map(VUELTA_DIR)
    try:
        base.generate_html()
    finally:
        base.OUTPUT_FILE = prev_output
        base.FILES_DIR = prev_files
        base.format_categoria_name = prev_format_cat
        base.VUELTA_A_VUELTA_FOLDER = None
        base.VUELTA_A_VUELTA_MAP = None

    with open(OUTPUT_FILE, "r", encoding="utf-8") as f:
        html_content = f.read()

    html_content = apply_fedemoto_theme(html_content)
    html_content = html_content.replace(
        "I Válida Nacional Velotierra - Tuluá, Valle del Cauca | FEDEMOTO",
        "III Válida Nacional Velotierra - Cartago, Valle del Cauca | FEDEMOTO",
    )
    html_content = html_content.replace(
        "<h1>I Válida Nacional Velotierra</h1>",
        "<h1>III Válida Nacional Velotierra</h1>",
    )
    html_content = html_content.replace(
        "<p>Tuluá, Valle del Cauca - Resultados por categoría</p>",
        "<p>Cartago, Valle del Cauca - Resultados por categoría</p>",
    )

    # Normalizar metadatos
    html_content = clean_metadata(html_content)

    # Enlazar script exportar-resultados-pdf.js si no está presente
    if "exportar-resultados-pdf.js" not in html_content:
        html_content = html_content.replace(
            '<script src="../../../load-menu.js"></script>',
            '<script src="../../../load-menu.js"></script>\n    <script src="../../../exportar-resultados-pdf.js"></script>',
        )

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(html_content)

    print("Página generada exitosamente:", OUTPUT_FILE)


if __name__ == "__main__":
    generate_html()
