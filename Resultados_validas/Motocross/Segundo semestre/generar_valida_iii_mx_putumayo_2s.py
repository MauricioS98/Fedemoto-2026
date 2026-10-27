"""
Genera la página HTML de la III Válida Nacional de Motocross (2do semestre) - Villagarzón, Putumayo
reutilizando el generador base para mantener el formato estandarizado.
Incluye enlaces "Ver vuelta a vuelta" (con PDFs compartidos para Femenina A/B y MX Preexpertos/MX Pro)
y motor de exportación a PDF vectorial con identidad institucional FEDEMOTO.
"""

import os
import re
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PRIMER_SEM = os.path.abspath(os.path.join(SCRIPT_DIR, "..", "Primer semestre"))
if PRIMER_SEM not in sys.path:
    sys.path.insert(0, PRIMER_SEM)

import generar_valida_girardota as base  # noqa: E402

OUTPUT_FILE = os.path.join(SCRIPT_DIR, "valida_iii_mx_putumayo.html")
FILES_DIR = os.path.join(SCRIPT_DIR, "FILES EXPORTED_PUTUMAYO")
VUELTA_DIR = os.path.join(SCRIPT_DIR, "VUELTA A VUELTA_PUTUMAYO")
VUELTA_FOLDER_URL = "VUELTA A VUELTA_PUTUMAYO"

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


def alias_shared_pdfs(pdf_map):
    """
    Los PDFs compartidos (FEMENINA A Y B, MX PREEXPERTOS Y MX PRO)
    se enlazan a sus categorías individuales canónicas.
    """
    if not pdf_map:
        return pdf_map
    for (cat, tipo), fn in list(pdf_map.items()):
        c_low = cat.lower().strip()
        if c_low in ("femenina a y b", "femenina a y b "):
            pdf_map.setdefault(("femenina a", tipo), fn)
            pdf_map.setdefault(("femenina b", tipo), fn)
        elif c_low in ("mx preexpertos y mx pro", "mx preexpertos y mx pro "):
            pdf_map.setdefault(("mx preexpertos", tipo), fn)
            pdf_map.setdefault(("mx pro", tipo), fn)
    return pdf_map


def generate_html():
    prev_output = base.OUTPUT_FILE
    prev_files = base.FILES_DIR
    base.OUTPUT_FILE = OUTPUT_FILE
    base.FILES_DIR = FILES_DIR
    base.VUELTA_A_VUELTA_FOLDER = VUELTA_FOLDER_URL
    pdf_map = base.build_vuelta_a_vuelta_map(VUELTA_DIR)
    base.VUELTA_A_VUELTA_MAP = alias_shared_pdfs(pdf_map)
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
        "III Válida Nacional de Motocross (2do semestre) - Villagarzón, Putumayo | FEDEMOTO",
    )
    html_content = html_content.replace(
        "<h1>I Válida Nacional de Motocross</h1>",
        "<h1>III Válida Nacional de Motocross — Segundo semestre</h1>",
    )
    html_content = html_content.replace(
        "<p>Girardota, Antioquia - Resultados por categoría</p>",
        "<p>Villagarzón, Putumayo - Resultados por categoría (2do semestre)</p>",
    )

    # Inyectar script de exportación PDF si no está enlazado explícitamente
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
