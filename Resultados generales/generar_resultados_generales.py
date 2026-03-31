# -*- coding: utf-8 -*-
"""
Generador de resultados generales por modalidad/campeonato.
"""

import csv
import html
import os
import re
import unicodedata
from collections import defaultdict

ROOT_DIR = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))


CHAMPIONSHIPS = [
    {
        "id": "enduro_2026",
        "modalidad": "Enduro",
        "campeonato": "Campeonato 2026",
        "validas": [
            {
                "label": "I Válida Enduro 2026",
                "files_dir": os.path.join(ROOT_DIR, "Resultados_validas", "Enduro", "Primera valida", "FILES EXPORTED"),
            }
        ],
        "output_html": os.path.join(SCRIPT_DIR, "Enduro", "resultado_general_enduro_2026.html"),
    },
    {
        "id": "motocross_1s",
        "modalidad": "Motocross",
        "campeonato": "Primer semestre",
        "validas": [
            {
                "label": "I Válida MX - Girardota",
                "files_dir": os.path.join(ROOT_DIR, "Resultados_validas", "Motocross", "Primer semestre", "FILES EXPORTED-girardota"),
            },
            {
                "label": "II Válida MX - Barranquilla",
                "files_dir": os.path.join(ROOT_DIR, "Resultados_validas", "Motocross", "Primer semestre", "FILES EXPORTED-barranquilla"),
            },
        ],
        "output_html": os.path.join(SCRIPT_DIR, "Motocross", "Primer semestre", "resultado_general_mx_primer_semestre.html"),
    },
    {
        "id": "velocidad_2026",
        "modalidad": "Velocidad",
        "campeonato": "Campeonato 2026",
        "validas": [
            {
                "label": "I Válida Velocidad - Zarzal",
                "files_dir": os.path.join(ROOT_DIR, "Resultados_validas", "Velocidad", "FILES EXPORTED"),
            }
        ],
        "output_html": os.path.join(SCRIPT_DIR, "Velocidad", "resultado_general_velocidad_2026.html"),
    },
    {
        "id": "velotierra_1s",
        "modalidad": "Velotierra",
        "campeonato": "Primer semestre",
        "validas": [
            {
                "label": "I Válida VT - Tuluá",
                "files_dir": os.path.join(ROOT_DIR, "Resultados_validas", "Velotierra", "Primer semestre", "FILES EXPORTED_tulua"),
            },
            {
                "label": "II Válida VT - Barcelona",
                "files_dir": os.path.join(ROOT_DIR, "Resultados_validas", "Velotierra", "Primer semestre", "FILES EXPORTED_barcelona"),
            },
        ],
        "output_html": os.path.join(SCRIPT_DIR, "Velotierra", "Primer semestre", "resultado_general_vt_primer_semestre.html"),
    },
]


def normalize_key(text):
    s = str(text or "").strip().lower()
    s = "".join(c for c in unicodedata.normalize("NFD", s) if unicodedata.category(c) != "Mn")
    s = re.sub(r"[^a-z0-9]+", "", s)
    return s


def pretty_categoria(name):
    parts = [p for p in re.split(r"[\s\-]+", str(name or "").strip()) if p]
    out = []
    for p in parts:
        if re.match(r"^\d+cc$", p, re.I):
            out.append(p.lower())
        elif p.upper() in ("MX", "MX2"):
            out.append(p.upper())
        else:
            out.append(p[0].upper() + p[1:].lower() if len(p) > 1 else p.upper())
    return " ".join(out)


def parse_filename(filename):
    base = filename.replace(".csv", "").strip()
    base = re.sub(r"\s*-\s*resultados\s*$", "", base, flags=re.I).strip()
    parts = [p.strip() for p in re.split(r"\s+-\s+", base, flags=re.I) if p.strip()]
    if len(parts) < 2:
        return pretty_categoria(parts[0] if parts else base), "final"
    categoria = pretty_categoria(" - ".join(parts[:-1]))
    tipo = parts[-1].strip().lower()
    return categoria, tipo


