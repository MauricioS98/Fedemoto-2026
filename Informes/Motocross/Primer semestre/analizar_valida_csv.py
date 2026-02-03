# -*- coding: utf-8 -*-
"""
Analiza los CSV de resultados de la I Válida MX (Girardota) y genera
estadísticas: participaciones, pilotos únicos, por liga, club, marca.
Salida: datos_informe_valida.json + opcional informe HTML.
"""

import csv
import os
import re
import json
from collections import defaultdict

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
FILES_DIR = os.path.join(SCRIPT_DIR, "FILES EXPORTED")
OUTPUT_JSON = os.path.join(SCRIPT_DIR, "datos_informe_valida.json")


def parse_filename(filename):
    """Extrae categoría y tipo (Final, Clasificatoria, etc.) del nombre del archivo."""
    name = filename.replace(".csv", "").strip()
    name = re.sub(r"\s*-\s*resultados\s*$", "", name, flags=re.I).strip()
    parts = [p.strip() for p in re.split(r"\s+-\s+", name, flags=re.I) if p.strip()]
    if len(parts) < 2:
        return (parts[0] if parts else name, "Final")
    return (" - ".join(parts[:-1]), parts[-1].strip())


def is_final_or_main(tipo_str):
    """True si es el resultado principal de la categoría (Final o única tabla como 50cc)."""
    t = tipo_str.lower()
    return "final" in t or ("clasificatoria" in t and "carrera" not in t) or "clasificacion" in t


def read_csv_headers(filepath):
    """Lee la primera línea y devuelve índices de N°, Nombre, LIGA, CLUB, MOTO."""
    with open(filepath, "r", encoding="utf-8-sig") as f:
        row = next(csv.reader(f))
    headers = [str(h).strip() for h in row]
    idx_num = idx_nombre = idx_liga = idx_club = idx_moto = None
    for i, h in enumerate(headers):
        hl = h.lower()
        if h == "N°" or hl == "n°" or hl == "numero" or hl == "nº":
            idx_num = i
        elif "nombre" in hl:
            idx_nombre = i
        elif "liga" in hl:
            idx_liga = i
        elif "club" in hl:
            idx_club = i
        elif "moto" in hl and "moto" == hl.replace(" ", ""):
            idx_moto = i
    return headers, idx_num, idx_nombre, idx_liga, idx_club, idx_moto


def load_categoria_final_rows():
    """
    Por cada categoría, carga solo el archivo 'principal' (FINAL o único).
    Devuelve: { categoria: [(numero, nombre, liga, club, moto), ...] }
    """
    by_categoria = defaultdict(list)
    files_per_cat = defaultdict(list)

    for filename in os.listdir(FILES_DIR):
        if not filename.lower().endswith(".csv"):
            continue
        filepath = os.path.join(FILES_DIR, filename)
        if not os.path.isfile(filepath):
            continue
        categoria, tipo = parse_filename(filename)
        files_per_cat[categoria].append((tipo, filepath))

    for categoria, files in files_per_cat.items():
        # Ordenar: preferir FINAL, luego Clasificatoria si es la única
        def key_f(f):
            t = f[0].lower()
            if "final" in t:
                return 0
            if "clasificatoria" in t or "clasificacion" in t:
                return 1
            return 2

        files_sorted = sorted(files, key=key_f)
        # Tomar el primero (FINAL o Clasificatoria para 50cc)
        _, filepath = files_sorted[0]
        headers, idx_num, idx_nombre, idx_liga, idx_club, idx_moto = read_csv_headers(filepath)
        if idx_num is None:
            continue
        with open(filepath, "r", encoding="utf-8-sig") as f:
            reader = csv.reader(f)
            next(reader)
            for row in reader:
                if len(row) <= max(i for i in [idx_num, idx_liga, idx_club, idx_moto] if i is not None):
                    continue
                num = str(row[idx_num]).strip() if idx_num is not None else ""
                nombre = str(row[idx_nombre]).strip() if idx_nombre is not None else ""
                liga = str(row[idx_liga]).strip() if idx_liga is not None and idx_liga < len(row) else ""
                club = str(row[idx_club]).strip() if idx_club is not None and idx_club < len(row) else ""
                moto = str(row[idx_moto]).strip() if idx_moto is not None and idx_moto < len(row) else ""
                if num:
                    liga_n = (liga.strip() if liga else "").strip()
                    if liga_n.upper() == "ANTIOQUIA":
                        liga_n = "Antioquia"
                    elif liga_n.upper() == "VALLE":
                        liga_n = "Valle del Cauca"
                    moto_n = (moto.strip() if moto else "").replace("YAMAHA", "Yamaha")
                    club_n = (club.strip() if club else "").strip()
                    by_categoria[categoria].append((num, nombre, liga_n, club_n, moto_n))

    return by_categoria


def analizar():
    by_categoria = load_categoria_final_rows()

    total_participaciones = 0
    todos_numeros = set()
    por_liga = defaultdict(set)
    por_club = defaultdict(set)
    por_marca = defaultdict(set)
    por_categoria = {}

    for categoria, rows in by_categoria.items():
        por_categoria[categoria] = len(rows)
        total_participaciones += len(rows)
        for num, nombre, liga, club, moto in rows:
            todos_numeros.add(num)
            if liga:
                por_liga[liga].add(num)
            if club:
                por_club[club].add(num)
            if moto:
                por_marca[moto].add(num)

    datos = {
        "participaciones_totales": total_participaciones,
        "pilotos_unicos": len(todos_numeros),
        "pilotos_por_liga": {k: len(v) for k, v in sorted(por_liga.items())},
        "pilotos_por_club": {k: len(v) for k, v in sorted(por_club.items())},
        "inscripciones_por_marca": {k: len(v) for k, v in sorted(por_marca.items())},
        "participaciones_por_categoria": por_categoria,
        "pilotos_por_categoria_unicos": {cat: len(set(r[0] for r in rows)) for cat, rows in by_categoria.items()},
    }
    return datos


if __name__ == "__main__":
    datos = analizar()
    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump(datos, f, ensure_ascii=False, indent=2)
    print("Datos guardados en:", OUTPUT_JSON)
    print("Participaciones totales:", datos["participaciones_totales"])
    print("Pilotos únicos:", datos["pilotos_unicos"])
    print("Ligas:", len(datos["pilotos_por_liga"]))
    print("Clubes:", len(datos["pilotos_por_club"]))
    print("Marcas:", list(datos["inscripciones_por_marca"].keys()))
