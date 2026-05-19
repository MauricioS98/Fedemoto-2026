# -*- coding: utf-8 -*-
"""
Genera informes estadísticos (HTML) para válidas a partir de carpetas FILES EXPORTED.
"""

import csv
import json
import os
import re
import unicodedata
from collections import defaultdict

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.normpath(os.path.join(SCRIPT_DIR, ".."))
import sys

sys.path.insert(0, os.path.join(ROOT_DIR, "Resultados generales"))
from enduro_categorias import canonical_enduro_categoria


REPORT_CONFIGS = [
    {
        "output_html": os.path.join(SCRIPT_DIR, "Enduro", "Primera valida", "informe_valida_i_enduro_2026.html"),
        "files_dir": os.path.join(ROOT_DIR, "Resultados_validas", "Enduro", "Primera valida", "FILES EXPORTED"),
        "title": "Informe I Válida Enduro 2026",
        "heading": "Informe I Válida Enduro",
        "subtitle": "Enduro 2026 — Estadísticas de la válida",
        "intro": (
            "A continuación se presentan las estadísticas generadas a partir de los resultados "
            "registrados para la I Válida de Enduro 2026."
        ),
    },
    {
        "output_html": os.path.join(SCRIPT_DIR, "Enduro", "Segunda valida", "informe_valida_ii_enduro_pasca.html"),
        "files_dir": os.path.join(ROOT_DIR, "Resultados_validas", "Enduro", "Segunda valida", "FILES EXPORTED"),
        "title": "Informe II Válida Enduro - Pasca, Cundinamarca | FEDEMOTO",
        "heading": "Informe II Válida Nacional de Enduro",
        "subtitle": "Pasca, Cundinamarca — Estadísticas de la válida",
        "intro": (
            "A continuación se presentan las estadísticas generadas a partir de los resultados "
            "registrados para la II Válida Nacional de Enduro 2026, realizada en Pasca, Cundinamarca."
        ),
    },
    {
        "output_html": os.path.join(SCRIPT_DIR, "Motocross", "Primer semestre", "informe_valida_ii_mx_barranquilla.html"),
        "files_dir": os.path.join(ROOT_DIR, "Resultados_validas", "Motocross", "Primer semestre", "FILES EXPORTED-barranquilla"),
        "title": "Informe II Válida MX - Barranquilla, Atlántico | FEDEMOTO",
        "heading": "Informe II Válida Nacional de Motocross",
        "subtitle": "Barranquilla, Atlántico — Estadísticas de la válida",
        "intro": (
            "A continuación se presentan las estadísticas generadas a partir de los resultados "
            "de la II Válida Nacional de Motocross, realizada en Barranquilla, Atlántico."
        ),
    },
    {
        "output_html": os.path.join(SCRIPT_DIR, "Motocross", "Primer semestre", "informe_valida_iii_mx_tocancipa.html"),
        "files_dir": os.path.join(ROOT_DIR, "Resultados_validas", "Motocross", "Primer semestre", "FILES EXPORTED-tocancipa"),
        "title": "Informe III Válida MX - Tocancipá, Cundinamarca | FEDEMOTO",
        "heading": "Informe III Válida Nacional de Motocross",
        "subtitle": "Tocancipá, Cundinamarca — Estadísticas de la válida",
        "intro": (
            "A continuación se presentan las estadísticas generadas a partir de los resultados "
            "de la III Válida Nacional de Motocross, realizada en Tocancipá, Cundinamarca."
        ),
    },
    {
        "output_html": os.path.join(SCRIPT_DIR, "Velocidad", "informe_valida_i_velocidad_zarzal.html"),
        "files_dir": os.path.join(ROOT_DIR, "Resultados_validas", "Velocidad", "FILES EXPORTED_ZARZAL"),
        "session_priority": ["final", "carrera", "clasificatoria", "otros"],
        "title": "Informe I Válida Velocidad - Zarzal, Valle del Cauca | FEDEMOTO",
        "heading": "Informe I Válida Nacional de Velocidad",
        "subtitle": "Zarzal, Valle del Cauca — Estadísticas de la válida",
        "intro": (
            "A continuación se presentan las estadísticas generadas a partir de los resultados "
            "de la I Válida Nacional de Velocidad, realizada en Zarzal, Valle del Cauca."
        ),
    },
    {
        "output_html": os.path.join(SCRIPT_DIR, "Velocidad", "informe_valida_ii_velocidad_chachagui.html"),
        "files_dir": os.path.join(ROOT_DIR, "Resultados_validas", "Velocidad", "FILES EXPORTED_CHACHAGUI"),
        "session_priority": ["final", "carrera", "clasificatoria", "otros"],
        "title": "Informe II Válida Velocidad - Chachagüi, Nariño | FEDEMOTO",
        "heading": "Informe II Válida Nacional de Velocidad",
        "subtitle": "Chachagüi, Nariño — Estadísticas de la válida",
        "intro": (
            "A continuación se presentan las estadísticas generadas a partir de los resultados "
            "de la II Válida Nacional de Velocidad, realizada en Chachagüi, Nariño."
        ),
    },
    {
        "output_html": os.path.join(SCRIPT_DIR, "Velotierra", "Primer semestre", "informe_valida_i_vt_tulua.html"),
        "files_dir": os.path.join(ROOT_DIR, "Resultados_validas", "Velotierra", "Primer semestre", "FILES EXPORTED_tulua"),
        "title": "Informe I Válida VT - Tuluá, Valle del Cauca | FEDEMOTO",
        "heading": "Informe I Válida Nacional Velotierra",
        "subtitle": "Tuluá, Valle del Cauca — Estadísticas de la válida",
        "intro": (
            "A continuación se presentan las estadísticas generadas a partir de los resultados "
            "de la I Válida Nacional Velotierra, realizada en Tuluá, Valle del Cauca."
        ),
    },
    {
        "output_html": os.path.join(SCRIPT_DIR, "Velotierra", "Primer semestre", "informe_valida_ii_vt_barcelona.html"),
        "files_dir": os.path.join(ROOT_DIR, "Resultados_validas", "Velotierra", "Primer semestre", "FILES EXPORTED_barcelona"),
        "title": "Informe II Válida VT - Barcelona, Quindío | FEDEMOTO",
        "heading": "Informe II Válida Nacional Velotierra",
        "subtitle": "Barcelona, Quindío — Estadísticas de la válida",
        "intro": (
            "A continuación se presentan las estadísticas generadas a partir de los resultados "
            "de la II Válida Nacional Velotierra, realizada en Barcelona, Quindío."
        ),
    },
    {
        "output_html": os.path.join(SCRIPT_DIR, "Velotierra", "Primer semestre", "informe_valida_iii_vt_ibague.html"),
        "files_dir": os.path.join(ROOT_DIR, "Resultados_validas", "Velotierra", "Primer semestre", "FILES EXPORTED_ibague"),
        "title": "Informe III Válida VT - Ibagué, Tolima | FEDEMOTO",
        "heading": "Informe III Válida Nacional Velotierra",
        "subtitle": "Ibagué, Tolima — Estadísticas de la válida",
        "intro": (
            "A continuación se presentan las estadísticas generadas a partir de los resultados "
            "de la III Válida Nacional Velotierra, realizada en Ibagué, Tolima."
        ),
    },
    {
        "output_html": os.path.join(SCRIPT_DIR, "GP Colombia", "informe_valida_i_gp_colombia_vitrix.html"),
        "files_dir": os.path.join(
            ROOT_DIR,
            "Resultados_validas",
            "GP Colombia",
            "FILES EXPORTED_Gran Premio Vitrix",
        ),
        "gp_colombia": True,
        "title": "Informe I Válida GP Colombia - Gran Premio Vitrix | FEDEMOTO",
        "heading": "Informe I Válida GP Colombia",
        "subtitle": "Gran Premio Vitrix — Estadísticas de la válida",
        "intro": (
            "A continuación se presentan las estadísticas generadas a partir de los resultados "
            "de la I Válida GP Colombia 2026, Gran Premio Vitrix."
        ),
    },
]