def categoria_sort_key(modalidad, categoria):
    c = categoria.lower()
    if modalidad == "Motocross":
        order = {
            "50cc": 0, "65cc": 1, "85cc mini": 2, "85cc junior": 3, "125cc": 4,
            "femenina a": 5, "femenina b": 6, "femenina a y b": 7,
            "inicio": 8, "mx master": 9, "mx preexpertos": 10, "mx pro": 11, "mx2": 12
        }
        return (order.get(c, 99), categoria)
    if modalidad == "Velotierra":
        order = {
            "125cc": 0, "infantil mini": 1, "infantil": 2, "juvenil": 3,
            "novatos": 4, "expertos": 5, "femenina": 6, "libre novatos": 7, "libre pro": 8, "master": 9
        }
        return (order.get(c, 99), categoria)
    if modalidad == "Enduro":
        order = {
            "scratch": 0, "infantil enduro 1": 1, "infantil enduro 2": 2, "infantil enduro 3": 3,
            "inicio": 4, "juvenil": 5, "junior": 6, "junior novatos": 7, "no racer": 8,
            "femenino": 9, "enduro 1": 10, "enduro 2": 11, "enduro 3": 12, "master a": 13, "master b": 14
        }
        return (order.get(c, 99), categoria)
    return (99, categoria)


def choose_main_file(files):
    def priority(tipo):
        t = normalize_key(tipo)
        if "final" in t:
            return 0
        if t in ("carrera",) or ("carrera" in t and "1" not in t and "2" not in t):
            return 1
        if "clasific" in t or "practica" in t:
            return 2
        if "1carrera" in t:
            return 3
        if "2carrera" in t:
            return 4
        return 9
    return sorted(files, key=lambda x: (priority(x[0]), x[0]))[0]


def find_indexes(headers):
    idx = {"numero": None, "nombre": None, "liga": None, "club": None, "moto": None, "puntos": None}
    for i, h in enumerate(headers):
        hk = normalize_key(h)
        if hk in ("n", "no", "numero"):
            idx["numero"] = i
        elif "nombre" in hk:
            idx["nombre"] = i
        elif "liga" in hk:
            idx["liga"] = i
        elif "club" in hk:
            idx["club"] = i
        elif "moto" in hk:
            idx["moto"] = i
        elif hk in ("totalpuntos", "puntostotales", "puntos"):
            if idx["puntos"] is None or hk == "totalpuntos":
                idx["puntos"] = i
    return idx


def parse_points(value):
    s = str(value or "").strip().replace(",", ".")
    if not s:
        return 0.0
    m = re.search(r"-?\d+(\.\d+)?", s)
    return float(m.group(0)) if m else 0.0


def load_valida_category_rows(files_dir):
    by_cat_files = defaultdict(list)
    for filename in os.listdir(files_dir):
        if not filename.lower().endswith(".csv"):
            continue
        path = os.path.join(files_dir, filename)
        if not os.path.isfile(path):
            continue
        categoria, tipo = parse_filename(filename)
        by_cat_files[categoria].append((tipo, path))

    out = {}
    for categoria, files in by_cat_files.items():
        _tipo, main_path = choose_main_file(files)
        with open(main_path, "r", encoding="utf-8-sig", newline="") as f:
            rows = list(csv.reader(f))
        if not rows:
            continue
        headers = rows[0]
        body = rows[1:]
        idx = find_indexes(headers)
        if idx["numero"] is None or idx["nombre"] is None or idx["puntos"] is None:
            continue
        cat_rows = []
        for r in body:
            if len(r) <= max(idx["numero"], idx["nombre"], idx["puntos"]):
                continue
            numero = str(r[idx["numero"]]).strip()
            if not numero:
                continue
            cat_rows.append({
                "numero": numero,
                "nombre": str(r[idx["nombre"]]).strip(),
                "liga": str(r[idx["liga"]]).strip() if idx["liga"] is not None and idx["liga"] < len(r) else "",
                "club": str(r[idx["club"]]).strip() if idx["club"] is not None and idx["club"] < len(r) else "",
                "moto": str(r[idx["moto"]]).strip() if idx["moto"] is not None and idx["moto"] < len(r) else "",
                "puntos": parse_points(r[idx["puntos"]]),
            })
        out[categoria] = cat_rows
    return out


