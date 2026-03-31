# -*- coding: utf-8 -*-
"""
Genera informes estadísticos (HTML) para válidas a partir de carpetas FILES EXPORTED.
"""

import csv
import json
import os
import re
from collections import defaultdict

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.normpath(os.path.join(SCRIPT_DIR, ".."))


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
        "output_html": os.path.join(SCRIPT_DIR, "Velocidad", "informe_valida_i_velocidad_zarzal.html"),
        "files_dir": os.path.join(ROOT_DIR, "Resultados_validas", "Velocidad", "FILES EXPORTED"),
        "title": "Informe I Válida Velocidad - Zarzal, Valle del Cauca | FEDEMOTO",
        "heading": "Informe I Válida Nacional de Velocidad",
        "subtitle": "Zarzal, Valle del Cauca — Estadísticas de la válida",
        "intro": (
            "A continuación se presentan las estadísticas generadas a partir de los resultados "
            "de la I Válida Nacional de Velocidad, realizada en Zarzal, Valle del Cauca."
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
]


def normalize_text(raw):
    return " ".join(str(raw).strip().split()) if raw is not None else ""


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


def choose_main_file(files):
    def sort_key(item):
        tipo = item[0].lower()
        if "final" in tipo:
            return 0
        if "clasificatoria" in tipo or "clasificacion" in tipo or "clasificación" in tipo:
            return 1
        return 2

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


def collect_rows_by_category(files_dir):
    by_categoria = defaultdict(list)
    files_per_cat = defaultdict(list)

    for filename in os.listdir(files_dir):
        if not filename.lower().endswith(".csv"):
            continue
        filepath = os.path.join(files_dir, filename)
        if not os.path.isfile(filepath):
            continue
        categoria, tipo = parse_filename(filename)
        files_per_cat[categoria].append((tipo, filepath))

    for categoria, files in files_per_cat.items():
        filepath = choose_main_file(files)
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


def analyze(files_dir):
    by_categoria = collect_rows_by_category(files_dir)
    total_participaciones = 0
    pilotos_unicos = set()
    por_liga = defaultdict(set)
    por_club = defaultdict(set)
    por_marca = defaultdict(set)

    for categoria, rows in by_categoria.items():
        total_participaciones += len(rows)
        for numero, _nombre, liga, club, moto in rows:
            pilotos_unicos.add(numero)
            if liga:
                por_liga[liga].add(numero)
            if club:
                por_club[club].add(numero)
            if moto:
                por_marca[moto].add(numero)

    return {
        "participaciones_totales": total_participaciones,
        "pilotos_unicos": len(pilotos_unicos),
        "pilotos_por_liga": {k: len(v) for k, v in sorted(por_liga.items())},
        "pilotos_por_club": {k: len(v) for k, v in sorted(por_club.items())},
        "inscripciones_por_marca": {k: len(v) for k, v in sorted(por_marca.items())},
        "participaciones_por_categoria": {k: len(v) for k, v in sorted(by_categoria.items())},
    }


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
    datos = analyze(files_dir)

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