def normalize_text(raw):
    return " ".join(str(raw).strip().split()) if raw is not None else ""


def normalize_chart_label(raw):
    """Primera letra en mayúscula y el resto en minúsculas (por palabra)."""
    s = normalize_text(raw)
    if not s:
        return ""

    words = []
    for word in s.split():
        if not word:
            continue
        if "." in word:
            word = ".".join(
                (seg[0].upper() + seg[1:].lower()) if seg else ""
                for seg in word.split(".")
            )
        else:
            word = word[0].upper() + word[1:].lower()
        words.append(word)
    return " ".join(words)


def normalize_club(raw):
    s = normalize_text(raw)
    return s.title() if s else ""


def normalize_liga(raw):
    s = normalize_text(raw)
    if not s:
        return ""
    upper = s.upper()
    if upper == "VALLE":
        return "Valle del Cauca"
    if upper == "ANTIOQUIA":
        return "Antioquia"
    return s


def normalize_marca(raw):
    s = normalize_text(raw)
    if not s:
        return ""
    return s.upper().replace("YAMAHA", "Yamaha").title().replace("Yamaha", "Yamaha")


def parse_filename(filename):
    name = filename.replace(".csv", "").strip()
    name = re.sub(r"\s*-\s*resultados\s*$", "", name, flags=re.I).strip()
    parts = [p.strip() for p in re.split(r"\s+-\s+", name, flags=re.I) if p.strip()]
    if len(parts) < 2:
        return (parts[0] if parts else name, "Final")
    return (" - ".join(parts[:-1]), parts[-1].strip())