def build_general_table(champ):
    validas = champ["validas"]
    data_by_valida = []
    for v in validas:
        data_by_valida.append(load_valida_category_rows(v["files_dir"]))

    categorias = set()
    for d in data_by_valida:
        categorias.update(d.keys())

    result = {}
    for categoria in categorias:
        riders = {}
        for i, d in enumerate(data_by_valida):
            for row in d.get(categoria, []):
                key = row["numero"]
                if key not in riders:
                    riders[key] = {
                        "numero": key,
                        "nombre": row["nombre"],
                        "liga": row["liga"],
                        "club": row["club"],
                        "moto": row["moto"],
                        "por_valida": [0.0] * len(validas),
                    }
                riders[key]["por_valida"][i] = row["puntos"]
                # Prefer latest valida values for profile fields when present
                for f in ("nombre", "liga", "club", "moto"):
                    if row[f]:
                        riders[key][f] = row[f]

        rows = []
        for rider in riders.values():
            total = sum(rider["por_valida"])
            rows.append({
                **rider,
                "total": total,
                "latest_points": rider["por_valida"][-1] if rider["por_valida"] else 0.0,
            })
        rows.sort(key=lambda r: (-r["total"], -r["latest_points"], r["nombre"].lower()))
        result[categoria] = rows
    return result


def esc(t):
    return html.escape(str(t)) if t is not None else ""


def fmt_points(v):
    if abs(v - int(v)) < 1e-9:
        return str(int(v))
    return f"{v:.1f}"


