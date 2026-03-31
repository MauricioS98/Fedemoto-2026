# -*- coding: utf-8 -*-
"""
Generador de resultados generales por modalidad/campeonato.
"""

import csv
import html
import json
import os
import re
import unicodedata
from datetime import datetime
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
    generated_at = datetime.now().strftime("%d/%m/%Y")
    liga_podium = defaultdict(
        lambda: {
            "first": 0,
            "second": 0,
            "third": 0,
            "details": {"first": [], "second": [], "third": []},
        }
    )
    for _cat, rows in table_by_categoria.items():
        for pos, rr in enumerate(rows[:3], start=1):
            liga = (rr.get("liga") or "").strip()
            if not liga:
                continue
            if pos == 1:
                liga_podium[liga]["first"] += 1
                liga_podium[liga]["details"]["first"].append(
                    {"categoria": _cat, "piloto": rr.get("nombre", ""), "puntos": rr.get("total", 0)}
                )
            elif pos == 2:
                liga_podium[liga]["second"] += 1
                liga_podium[liga]["details"]["second"].append(
                    {"categoria": _cat, "piloto": rr.get("nombre", ""), "puntos": rr.get("total", 0)}
                )
            elif pos == 3:
                liga_podium[liga]["third"] += 1
                liga_podium[liga]["details"]["third"].append(
                    {"categoria": _cat, "piloto": rr.get("nombre", ""), "puntos": rr.get("total", 0)}
                )
    liga_rows = sorted(
        liga_podium.items(),
        key=lambda kv: (-kv[1]["first"], -kv[1]["second"], -kv[1]["third"], kv[0].lower()),
    )

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
        .toolbar {{ padding: 25px 40px; background: #f8f9fa; border-bottom: 1px solid #c0c0c0; }}
        .search-box {{ width: 100%; padding: 12px 20px; font-family: 'Inter', sans-serif; font-size: 1em; border: 2px solid #d1d5db; border-radius: 8px; }}
        .search-box:focus {{ outline: none; border-color: #123E92; box-shadow: 0 0 0 3px rgba(18, 62, 146, 0.2); }}
        .intro-message {{ padding: 22px 40px; background: #f0f4fc; border-left: 5px solid #123E92; color: #1f2937; border-bottom: 1px solid #c0c0c0; }}
        .index-cards {{ display: flex; flex-wrap: wrap; gap: 12px; padding: 25px 40px; background: #f8f9fa; border-bottom: 1px solid #c0c0c0; }}
        .index-card {{ display: inline-block; padding: 10px 20px; background: white; color: #123E92; border: 2px solid #123E92; border-radius: 8px; font-family: 'Roboto Condensed', sans-serif; font-weight: 700; text-decoration: none; }}
        .index-card.search-match {{ background: #F7C31D; color: #123E92; border-color: #F7C31D; }}
        .index-card.search-no-results {{ display: none !important; }}
        .content-section {{ padding: 40px; }}
        .categoria-section {{ margin-bottom: 38px; border: 2px solid #e0e0e0; border-radius: 12px; overflow: hidden; scroll-margin-top: 115px; }}
        .categoria-section.search-match {{ border-color: #F7C31D; box-shadow: 0 0 0 3px rgba(247, 195, 29, 0.4); }}
        .categoria-section.search-no-results {{ display: none !important; }}
        .categoria-header {{ background: linear-gradient(135deg, #123E92 0%, #0f3377 100%); color: white; padding: 20px 26px; display: flex; align-items: center; justify-content: space-between; gap: 12px; }}
        .categoria-header h2 {{ font-family: 'Bebas Neue', sans-serif; font-size: 1.9em; letter-spacing: 1px; }}
        .btn-top {{ display: inline-flex; align-items: center; justify-content: center; width: 34px; height: 34px; background: rgba(255,255,255,0.2); color: white; border: 2px solid rgba(255,255,255,0.6); border-radius: 8px; cursor: pointer; transition: all 0.2s ease; flex-shrink: 0; }}
        .btn-top:hover {{ background: #F7C31D; color: #123E92; border-color: #F7C31D; }}
        .btn-top svg {{ width: 16px; height: 16px; }}
        .table-wrapper {{ overflow-x: auto; margin: 0; border-top: 1px solid #d1d5db; }}
        table {{ width: 100%; border-collapse: collapse; font-size: 0.92em; }}
        th, td {{ padding: 10px 12px; text-align: left; border-bottom: 1px solid #e0e0e0; white-space: nowrap; }}
        th {{ background: #123E92; color: white; font-family: 'Roboto Condensed', sans-serif; font-weight: 700; position: sticky; top: 0; }}
        tr:nth-child(odd) {{ background: #fafafa; }}
        tr:hover {{ background: #f0f4fc; }}
        tr.pos-1 {{ background: rgba(247, 195, 29, 0.15) !important; }}
        tr.pos-2 {{ background: rgba(192, 192, 192, 0.20) !important; }}
        tr.pos-3 {{ background: rgba(184, 115, 51, 0.16) !important; }}
        tr.search-hidden {{ display: none !important; }}
        .col-total {{ font-weight: 700; color: #123E92; }}
        .liga-summary {{ padding: 22px 40px; background: #f8f9fa; border-bottom: 1px solid #c0c0c0; }}
        .liga-summary h3 {{ font-family: 'Bebas Neue', sans-serif; font-size: 1.6em; color: #123E92; letter-spacing: 1px; margin-bottom: 10px; }}
        .liga-summary table {{ width: 100%; border-collapse: collapse; font-size: 0.92em; }}
        .liga-summary th, .liga-summary td {{ padding: 8px 10px; border-bottom: 1px solid #e5e7eb; text-align: left; }}
        .liga-summary th {{ background: #123E92; color: white; font-family: 'Roboto Condensed', sans-serif; }}
        .liga-summary .num {{ font-family: 'Bebas Neue', sans-serif; font-size: 1.2em; color: #123E92; }}
        .liga-summary tr.pos-1 {{ background: rgba(247, 195, 29, 0.15); }}
        .liga-summary tr.pos-2 {{ background: rgba(192, 192, 192, 0.20); }}
        .liga-summary tr.pos-3 {{ background: rgba(184, 115, 51, 0.16); }}
        .info-btn {{ display: inline-flex; align-items: center; justify-content: center; width: 22px; height: 22px; margin-left: 6px; border: 1px solid #123E92; border-radius: 999px; background: #e8eef8; color: #123E92; font-size: 12px; font-weight: 700; cursor: pointer; }}
        .info-btn:hover {{ background: #123E92; color: #fff; }}
        .modal-overlay {{ display: none; position: fixed; inset: 0; background: rgba(0,0,0,0.5); z-index: 10020; align-items: center; justify-content: center; }}
        .modal-overlay.open {{ display: flex; }}
        .modal-box {{ background: #fff; border-radius: 12px; padding: 24px; max-width: 680px; width: 92%; max-height: 80vh; overflow-y: auto; box-shadow: 0 20px 60px rgba(0,0,0,0.3); }}
        .modal-box h3 {{ font-family: 'Bebas Neue', sans-serif; font-size: 1.6em; color: #123E92; margin-bottom: 14px; }}
        .modal-box ul {{ margin-left: 18px; }}
        .modal-box li {{ margin-bottom: 6px; }}
        .modal-close {{ margin-top: 14px; padding: 10px 16px; border: 0; border-radius: 8px; background: #123E92; color: #fff; font-family: 'Roboto Condensed', sans-serif; cursor: pointer; }}
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
        <div class="intro-message">
            <p>Los resultados generales presentados en esta página están actualizados hasta la fecha <strong>{generated_at}</strong>.</p>
        </div>
        <div class="toolbar">
            <input type="text" id="buscador" class="search-box" placeholder="Buscar por nombre o N° del piloto..." />
        </div>
        <div class="index-cards">
"""]

    for cat in categorias:
        sid = re.sub(r"[^a-z0-9]+", "-", normalize_key(cat)).strip("-")
        html_parts.append(f'            <a href="#{sid}" class="index-card">{esc(cat)}</a>\n')

    html_parts.append("""        </div>
        <div class="liga-summary">
            <h3>Resumen de ligas (podios)</h3>
            <div class="table-wrapper">
                <table>
                    <thead><tr><th>Liga</th><th>1ros</th><th>2dos</th><th>3ros</th></tr></thead>
                    <tbody>
""")
    for i, (liga, cnt) in enumerate(liga_rows, start=1):
        row_class = ""
        if i == 1:
            row_class = ' class="pos-1"'
        elif i == 2:
            row_class = ' class="pos-2"'
        elif i == 3:
            row_class = ' class="pos-3"'
        first_d = html.escape(json.dumps(cnt["details"]["first"], ensure_ascii=False))
        second_d = html.escape(json.dumps(cnt["details"]["second"], ensure_ascii=False))
        third_d = html.escape(json.dumps(cnt["details"]["third"], ensure_ascii=False))
        first_info = f'<button type="button" class="info-btn" data-title="1ros puestos - {esc(liga)}" data-details="{first_d}">i</button>' if cnt["first"] else ""
        second_info = f'<button type="button" class="info-btn" data-title="2dos puestos - {esc(liga)}" data-details="{second_d}">i</button>' if cnt["second"] else ""
        third_info = f'<button type="button" class="info-btn" data-title="3ros puestos - {esc(liga)}" data-details="{third_d}">i</button>' if cnt["third"] else ""
        html_parts.append(
            f'<tr{row_class}><td>{esc(liga)}</td>'
            f'<td class="num">{cnt["first"]}{first_info}</td>'
            f'<td class="num">{cnt["second"]}{second_info}</td>'
            f'<td class="num">{cnt["third"]}{third_info}</td></tr>'
        )
    if not liga_rows:
        html_parts.append('<tr><td colspan="4">Sin datos de podio por liga.</td></tr>')
    html_parts.append("""                    </tbody>
                </table>
            </div>
        </div>
        <div class="content-section">
""")

    for cat in categorias:
        sid = re.sub(r"[^a-z0-9]+", "-", normalize_key(cat)).strip("-")
        rows = table_by_categoria.get(cat, [])
        html_parts.append(f"""            <div class="categoria-section" id="{sid}" data-categoria-id="{sid}">
                <div class="categoria-header"><h2>{esc(cat)}</h2><button type="button" class="btn-top" title="Ir al inicio" aria-label="Ir al inicio"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor"><path d="M12 4l-8 8h5v8h6v-8h5L12 4z"/></svg></button></div>
                <div class="table-wrapper">
                    <table>
                        <thead><tr><th>Pos.</th><th>N°</th><th>Nombre</th><th>Liga</th><th>Club</th><th>Moto</th>""")
        for v in validas:
            html_parts.append(f"<th>{esc(v['label'])}</th>")
        html_parts.append("<th>Total</th></tr></thead><tbody>")
        for i, r in enumerate(rows, start=1):
            pos_class = ""
            if i == 1:
                pos_class = "pos-1"
            elif i == 2:
                pos_class = "pos-2"
            elif i == 3:
                pos_class = "pos-3"
            html_parts.append(f'<tr class="{pos_class}" data-numero="{esc(r["numero"])}" data-nombre="{esc(r["nombre"])}">')
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
    <div id="modalLigaDetalle" class="modal-overlay">
        <div class="modal-box">
            <h3 id="modalLigaDetalleTitle">Detalle</h3>
            <div id="modalLigaDetalleBody"></div>
            <button type="button" id="modalLigaDetalleClose" class="modal-close">Cerrar</button>
        </div>
    </div>
    <script src="{rel_to_root}load-menu.js"></script>
    <script>
        function escapeHtml(t) {{
            return (t + '').replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
        }}
        function renderLigaDetails(raw) {{
            var list = [];
            try {{ list = JSON.parse(raw); }} catch (e) {{ list = []; }}
            if (!Array.isArray(list) || list.length === 0) return '<p>Sin detalles disponibles.</p>';
            var html = '<ul>';
            list.forEach(function(item) {{
                var cat = (item.categoria || '');
                var pil = (item.piloto || '');
                var pts = (item.puntos || 0);
                html += '<li><strong>' + escapeHtml(cat) + '</strong> — ' + escapeHtml(pil) + ' (' + pts + ' pts)</li>';
            }});
            html += '</ul>';
            return html;
        }}
        var modal = document.getElementById('modalLigaDetalle');
        var modalTitle = document.getElementById('modalLigaDetalleTitle');
        var modalBody = document.getElementById('modalLigaDetalleBody');
        document.querySelectorAll('.info-btn').forEach(function(btn) {{
            btn.addEventListener('click', function() {{
                modalTitle.textContent = this.getAttribute('data-title') || 'Detalle';
                modalBody.innerHTML = renderLigaDetails(this.getAttribute('data-details') || '[]');
                modal.classList.add('open');
            }});
        }});
        document.getElementById('modalLigaDetalleClose').addEventListener('click', function() {{
            modal.classList.remove('open');
        }});
        modal.addEventListener('click', function(e) {{
            if (e.target === this) this.classList.remove('open');
        }});
        document.querySelectorAll('.btn-top').forEach(function(btn) {{
            btn.addEventListener('click', function() {{ window.scrollTo({{ top: 0, behavior: 'smooth' }}); }});
        }});
        var buscador = document.getElementById('buscador');
        buscador.addEventListener('input', function() {{
            var q = this.value.trim().toLowerCase();
            var sections = document.querySelectorAll('.categoria-section');
            var cards = document.querySelectorAll('.index-card');
            cards.forEach(function(c){{ c.classList.remove('search-match', 'search-no-results'); }});
            sections.forEach(function(s){{ s.classList.remove('search-match', 'search-no-results'); }});
            if (!q) {{
                document.querySelectorAll('.search-hidden').forEach(function(tr){{ tr.classList.remove('search-hidden'); }});
                return;
            }}
            sections.forEach(function(section) {{
                var rows = section.querySelectorAll('tbody tr[data-numero], tbody tr[data-nombre]');
                var visible = 0;
                rows.forEach(function(tr) {{
                    var num = (tr.getAttribute('data-numero') || '').toLowerCase();
                    var nom = (tr.getAttribute('data-nombre') || '').toLowerCase();
                    var match = num.indexOf(q) >= 0 || nom.indexOf(q) >= 0;
                    tr.classList.toggle('search-hidden', !match);
                    if (match) visible++;
                }});
                var id = section.getAttribute('data-categoria-id');
                var card = document.querySelector('.index-card[href="#' + id + '"]');
                if (visible > 0) {{
                    section.classList.add('search-match');
                    if (card) card.classList.add('search-match');
                }} else {{
                    section.classList.add('search-no-results');
                    if (card) card.classList.add('search-no-results');
                }}
            }});
        }});
    </script>
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