def normalize_ascii(text):
    raw = str(text or "")
    return "".join(c for c in unicodedata.normalize("NFD", raw) if unicodedata.category(c) != "Mn")


def session_bucket(tipo):
    t = normalize_ascii(tipo).lower()
    if "final" in t:
        return "final"
    if "carrera" in t:
        return "carrera"
    if "clasific" in t:
        return "clasificatoria"
    return "otros"


def choose_main_file(files, session_priority=None):
    priority = session_priority or ["final", "clasificatoria", "carrera", "otros"]
    rank = {name: i for i, name in enumerate(priority)}

    def sort_key(item):
        bucket = session_bucket(item[0])
        return rank.get(bucket, len(rank))

    return sorted(files, key=sort_key)[0][1]


def find_header_indexes(headers):
    idx_num = idx_nombre = idx_liga = idx_club = idx_moto = None
    for i, h in enumerate(headers):
        hl = normalize_text(h).lower()
        hn = hl.replace(" ", "")
        if hl in ("n°", "nº", "numero") or hn in ("n°", "nº", "numero"):
            idx_num = i
        elif "nombre" in hl:
            idx_nombre = i
        elif "liga" in hl:
            idx_liga = i
        elif "club" in hl:
            idx_club = i
        elif "moto" in hn:
            idx_moto = i
    return idx_num, idx_nombre, idx_liga, idx_club, idx_moto


def collect_rows_by_category(files_dir, session_priority=None):
    by_categoria = defaultdict(list)
    files_per_cat = defaultdict(list)

    for filename in os.listdir(files_dir):
        if not filename.lower().endswith(".csv"):
            continue
        filepath = os.path.join(files_dir, filename)
        if not os.path.isfile(filepath):
            continue
        categoria, tipo = parse_filename(filename)
        categoria = canonical_enduro_categoria(categoria)
        files_per_cat[categoria].append((tipo, filepath))

    for categoria, files in files_per_cat.items():
        filepath = choose_main_file(files, session_priority=session_priority)
        with open(filepath, "r", encoding="utf-8-sig") as f:
            reader = csv.reader(f)
            headers = next(reader, [])
            idx_num, idx_nombre, idx_liga, idx_club, idx_moto = find_header_indexes(headers)
            required = [i for i in (idx_num, idx_nombre) if i is not None]
            if not required:
                continue
            for row in reader:
                if len(row) <= max(required):
                    continue
                numero = normalize_text(row[idx_num]) if idx_num is not None and idx_num < len(row) else ""
                if not numero:
                    continue
                nombre = normalize_text(row[idx_nombre]) if idx_nombre is not None and idx_nombre < len(row) else ""
                liga = normalize_liga(row[idx_liga]) if idx_liga is not None and idx_liga < len(row) else ""
                club = normalize_club(row[idx_club]) if idx_club is not None and idx_club < len(row) else ""
                moto = normalize_marca(row[idx_moto]) if idx_moto is not None and idx_moto < len(row) else ""
                by_categoria[categoria].append((numero, nombre, liga, club, moto))

    return by_categoria