def render_html(champ, table_by_categoria):
    validas = champ["validas"]
    rel_to_root = os.path.relpath(ROOT_DIR, os.path.dirname(champ["output_html"])).replace("\\", "/") + "/"

    categorias = sorted(
        table_by_categoria.keys(),
        key=lambda c: categoria_sort_key(champ["modalidad"], c),
    )
    title = f"Resultados generales - {champ['modalidad']} - {champ['campeonato']} | FEDEMOTO"
    h1 = f"Resultados generales {champ['modalidad']}"
    subtitle = champ["campeonato"]

    html_parts = [f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{esc(title)}</title>
    <link rel="icon" type="image/png" href="{rel_to_root}fedemoto-logo.png">
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Roboto+Condensed:wght@300;400;700&family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: 'Inter', sans-serif; background: #f5f5f5; color: #000; line-height: 1.6; padding: 20px; padding-top: 120px; min-height: 100vh; }}
        .container {{ max-width: 1400px; margin: 0 auto; background: white; border-radius: 12px; box-shadow: 0 20px 60px rgba(0,0,0,0.18); overflow: hidden; margin-bottom: 40px; }}
        .container > header {{ background: linear-gradient(135deg, #123E92 0%, #0f3377 100%); color: white; padding: 40px; text-align: center; }}
        .container > header h1 {{ font-family: 'Bebas Neue', sans-serif; font-size: 2.2em; margin-bottom: 10px; letter-spacing: 2px; }}
        .container > header p {{ font-family: 'Roboto Condensed', sans-serif; font-size: 1.2em; opacity: 0.95; }}
        .index-cards {{ display: flex; flex-wrap: wrap; gap: 12px; padding: 25px 40px; background: #f8f9fa; border-bottom: 1px solid #c0c0c0; }}
        .index-card {{ display: inline-block; padding: 10px 20px; background: white; color: #123E92; border: 2px solid #123E92; border-radius: 8px; font-family: 'Roboto Condensed', sans-serif; font-weight: 700; text-decoration: none; }}
        .content-section {{ padding: 40px; }}
        .categoria-section {{ margin-bottom: 38px; border: 2px solid #e0e0e0; border-radius: 12px; overflow: hidden; scroll-margin-top: 115px; }}
        .categoria-header {{ background: linear-gradient(135deg, #123E92 0%, #0f3377 100%); color: white; padding: 20px 26px; }}
        .categoria-header h2 {{ font-family: 'Bebas Neue', sans-serif; font-size: 1.9em; letter-spacing: 1px; }}
        .table-wrapper {{ overflow-x: auto; margin: 0; border-top: 1px solid #d1d5db; }}
        table {{ width: 100%; border-collapse: collapse; font-size: 0.92em; }}
        th, td {{ padding: 10px 12px; text-align: left; border-bottom: 1px solid #e0e0e0; white-space: nowrap; }}
        th {{ background: #123E92; color: white; font-family: 'Roboto Condensed', sans-serif; font-weight: 700; position: sticky; top: 0; }}
        tr:nth-child(odd) {{ background: #fafafa; }}
        tr:hover {{ background: #f0f4fc; }}
        .col-total {{ font-weight: 700; color: #123E92; }}
        footer {{ background: #f8f9fa; padding: 30px 40px; text-align: center; border-top: 1px solid #c0c0c0; color: #000; font-family: 'Inter', sans-serif; font-size: 0.9em; }}
        footer .developer {{ font-family: 'Roboto Condensed', sans-serif; font-weight: 700; color: #123E92; }}
    </style>
</head>
<body>
    <div id="menu-container"></div>
    <div class="container">
        <header>
            <h1>{esc(h1)}</h1>
            <p>{esc(subtitle)}</p>
        </header>
        <div class="index-cards">
"""]

    for cat in categorias:
        sid = re.sub(r"[^a-z0-9]+", "-", normalize_key(cat)).strip("-")
        html_parts.append(f'            <a href="#{sid}" class="index-card">{esc(cat)}</a>\n')

    html_parts.append("""        </div>
        <div class="content-section">
""")

    for cat in categorias:
        sid = re.sub(r"[^a-z0-9]+", "-", normalize_key(cat)).strip("-")
        rows = table_by_categoria.get(cat, [])
        html_parts.append(f"""            <div class="categoria-section" id="{sid}">
                <div class="categoria-header"><h2>{esc(cat)}</h2></div>
                <div class="table-wrapper">
                    <table>
                        <thead><tr><th>Pos.</th><th>N°</th><th>Nombre</th><th>Liga</th><th>Club</th><th>Moto</th>""")
        for v in validas:
            html_parts.append(f"<th>{esc(v['label'])}</th>")
        html_parts.append("<th>Total</th></tr></thead><tbody>")
        for i, r in enumerate(rows, start=1):
            html_parts.append("<tr>")
            html_parts.append(f"<td>{i}</td><td>{esc(r['numero'])}</td><td>{esc(r['nombre'])}</td><td>{esc(r['liga'])}</td><td>{esc(r['club'])}</td><td>{esc(r['moto'])}</td>")
            for p in r["por_valida"]:
                html_parts.append(f"<td>{fmt_points(p)}</td>")
            html_parts.append(f'<td class="col-total">{fmt_points(r["total"])}</td></tr>')
        html_parts.append("</tbody></table></div></div>\n")

    html_parts.append(f"""        </div>
        <footer>
            <p><span class="developer">Developed by Mauricio Sánchez Aguilar - Fedemoto</span></p>
            <p>Este proyecto es de uso interno de FEDEMOTO.</p>
        </footer>
    </div>
    <script src="{rel_to_root}load-menu.js"></script>
</body>
</html>""")
    return "".join(html_parts)


def generate():
    for champ in CHAMPIONSHIPS:
        table = build_general_table(champ)
        out = champ["output_html"]
        os.makedirs(os.path.dirname(out), exist_ok=True)
        with open(out, "w", encoding="utf-8") as f:
            f.write(render_html(champ, table))
        print("Resultado general generado:", out)


if __name__ == "__main__":
    generate()
