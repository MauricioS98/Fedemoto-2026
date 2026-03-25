"""
Genera la página HTML de la II Válida Nacional de Motocross - Barranquilla, Atlántico
reutilizando el generador base de Girardota para mantener el mismo formato.
"""

import os

import generar_valida_girardota as base


SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_FILE = os.path.join(SCRIPT_DIR, "valida_ii_mx_barranquilla.html")


def generate_html():
    base.OUTPUT_FILE = OUTPUT_FILE
    base.generate_html()

    with open(OUTPUT_FILE, "r", encoding="utf-8") as f:
        html_content = f.read()

    html_content = html_content.replace(
        "I Válida Nacional de Motocross - Girardota, Antioquia | FEDEMOTO",
        "II Válida Nacional de Motocross - Barranquilla, Atlántico | FEDEMOTO",
    )
    html_content = html_content.replace(
        "<h1>I Válida Nacional de Motocross</h1>",
        "<h1>II Válida Nacional de Motocross</h1>",
    )
    html_content = html_content.replace(
        "<p>Girardota, Antioquia - Resultados por categoría</p>",
        "<p>Barranquilla, Atlántico - Resultados por categoría</p>",
    )

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(html_content)

    print("Página generada:", OUTPUT_FILE)


if __name__ == "__main__":
    generate_html()