def analyze_gp_colombia(files_dir):
    gp_dir = os.path.join(ROOT_DIR, "Resultados_validas", "GP Colombia")
    if gp_dir not in sys.path:
        sys.path.insert(0, gp_dir)
    import generar_valida_i_gp_vitrix as gp

    by_categoria = defaultdict(list)
    rows_by_cat = gp.export_valida_general_rows(files_dir)
    for categoria, rows in rows_by_cat.items():
        for row in rows:
            by_categoria[categoria].append(
                (
                    row["numero"],
                    row["nombre"],
                    normalize_liga(row["liga"]),
                    normalize_club(row["club"]),
                    normalize_marca(row["moto"]),
                )
            )
    return _analyze_from_by_categoria(by_categoria)


def _chart_key_liga(raw):
    return normalize_chart_label(normalize_liga(raw))


def _chart_key_club(raw):
    return normalize_chart_label(normalize_club(raw))


def _chart_key_marca(raw):
    return normalize_chart_label(normalize_marca(raw))


def _chart_key_categoria(raw):
    return normalize_chart_label(raw)


def _analyze_from_by_categoria(by_categoria):
    total_participaciones = 0
    pilotos_unicos = set()
    por_liga = defaultdict(set)
    por_club = defaultdict(set)
    por_marca = defaultdict(set)
    por_categoria = defaultdict(int)

    for categoria, rows in by_categoria.items():
        cat_key = _chart_key_categoria(categoria)
        por_categoria[cat_key] += len(rows)
        total_participaciones += len(rows)
        for numero, _nombre, liga, club, moto in rows:
            pilotos_unicos.add(numero)
            liga_key = _chart_key_liga(liga)
            if liga_key:
                por_liga[liga_key].add(numero)
            club_key = _chart_key_club(club)
            if club_key:
                por_club[club_key].add(numero)
            marca_key = _chart_key_marca(moto)
            if marca_key:
                por_marca[marca_key].add(numero)

    return {
        "participaciones_totales": total_participaciones,
        "pilotos_unicos": len(pilotos_unicos),
        "pilotos_por_liga": {k: len(v) for k, v in sorted(por_liga.items())},
        "pilotos_por_club": {k: len(v) for k, v in sorted(por_club.items())},
        "inscripciones_por_marca": {k: len(v) for k, v in sorted(por_marca.items())},
        "participaciones_por_categoria": dict(sorted(por_categoria.items())),
    }


def analyze(files_dir, session_priority=None):
    by_categoria = collect_rows_by_category(files_dir, session_priority=session_priority)
    return _analyze_from_by_categoria(by_categoria)


def build_html(datos, title, heading, subtitle, intro, root_rel_prefix):
    datos_js = json.dumps(datos, ensure_ascii=False)
    return f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <link rel="icon" type="image/png" href="{root_rel_prefix}fedemoto-logo.png">
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Roboto+Condensed:wght@300;400;700&family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: 'Inter', sans-serif; background: #f5f5f5; color: #000; line-height: 1.6; padding: 20px; padding-top: 120px; min-height: 100vh; }}
        .fixed-header {{ position: fixed; top: 0; left: 0; right: 0; background: #123E92; color: white; z-index: 1000; box-shadow: 0 4px 10px rgba(0,0,0,0.2); }}
        .header-content {{ max-width: 1400px; margin: 0 auto; display: flex; align-items: center; justify-content: space-between; padding: 15px 30px; }}
        .logo-container {{ display: flex; align-items: center; gap: 15px; }}
        .logo-container a {{ display: flex; align-items: center; gap: 15px; text-decoration: none; color: inherit; }}
        .logo-container img {{ height: 50px; width: auto; }}
        .nav-menu {{ display: flex; gap: 0; list-style: none; margin: 0; padding: 0; }}
        .nav-menu li {{ margin: 0; position: relative; }}
        .nav-menu > li > a {{ display: block; padding: 12px 25px; color: white; text-decoration: none; font-family: 'Roboto Condensed', sans-serif; font-weight: 400; font-size: 1.1em; transition: all 0.2s ease; border-radius: 8px; position: relative; cursor: pointer; }}
        .nav-menu > li > a:hover {{ background: rgba(255,255,255,0.1); transform: translateY(-2px); }}
        .dropdown {{ position: relative; }}
        .dropdown > a::after {{ content: ' ▼'; font-size: 0.8em; margin-left: 5px; }}
        .nav-menu > .dropdown::before, .dropdown::before {{ content: ''; position: absolute; top: 100%; left: 0; right: 0; height: 5px; background: transparent; z-index: 1001; }}
        .dropdown-menu .dropdown::before {{ content: ''; position: absolute; top: 0; left: 100%; width: 10px; height: 100%; background: transparent; z-index: 10004; }}
        .dropdown-menu {{ display: none; position: absolute; top: calc(100% + 5px); left: 0; background: white; min-width: 200px; width: 220px; box-shadow: 0 8px 16px rgba(0,0,0,0.2); border-radius: 8px; z-index: 10001; list-style: none; padding: 0; margin: 0; overflow: visible; border: 1px solid #d1d5db; }}
        .dropdown-menu .dropdown {{ position: relative; }}
        .dropdown-menu .dropdown > a {{ position: relative; padding-right: 35px; }}
        .dropdown-menu .dropdown > a::after {{ content: ' ▶'; position: absolute; right: 15px; top: 50%; transform: translateY(-50%); font-size: 0.8em; margin: 0; }}
        .dropdown-menu .dropdown .dropdown-menu {{ display: none !important; position: absolute; left: 100%; top: 0; margin-left: 5px; z-index: 10003; min-width: 180px; background: white; box-shadow: 0 8px 16px rgba(0,0,0,0.2); border-radius: 8px; overflow: visible; border: 1px solid #d1d5db; }}
        .nav-menu > .dropdown:nth-child(3) .dropdown-menu .dropdown .dropdown-menu, .nav-menu > .dropdown:nth-child(4) .dropdown-menu .dropdown .dropdown-menu, .nav-menu > .dropdown:nth-child(5) .dropdown-menu .dropdown .dropdown-menu {{ left: auto !important; right: 100% !important; margin-left: 0 !important; margin-right: 5px !important; }}
        .dropdown-menu .dropdown:hover > .dropdown-menu {{ display: block !important; }}
        .nav-menu > .dropdown:hover > .dropdown-menu, .nav-menu > .dropdown.active > .dropdown-menu {{ display: block; animation: fadeInDown 0.3s ease; }}
        @keyframes fadeInDown {{ from {{ opacity: 0; transform: translateY(-10px); }} to {{ opacity: 1; transform: translateY(0); }} }}
        .dropdown-menu li {{ margin: 0; position: relative; }}
        .dropdown-menu a {{ display: block; padding: 12px 20px; color: #000; text-decoration: none; font-family: 'Inter', sans-serif; font-size: 1em; font-weight: 400; transition: all 0.2s ease; border-bottom: 1px solid #f0f0f0; }}
        .dropdown-menu a:last-child {{ border-bottom: none; }}
        .dropdown-menu a:hover {{ background: #f8f9fa; color: #123E92; }}
        .container {{ max-width: 1400px; margin: 0 auto; background: white; border-radius: 12px; box-shadow: 0 20px 60px rgba(0,0,0,0.15); overflow: hidden; margin-bottom: 40px; }}
        .container > header {{ background: linear-gradient(135deg, #123E92 0%, #0f3377 100%); color: white; padding: 40px; text-align: center; }}
        .container > header h1 {{ font-family: 'Bebas Neue', sans-serif; font-size: 2.2em; margin-bottom: 10px; letter-spacing: 2px; }}
        .container > header p {{ font-family: 'Roboto Condensed', sans-serif; font-size: 1.2em; opacity: 0.95; }}
        .stats-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 20px; padding: 30px 40px; background: #f8f9fa; border-bottom: 1px solid #e0e0e0; }}
        .stat-card {{ background: white; padding: 24px; border-radius: 8px; box-shadow: 0 4px 12px rgba(0,0,0,0.08); text-align: center; }}
        .stat-card .number {{ font-family: 'Bebas Neue', sans-serif; font-size: 2.5em; color: #123E92; margin-bottom: 8px; letter-spacing: 2px; }}
        .stat-card .label {{ font-family: 'Roboto Condensed', sans-serif; font-size: 0.95em; color: #374151; text-transform: uppercase; letter-spacing: 0.5px; }}
        .section {{ padding: 35px 40px; border-bottom: 1px solid #e0e0e0; }}
        .section:last-child {{ border-bottom: none; }}
        .section h2 {{ font-family: 'Bebas Neue', sans-serif; font-size: 1.8em; color: #123E92; margin-bottom: 22px; padding-bottom: 12px; border-bottom: 3px solid #F7C31D; letter-spacing: 1px; }}
        .chart-columns {{ display: flex; flex-direction: column; gap: 12px; }}
        .chart-row {{ display: flex; align-items: center; gap: 12px; min-height: 36px; }}
        .chart-row .label {{ flex: 0 0 220px; font-size: 0.95em; font-weight: 500; color: #111; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }}
        .chart-row .bar-wrap {{ flex: 1 1 200px; height: 28px; background: #e5e7eb; border-radius: 6px; overflow: hidden; min-width: 0; }}
        .chart-row .bar {{ height: 100%; background: linear-gradient(90deg, #123E92 0%, #1a52b8 100%); border-radius: 6px; min-width: 4px; }}
        .chart-row .value {{ flex: 0 0 42px; font-family: 'Bebas Neue', sans-serif; font-size: 1.2em; color: #123E92; text-align: right; letter-spacing: 1px; }}
        .intro-message {{ padding: 28px 40px; background: #f0f4fc; border-left: 5px solid #123E92; border-radius: 0 8px 8px 0; font-size: 1em; line-height: 1.75; color: #1f2937; margin-bottom: 8px; }}
        .footer-informe {{ background: #f8f9fa; padding: 24px 40px; text-align: center; color: #666; font-size: 0.9em; border-top: 1px solid #e0e0e0; }}
        .footer-informe .developer {{ font-family: 'Roboto Condensed', sans-serif; font-weight: 700; color: #123E92; }}
        @media (max-width: 1024px) {{
            body {{ padding: 12px; padding-top: 105px; }}
            .header-content {{ padding: 10px 14px; gap: 10px; }}
            .nav-menu > li > a {{ padding: 10px 14px; font-size: 1em; }}
            .container > header {{ padding: 28px 20px; }}
            .stats-grid {{ grid-template-columns: repeat(2, minmax(0, 1fr)); padding: 20px; gap: 12px; }}
            .section {{ padding: 24px 20px; }}
            .intro-message {{ padding: 20px; margin: 0 10px 8px; }}
        }}
        @media (max-width: 768px) {{
            body {{ padding: 8px; padding-top: 96px; }}
            .header-content {{ align-items: flex-start; flex-direction: column; }}
            .logo-container img {{ height: 42px; }}
            .nav-menu {{ width: 100%; overflow-x: auto; white-space: nowrap; padding-bottom: 4px; }}
            .nav-menu > li > a {{ padding: 9px 12px; font-size: 0.95em; }}
            .dropdown-menu {{ min-width: 180px; width: 190px; }}
            .container {{ border-radius: 10px; }}
            .container > header h1 {{ font-size: 1.7em; letter-spacing: 1px; }}
            .container > header p {{ font-size: 1em; }}
            .stats-grid {{ grid-template-columns: 1fr; }}
            .stat-card {{ padding: 16px; }}
            .stat-card .number {{ font-size: 2em; }}
            .section h2 {{ font-size: 1.5em; margin-bottom: 14px; }}
            .chart-row {{ align-items: flex-start; flex-direction: column; gap: 6px; }}
            .chart-row .label {{ flex: 0 0 auto; width: 100%; white-space: normal; }}
            .chart-row .bar-wrap {{ width: 100%; }}
            .chart-row .value {{ flex: 0 0 auto; width: 100%; text-align: left; }}
        }}
        @media (max-width: 480px) {{
            .container > header {{ padding: 22px 14px; }}
            .intro-message {{ padding: 14px; margin: 0 6px 8px; font-size: 0.92em; }}
            .section {{ padding: 18px 14px; }}
            .footer-informe {{ padding: 18px 14px; }}
        }}
    </style>
</head>
<body>
    <div id="menu-container"></div>
    <div class="container">
        <header>
            <h1>{heading}</h1>
            <p>{subtitle}</p>
        </header>
        <div class="stats-grid" id="statsGrid"></div>
        <div class="intro-message">
            <p>{intro}</p>
            <p>Este informe se basa en las planillas oficiales exportadas para cada categoría.</p>
        </div>
        <div class="section">
            <h2>Pilotos únicos por liga</h2>
            <div class="chart-columns" id="porLiga"></div>
        </div>
        <div class="section">
            <h2>Participaciones por categoría</h2>
            <div class="chart-columns" id="porCategoria"></div>
        </div>
        <div class="section">
            <h2>Inscripciones por marca</h2>
            <div class="chart-columns" id="porMarca"></div>
        </div>
        <div class="section">
            <h2>Pilotos únicos por club</h2>
            <div class="chart-columns" id="porClub"></div>
        </div>
        <div class="footer-informe">
            <p><span class="developer">Developed by Mauricio Sánchez Aguilar - Fedemoto</span></p>
            <p>Este proyecto es de uso interno de FEDEMOTO.</p>
        </div>
    </div>
    <script src="{root_rel_prefix}load-menu.js"></script>
    <script>
        (function() {{
            var datos = {datos_js};
            var stats = [
                {{ num: datos.participaciones_totales, label: 'Participaciones totales' }},
                {{ num: datos.pilotos_unicos, label: 'Pilotos participantes' }},
                {{ num: Object.keys(datos.pilotos_por_liga).length, label: 'Ligas' }},
                {{ num: Object.keys(datos.pilotos_por_club).length, label: 'Clubes' }},
                {{ num: Object.keys(datos.inscripciones_por_marca).length, label: 'Marcas' }}
            ];
            var grid = document.getElementById('statsGrid');
            stats.forEach(function(s) {{
                var card = document.createElement('div');
                card.className = 'stat-card';
                card.innerHTML = '<div class="number">' + s.num + '</div><div class="label">' + s.label + '</div>';
                grid.appendChild(card);
            }});
            function escapeHtml(t) {{ return (t+'').replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;'); }}
            function fillChart(id, obj) {{
                var el = document.getElementById(id);
                var entries = Object.keys(obj).map(function(k) {{ return [k, obj[k]]; }}).sort(function(a, b) {{ return b[1] - a[1]; }});
                var maxVal = entries.length ? Math.max.apply(null, entries.map(function(e) {{ return e[1]; }})) : 1;
                entries.forEach(function(e) {{
                    var row = document.createElement('div');
                    row.className = 'chart-row';
                    var pct = maxVal > 0 ? (e[1] / maxVal * 100) : 0;
                    row.innerHTML = '<span class="label" title="' + escapeHtml(e[0]) + '">' + escapeHtml(e[0]) + '</span><div class="bar-wrap"><div class="bar" style="width:' + pct + '%"></div></div><span class="value">' + e[1] + '</span>';
                    el.appendChild(row);
                }});
            }}
            fillChart('porLiga', datos.pilotos_por_liga);
            fillChart('porCategoria', datos.participaciones_por_categoria);
            fillChart('porMarca', datos.inscripciones_por_marca);
            fillChart('porClub', datos.pilotos_por_club);
        }})();
    </script>
</body>
</html>
"""


def generate_report(config):
    files_dir = config["files_dir"]
    output_html = config["output_html"]
    if not os.path.isdir(files_dir):
        raise FileNotFoundError(f"No existe carpeta de entrada: {files_dir}")
    os.makedirs(os.path.dirname(output_html), exist_ok=True)
    if config.get("gp_colombia"):
        datos = analyze_gp_colombia(files_dir)
    else:
        datos = analyze(files_dir, session_priority=config.get("session_priority"))

    output_dir = os.path.dirname(output_html)
    root_rel_prefix = os.path.relpath(ROOT_DIR, output_dir).replace("\\", "/") + "/"
    html = build_html(
        datos,
        config["title"],
        config["heading"],
        config["subtitle"],
        config["intro"],
        root_rel_prefix,
    )
    with open(output_html, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"Informe generado: {output_html}")


if __name__ == "__main__":
    for cfg in REPORT_CONFIGS:
        generate_report(cfg)
