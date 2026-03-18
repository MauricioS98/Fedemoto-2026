"""
Script para generar la página HTML de resultados de la I Válida Nacional de Velocidad - Zarzal.
"""

import csv
import html
import os
import re

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
FILES_DIR = os.path.join(SCRIPT_DIR, "FILES EXPORTED")
OUTPUT_FILE = os.path.join(SCRIPT_DIR, "valida_i_velocidad_zarzal.html")


def format_header(header):
    if not header:
        return ""
    h = str(header).strip()
    return h[0].upper() + h[1:].lower() if h else ""


def format_categoria_name(name):
    if not name:
        return ""
    cleaned = re.sub(r"\s+", " ", str(name).strip())
    parts = cleaned.split(" ")
    result = []
    for part in parts:
        p = part.strip()
        if not p:
            continue
        if re.match(r"^\d+$", p):
            result.append(p)
            continue
        if re.match(r"^\d+cc$", p, re.I):
            result.append(p.lower())
            continue
        if p.upper() in {"CC", "2T", "4T"}:
            result.append(p.upper())
            continue
        result.append(p[0].upper() + p[1:].lower() if len(p) > 1 else p.upper())
    return " ".join(result)


def slugify(text):
    s = re.sub(r"[^\w\s-]", "", str(text).lower())
    return re.sub(r"[\s_]+", "-", s).strip("-")


def escape_html(text):
    return html.escape(str(text)) if text is not None else ""


def parse_filename(filename):
    name = filename.replace(".csv", "").strip()
    name = re.sub(r"\s*-\s*resultados\s*$", "", name, flags=re.I).strip()
    parts = [p.strip() for p in re.split(r"\s*-\s*", name) if p.strip()]
    if len(parts) < 2:
        return format_categoria_name(name), "Final", 0

    categoria = format_categoria_name(parts[0])
    tipo_raw = parts[1].strip().lower()

    if "final" in tipo_raw:
        return categoria, "Final", 0
    if "clasific" in tipo_raw or "pract" in tipo_raw:
        return categoria, "Clasificatoria", 1
    if "carrera 1" in tipo_raw:
        return categoria, "Carrera 1", 2
    if "carrera 2" in tipo_raw:
        return categoria, "Carrera 2", 3
    if "carrera" in tipo_raw:
        return categoria, "Carrera", 2
    return categoria, format_categoria_name(parts[1]), 99


def parse_csv(filepath):
    with open(filepath, "r", encoding="utf-8-sig", newline="") as f:
        rows = list(csv.reader(f))
    return (rows[0], rows[1:]) if rows else ([], [])


def remove_column(headers, rows, column_name):
    idx = next((i for i, h in enumerate(headers) if str(h).strip().lower() == column_name), None)
    if idx is None:
        return headers, rows, None
    new_headers = [h for i, h in enumerate(headers) if i != idx]
    new_rows = [[c for i, c in enumerate(row) if i != idx] for row in rows]
    removed_values = [str(row[idx]).strip() if len(row) > idx else "" for row in rows]
    return new_headers, new_rows, removed_values


def remove_clase_and_comentario(headers, rows):
    headers, rows, _ = remove_column(headers, rows, "clase")
    headers, rows, comentarios = remove_column(headers, rows, "comentario")
    if comentarios is None:
        comentarios = [""] * len(rows)
    return headers, rows, comentarios


def find_column_index(headers, candidates):
    normalized = [str(h).strip().lower() for h in headers]
    for cand in candidates:
        for idx, header in enumerate(normalized):
            if cand in header:
                return idx
    return -1


def time_to_seconds(time_text):
    if not time_text:
        return None
    t = str(time_text).strip()
    if not re.match(r"^\d+:\d{2}(?:\.\d+)?$", t):
        return None
    minutes, seconds = t.split(":")
    return int(minutes) * 60 + float(seconds)


def get_mejor_tiempo(rows, headers):
    idx_num = find_column_index(headers, ["n°", "no", "numero"])
    idx_nombre = find_column_index(headers, ["nombre"])
    idx_tm = find_column_index(headers, ["mejor tm", "mejor tiempo", "tiempo"])
    if idx_num < 0 or idx_nombre < 0 or idx_tm < 0:
        return None

    best = None
    for row in rows:
        if len(row) <= max(idx_num, idx_nombre, idx_tm):
            continue
        tm = str(row[idx_tm]).strip()
        sec = time_to_seconds(tm)
        if sec is None:
            continue
        num = str(row[idx_num]).strip()
        nombre = str(row[idx_nombre]).strip()
        if not num:
            continue
        if best is None or sec < best[0]:
            best = (sec, tm, num, nombre)
    if not best:
        return None
    return best[1], best[2], best[3]


def get_category_sort_key(categoria):
    cat = categoria.lower()
    number_match = re.search(r"\d+", cat)
    base_num = int(number_match.group(0)) if number_match else 999
    if "infantil" in cat:
        sub = 0
    elif "inicio" in cat:
        sub = 1
    elif "elite" in cat:
        sub = 2
    elif "master" in cat:
        sub = 3
    else:
        sub = 4
    return base_num, sub, categoria


def render_row(row, comentario, search_attrs):
    pos_val = str(row[0]).strip() if row else ""
    pos_class = ""
    if pos_val == "1":
        pos_class = ' class="pos-1"'
    elif pos_val == "2":
        pos_class = ' class="pos-2"'
    elif pos_val == "3":
        pos_class = ' class="pos-3"'

    html_parts = [f"<tr{pos_class}{search_attrs}>"]
    for i, cell in enumerate(row):
        if i == 0 and comentario:
            html_parts.append(
                f'<td><span class="pos-cell">{escape_html(cell)}</span>'
                f'<button type="button" class="comentario-btn" data-comentario="{escape_html(comentario)}" '
                f'aria-label="Ver comentario">i</button></td>'
            )
        else:
            html_parts.append(f"<td>{escape_html(cell)}</td>")
    html_parts.append("</tr>")
    return "".join(html_parts)


def build_html(categorias):
    html_content = """<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>I Válida Nacional de Velocidad - Zarzal, Valle del Cauca | FEDEMOTO</title>
    <link rel="icon" type="image/png" href="../../fedemoto-logo.png">
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Roboto+Condensed:wght@300;400;700&family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Inter', sans-serif; background: #f5f5f5; color: #000; line-height: 1.6; padding: 20px; padding-top: 120px; min-height: 100vh; }
        .fixed-header { position: fixed; top: 0; left: 0; right: 0; background: #123E92; color: white; z-index: 1000; box-shadow: 0 4px 10px rgba(0,0,0,0.2); }
        .header-content { max-width: 1400px; margin: 0 auto; display: flex; align-items: center; justify-content: space-between; padding: 15px 30px; }
        .logo-container { display: flex; align-items: center; gap: 15px; }
        .logo-container a { display: flex; align-items: center; gap: 15px; text-decoration: none; color: inherit; }
        .logo-container img { height: 50px; width: auto; }
        .nav-menu { display: flex; gap: 0; list-style: none; margin: 0; padding: 0; }
        .nav-menu li { margin: 0; position: relative; }
        .nav-menu > li > a { display: block; padding: 12px 25px; color: white; text-decoration: none; font-family: 'Roboto Condensed', sans-serif; font-weight: 400; font-size: 1.1em; transition: all 0.2s ease; border-radius: 8px; }
        .nav-menu > li > a:hover { background: rgba(255,255,255,0.1); transform: translateY(-2px); }
        .dropdown { position: relative; }
        .dropdown > a::after { content: ' ▼'; font-size: 0.8em; margin-left: 5px; }
        .dropdown-menu { display: none; position: absolute; top: calc(100% + 5px); left: 0; background: white; min-width: 200px; box-shadow: 0 8px 16px rgba(0,0,0,0.2); border-radius: 8px; z-index: 10001; list-style: none; padding: 0; margin: 0; border: 1px solid #d1d5db; }
        .nav-menu > .dropdown:hover > .dropdown-menu { display: block; }
        .dropdown-menu a { display: block; padding: 12px 20px; color: #000; text-decoration: none; font-family: 'Inter', sans-serif; font-size: 1em; transition: all 0.2s ease; border-bottom: 1px solid #f0f0f0; }
        .dropdown-menu a:hover { background: #f8f9fa; color: #123E92; }
        .container { max-width: 1400px; margin: 0 auto; background: white; border-radius: 12px; box-shadow: 0 20px 60px rgba(0,0,0,0.3); overflow: hidden; margin-bottom: 40px; }
        .container > header { background: linear-gradient(135deg, #123E92 0%, #0f3377 100%); color: white; padding: 40px; text-align: center; }
        .container > header h1 { font-family: 'Bebas Neue', sans-serif; font-size: 2.2em; margin-bottom: 10px; letter-spacing: 2px; }
        .container > header p { font-family: 'Roboto Condensed', sans-serif; font-size: 1.2em; opacity: 0.95; }
        .toolbar { padding: 25px 40px; background: #f8f9fa; border-bottom: 1px solid #C0C0C0; }
        .search-box { width: 100%; padding: 12px 20px; font-family: 'Inter', sans-serif; font-size: 1em; border: 2px solid #d1d5db; border-radius: 8px; }
        .search-box:focus { outline: none; border-color: #123E92; box-shadow: 0 0 0 3px rgba(18, 62, 146, 0.2); }
        .index-cards { display: flex; flex-wrap: wrap; gap: 12px; padding: 25px 40px; background: #f8f9fa; border-bottom: 1px solid #C0C0C0; }
        .index-card { display: inline-block; padding: 10px 20px; background: white; color: #123E92; border: 2px solid #123E92; border-radius: 8px; font-family: 'Roboto Condensed', sans-serif; font-weight: 700; text-decoration: none; transition: all 0.2s ease; }
        .index-card:hover { background: #123E92; color: white; transform: translateY(-2px); }
        .index-card.search-match { background: #F7C31D; color: #123E92; border-color: #F7C31D; }
        .index-card.search-no-results { display: none !important; }
        .content-section { padding: 40px; }
        .categoria-section { margin-bottom: 50px; scroll-margin-top: 120px; border: 2px solid #e0e0e0; border-radius: 12px; overflow: hidden; }
        .categoria-section:last-child { margin-bottom: 0; }
        .categoria-section.search-match { border-color: #F7C31D; box-shadow: 0 0 0 3px rgba(247, 195, 29, 0.4); }
        .categoria-section.search-no-results { display: none !important; }
        .categoria-header { background: linear-gradient(135deg, #123E92 0%, #0f3377 100%); color: white; padding: 25px 30px; display: flex; align-items: center; justify-content: space-between; gap: 15px; }
        .categoria-header h2 { font-family: 'Bebas Neue', sans-serif; font-size: 2em; letter-spacing: 2px; }
        .btn-top { display: inline-flex; align-items: center; justify-content: center; width: 40px; height: 40px; background: rgba(255,255,255,0.2); color: white; border: 2px solid rgba(255,255,255,0.6); border-radius: 8px; cursor: pointer; transition: all 0.2s ease; flex-shrink: 0; }
        .btn-top:hover { background: #F7C31D; color: #123E92; border-color: #F7C31D; }
        .btn-top svg { width: 20px; height: 20px; }
        .times-summary { margin: 20px 30px; padding: 20px; background: #f8f9fa; border-radius: 8px; border-left: 5px solid #123E92; }
        .times-summary h4 { font-family: 'Roboto Condensed', sans-serif; color: #123E92; margin-bottom: 15px; font-size: 1.1em; }
        .times-summary-items p { margin-bottom: 10px; font-size: 1em; }
        .times-summary-items p:last-child { margin-bottom: 0; }
        .final-block { padding: 0 30px 30px; }
        .final-block h3 { font-family: 'Bebas Neue', sans-serif; font-size: 1.8em; color: #123E92; margin: 25px 0 15px; padding-bottom: 8px; border-bottom: 3px solid #F7C31D; letter-spacing: 1px; }
        .desglose-block { padding: 0 30px 30px; background: #fafafa; border-top: 1px solid #e0e0e0; }
        .desglose-block h3 { font-family: 'Roboto Condensed', sans-serif; font-size: 1.2em; color: #666; margin: 20px 0 12px; padding-bottom: 6px; border-bottom: 1px solid #C0C0C0; font-weight: 700; }
        .table-wrapper { overflow-x: auto; margin-bottom: 20px; border-radius: 8px; border: 1px solid #d1d5db; }
        table { width: 100%; border-collapse: collapse; font-size: 0.9em; }
        th, td { padding: 12px 15px; text-align: left; border-bottom: 1px solid #e0e0e0; }
        th { background: #123E92; color: white; font-family: 'Roboto Condensed', sans-serif; font-weight: 700; }
        tr:hover { background: #f8f9fa; }
        tr.search-hidden { display: none !important; }
        .pos-1 { background: rgba(247, 195, 29, 0.15) !important; }
        .pos-2 { background: rgba(192, 192, 192, 0.2) !important; }
        .pos-3 { background: rgba(139, 90, 43, 0.1) !important; }
        .pos-cell { display: inline-block; margin-right: 4px; }
        .comentario-btn { display: inline-flex; align-items: center; justify-content: center; width: 24px; height: 24px; margin-left: 6px; border: 1px solid #123E92; border-radius: 999px; background: #e8eef8; color: #123E92; font-size: 14px; font-weight: 700; cursor: pointer; vertical-align: middle; }
        .comentario-btn:hover, .comentario-btn:focus { background: #123E92; color: white; outline: none; }
        .pdf-section { text-align: center; padding: 40px 20px; border-top: 1px solid #C0C0C0; background: #f8f9fa; }
        .btn-pdf { display: inline-block; padding: 14px 32px; background: #123E92; color: white; border: none; border-radius: 8px; font-family: 'Roboto Condensed', sans-serif; font-size: 1.1em; font-weight: 700; cursor: pointer; transition: all 0.2s ease; }
        .btn-pdf:hover { background: #0f3377; transform: translateY(-2px); }
        .pdf-hint { margin-top: 12px; font-size: 0.9em; color: #666; }
        .modal-overlay { display: none; position: fixed; top: 0; left: 0; right: 0; bottom: 0; background: rgba(0,0,0,0.5); z-index: 10000; align-items: center; justify-content: center; }
        .modal-overlay.open { display: flex; }
        .modal-box { background: white; border-radius: 12px; padding: 30px; max-width: 450px; width: 90%; max-height: 80vh; overflow-y: auto; box-shadow: 0 20px 60px rgba(0,0,0,0.3); }
        .modal-box h3 { font-family: 'Bebas Neue', sans-serif; font-size: 1.6em; color: #123E92; margin-bottom: 20px; }
        .modal-categorias { display: flex; flex-wrap: wrap; gap: 8px 16px; margin-bottom: 20px; }
        .modal-cat-item { display: flex; align-items: center; gap: 8px; cursor: pointer; }
        .modal-cat-item input { cursor: pointer; width: 18px; height: 18px; accent-color: #123E92; }
        .modal-actions { display: flex; gap: 12px; flex-wrap: wrap; }
        .modal-btn { padding: 10px 20px; border-radius: 8px; font-family: 'Roboto Condensed', sans-serif; font-weight: 700; cursor: pointer; border: none; font-size: 1em; transition: all 0.2s ease; }
        .modal-btn-primary { background: #123E92; color: white; }
        .modal-btn-primary:hover { background: #0f3377; }
        .modal-btn-secondary { background: #e5e7eb; color: #374151; }
        .modal-btn-secondary:hover { background: #d1d5db; }
        .modal-btn-link { background: transparent; color: #123E92; text-decoration: underline; }
        .modal-btn-link:hover { color: #0f3377; }
        .categoria-section.pdf-exclude { display: none !important; }
        footer { background: #f8f9fa; padding: 30px 40px; text-align: center; border-top: 1px solid #C0C0C0; color: #000; font-family: 'Inter', sans-serif; font-size: 0.9em; font-weight: 400; line-height: 1.8; }
        footer .developer { font-family: 'Roboto Condensed', sans-serif; font-weight: 700; color: #123E92; }
        @media print {
            @page { size: A4 landscape; margin: 15mm; }
            body { padding: 0 !important; padding-top: 0 !important; background: white !important; }
            #menu-container, .fixed-header, .pdf-section, .toolbar, .index-cards, .btn-top, footer { display: none !important; }
            .container { box-shadow: none !important; max-width: 100% !important; }
            .categoria-section { break-before: page; page-break-before: always; }
            .categoria-section:first-child { break-before: auto; page-break-before: auto; }
            .modal-overlay { display: none !important; }
            .container > header, .categoria-header, th { -webkit-print-color-adjust: exact; print-color-adjust: exact; }
            table { font-size: 0.75em; }
        }
    </style>
</head>
<body>
    <div id="menu-container"></div>
    <div id="contenido-exportar" class="container">
        <header>
            <h1>I Válida Nacional de Velocidad</h1>
            <p>Zarzal, Valle del Cauca - Resultados por categoría</p>
        </header>
        <div class="toolbar">
            <input type="text" id="buscador" class="search-box" placeholder="Buscar por nombre o N° del piloto..." />
        </div>
        <div class="index-cards">
"""

    for categoria in categorias:
        section_id = categoria["section_id"]
        nombre = categoria["nombre"]
        html_content += f'            <a href="#{section_id}" class="index-card" data-categoria-id="{section_id}">{escape_html(nombre)}</a>\n'

    html_content += """        </div>
        <div class="content-section">
"""

    for categoria in categorias:
        section_id = categoria["section_id"]
        nombre = categoria["nombre"]
        tablas = categoria.get("tablas", {})

        final_data = tablas.get("Final")
        carrera_data = tablas.get("Carrera")
        clasif_data = tablas.get("Clasificatoria")
        c1_data = tablas.get("Carrera 1")
        c2_data = tablas.get("Carrera 2")
        has_carrera2 = c2_data is not None

        main_label = None
        main_data = None
        if has_carrera2:
            if final_data:
                main_label, main_data = "Final", final_data
            elif carrera_data:
                main_label, main_data = "Carrera", carrera_data
            elif clasif_data:
                main_label, main_data = "Clasificatoria", clasif_data
            elif c1_data:
                main_label, main_data = "Carrera 1", c1_data
            elif c2_data:
                main_label, main_data = "Carrera 2", c2_data

        html_content += f"""
            <div class="categoria-section" id="{section_id}" data-categoria-id="{section_id}">
                <div class="categoria-header">
                    <h2>{escape_html(nombre)}</h2>
                    <button type="button" class="btn-top" title="Ir al inicio" aria-label="Ir al inicio">
                        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor"><path d="M12 4l-8 8h5v8h6v-8h5L12 4z"/></svg>
                    </button>
                </div>
"""

        best_clasif = get_mejor_tiempo(clasif_data["rows"], clasif_data["headers"]) if clasif_data else None
        best_carrera = None
        if c1_data or c2_data:
            for label, data in (("Carrera 1", c1_data), ("Carrera 2", c2_data)):
                if not data:
                    continue
                best = get_mejor_tiempo(data["rows"], data["headers"])
                if not best:
                    continue
                tm, num, piloto = best
                sec = time_to_seconds(tm)
                if sec is None:
                    continue
                if best_carrera is None or sec < best_carrera[0]:
                    best_carrera = (sec, tm, num, piloto, label)
        elif carrera_data:
            best = get_mejor_tiempo(carrera_data["rows"], carrera_data["headers"])
            if best:
                tm, num, piloto = best
                best_carrera = (time_to_seconds(tm) or 999999.0, tm, num, piloto, "Carrera")

        if best_clasif or best_carrera:
                html_content += """
                <div class="times-summary">
                    <h4>Mejores tiempos - Clasificatoria y carreras</h4>
                    <div class="times-summary-items">
"""
        if best_clasif:
            tm, num, piloto = best_clasif
            html_content += f"""
                        <p><strong>Mejor tiempo Clasificatoria:</strong> {escape_html(tm)} - N° {escape_html(num)} {escape_html(piloto)}</p>
"""
        if best_carrera:
            _, tm, num, piloto, carrera_label = best_carrera
            html_content += f"""
                        <p><strong>Mejor tiempo Carrera:</strong> {escape_html(tm)} ({escape_html(carrera_label)}) - N° {escape_html(num)} {escape_html(piloto)}</p>
"""
        if best_clasif or best_carrera:
            html_content += """
                    </div>
                </div>
"""

        if has_carrera2:
            if main_data:
                headers = main_data["headers"]
                rows = main_data["rows"]
                comentarios = main_data["comentarios"]
                html_content += """
                <div class="final-block">
"""
                html_content += f"""
                    <h3>{escape_html(main_label)}</h3>
"""
                html_content += """
                    <div class="table-wrapper">
                        <table>
                            <thead><tr>
"""
                for h in headers:
                    html_content += f"<th>{escape_html(h)}</th>"
                html_content += "</tr></thead><tbody>"
                for i, row in enumerate(rows):
                    comentario = comentarios[i] if i < len(comentarios) else ""
                    search_attrs = f' data-numero="{escape_html(row[1] if len(row) > 1 else "")}" data-nombre="{escape_html(row[2] if len(row) > 2 else "")}"'
                    html_content += render_row(row, comentario, search_attrs)
                html_content += """
                            </tbody>
                        </table>
                    </div>
                </div>
"""
        else:
            # En velocidad normal: mostrar primero Clasificatoria y luego Carrera, sin desglose.
            ordered_labels = ["Clasificatoria", "Carrera", "Final", "Carrera 1"]
            rendered_any = False
            for label in ordered_labels:
                data = tablas.get(label)
                if not data:
                    continue
                rendered_any = True
                headers = data["headers"]
                rows = data["rows"]
                comentarios = data["comentarios"]
                html_content += """
                <div class="final-block">
"""
                html_content += f"""
                    <h3>{escape_html(label)}</h3>
"""
                html_content += """
                    <div class="table-wrapper">
                        <table>
                            <thead><tr>
"""
                for h in headers:
                    html_content += f"<th>{escape_html(h)}</th>"
                html_content += "</tr></thead><tbody>"
                for i, row in enumerate(rows):
                    comentario = comentarios[i] if i < len(comentarios) else ""
                    search_attrs = f' data-numero="{escape_html(row[1] if len(row) > 1 else "")}" data-nombre="{escape_html(row[2] if len(row) > 2 else "")}"'
                    html_content += render_row(row, comentario, search_attrs)
                html_content += """
                            </tbody>
                        </table>
                    </div>
                </div>
"""
            if not rendered_any:
                # Fallback defensivo por si llega una sesión con nombre no contemplado.
                for label, data in sorted(tablas.items(), key=lambda x: x[0]):
                    headers = data["headers"]
                    rows = data["rows"]
                    comentarios = data["comentarios"]
                    html_content += """
                <div class="final-block">
"""
                    html_content += f"""
                    <h3>{escape_html(label)}</h3>
"""
                    html_content += """
                    <div class="table-wrapper">
                        <table>
                            <thead><tr>
"""
                    for h in headers:
                        html_content += f"<th>{escape_html(h)}</th>"
                    html_content += "</tr></thead><tbody>"
                    for i, row in enumerate(rows):
                        comentario = comentarios[i] if i < len(comentarios) else ""
                        search_attrs = f' data-numero="{escape_html(row[1] if len(row) > 1 else "")}" data-nombre="{escape_html(row[2] if len(row) > 2 else "")}"'
                        html_content += render_row(row, comentario, search_attrs)
                    html_content += """
                            </tbody>
                        </table>
                    </div>
                </div>
"""

        if has_carrera2:
            secondary_order = ["Clasificatoria", "Carrera 1", "Carrera 2", "Carrera", "Final"]
            secondary_blocks = []
            for label in secondary_order:
                if label == main_label:
                    continue
                data = tablas.get(label)
                if data:
                    secondary_blocks.append((label, data))

            if secondary_blocks:
                html_content += """
                <div class="desglose-block">
                    <h3>Desglose por sesión</h3>
"""
                for label, data in secondary_blocks:
                    headers = data["headers"]
                    rows = data["rows"]
                    comentarios = data["comentarios"]
                    html_content += f"""
                    <h3>{escape_html(label)}</h3>
                    <div class="table-wrapper">
                        <table>
                            <thead><tr>
"""
                    for h in headers:
                        html_content += f"<th>{escape_html(h)}</th>"
                    html_content += "</tr></thead><tbody>"
                    for i, row in enumerate(rows):
                        comentario = comentarios[i] if i < len(comentarios) else ""
                        search_attrs = f' data-numero="{escape_html(row[1] if len(row) > 1 else "")}" data-nombre="{escape_html(row[2] if len(row) > 2 else "")}"'
                        html_content += render_row(row, comentario, search_attrs)
                    html_content += """
                            </tbody>
                        </table>
                    </div>
"""
                html_content += """
                </div>
"""

        html_content += """
            </div>
"""

    html_content += """
        </div>
        <div class="pdf-section">
            <button id="descargarPDF" class="btn-pdf">Exportar a PDF</button>
            <p class="pdf-hint">En el diálogo de impresión, elige "Guardar como PDF" o "Microsoft Print to PDF" como destino.</p>
        </div>
        <footer>
            <p><span class="developer">Developed by Mauricio Sánchez Aguilar - Fedemoto</span></p>
            <p>Este proyecto es de uso interno de FEDEMOTO.</p>
        </footer>
    </div>
    <div id="modalExportar" class="modal-overlay">
        <div class="modal-box">
            <h3>Exportar a PDF</h3>
            <p style="margin-bottom: 16px; font-size: 0.95em; color: #374151;">Selecciona las categorías que deseas incluir:</p>
            <div class="modal-categorias" id="modalCategorias">
"""

    for categoria in categorias:
        section_id = categoria["section_id"]
        nombre = categoria["nombre"]
        html_content += f'                <label class="modal-cat-item"><input type="checkbox" value="{section_id}" checked> {escape_html(nombre)}</label>\n'

    html_content += """            </div>
            <div class="modal-actions">
                <button type="button" class="modal-btn modal-btn-link" id="modalSelectAll">Seleccionar todo</button>
                <button type="button" class="modal-btn modal-btn-link" id="modalDeselectAll">Deseleccionar todo</button>
            </div>
            <div class="modal-actions" style="margin-top: 20px;">
                <button type="button" class="modal-btn modal-btn-primary" id="modalExportarBtn">Exportar</button>
                <button type="button" class="modal-btn modal-btn-secondary" id="modalCancelar">Cancelar</button>
            </div>
        </div>
    </div>
    <div id="modalComentario" class="modal-overlay">
        <div class="modal-box">
            <h3>Comentario</h3>
            <p id="modalComentarioTexto" style="margin-bottom: 20px; font-size: 1em; color: #111827; white-space: pre-wrap;"></p>
            <div class="modal-actions">
                <button type="button" class="modal-btn modal-btn-primary" id="modalComentarioCerrar">Cerrar</button>
            </div>
        </div>
    </div>
    <script src="../../load-menu.js"></script>
    <script>
        document.getElementById('descargarPDF').addEventListener('click', function() {
            document.querySelectorAll('.search-no-results').forEach(function(el){ el.classList.remove('search-no-results'); });
            document.querySelectorAll('.search-hidden').forEach(function(el){ el.classList.remove('search-hidden'); });
            document.getElementById('modalExportar').classList.add('open');
        });

        document.getElementById('modalSelectAll').addEventListener('click', function() {
            document.querySelectorAll('#modalCategorias input').forEach(function(cb){ cb.checked = true; });
        });
        document.getElementById('modalDeselectAll').addEventListener('click', function() {
            document.querySelectorAll('#modalCategorias input').forEach(function(cb){ cb.checked = false; });
        });
        document.getElementById('modalCancelar').addEventListener('click', function() {
            document.getElementById('modalExportar').classList.remove('open');
        });
        document.getElementById('modalExportar').addEventListener('click', function(e) {
            if (e.target === this) this.classList.remove('open');
        });
        var modalComentario = document.getElementById('modalComentario');
        var modalComentarioTexto = document.getElementById('modalComentarioTexto');
        document.addEventListener('click', function(e) {
            var btn = e.target.closest('.comentario-btn');
            if (!btn) return;
            var texto = btn.getAttribute('data-comentario') || '';
            modalComentarioTexto.textContent = texto;
            modalComentario.classList.add('open');
        });
        document.getElementById('modalComentarioCerrar').addEventListener('click', function() {
            modalComentario.classList.remove('open');
        });
        modalComentario.addEventListener('click', function(e) {
            if (e.target === this) this.classList.remove('open');
        });

        document.getElementById('modalExportarBtn').addEventListener('click', function() {
            var selected = [];
            document.querySelectorAll('#modalCategorias input[type="checkbox"]').forEach(function(cb) {
                if (cb.checked) selected.push(cb.value);
            });
            if (selected.length === 0) {
                alert('Selecciona al menos una categoría.');
                return;
            }
            document.querySelectorAll('.categoria-section').forEach(function(section) {
                var id = section.getAttribute('data-categoria-id');
                section.classList.toggle('pdf-exclude', selected.indexOf(id) === -1);
            });
            document.getElementById('modalExportar').classList.remove('open');
            void document.body.offsetHeight;
            setTimeout(function() { window.print(); }, 150);
        });

        window.addEventListener('afterprint', function() {
            document.querySelectorAll('.categoria-section').forEach(function(section) {
                section.classList.remove('pdf-exclude');
            });
        });

        document.querySelectorAll('.btn-top').forEach(function(btn) {
            btn.addEventListener('click', function() {
                window.scrollTo({ top: 0, behavior: 'smooth' });
            });
        });

        var buscador = document.getElementById('buscador');
        buscador.addEventListener('input', function() {
            var q = this.value.trim().toLowerCase();
            var sections = document.querySelectorAll('.categoria-section');
            var cards = document.querySelectorAll('.index-card');

            cards.forEach(function(c) { c.classList.remove('search-match', 'search-no-results'); });
            sections.forEach(function(s) { s.classList.remove('search-match', 'search-no-results'); });

            if (!q) {
                document.querySelectorAll('.search-hidden').forEach(function(tr){ tr.classList.remove('search-hidden'); });
                return;
            }

            sections.forEach(function(section) {
                var rows = section.querySelectorAll('tbody tr[data-numero], tbody tr[data-nombre]');
                var visible = 0;
                rows.forEach(function(tr) {
                    var num = (tr.getAttribute('data-numero') || '').toLowerCase();
                    var nom = (tr.getAttribute('data-nombre') || '').toLowerCase();
                    var match = num.indexOf(q) >= 0 || nom.indexOf(q) >= 0;
                    tr.classList.toggle('search-hidden', !match);
                    if (match) visible++;
                });
                var id = section.getAttribute('data-categoria-id');
                var card = document.querySelector('.index-card[data-categoria-id="' + id + '"]');
                if (visible > 0) {
                    section.classList.add('search-match');
                    if (card) card.classList.add('search-match');
                } else {
                    section.classList.add('search-no-results');
                    if (card) card.classList.add('search-no-results');
                }
            });
        });
    </script>
</body>
</html>
"""

    return html_content


def generate_html():
    categorias_data = {}
    for filename in os.listdir(FILES_DIR):
        if not filename.lower().endswith(".csv"):
            continue
        filepath = os.path.join(FILES_DIR, filename)
        if not os.path.isfile(filepath):
            continue

        headers, rows = parse_csv(filepath)
        headers, rows, comentarios = remove_clase_and_comentario(headers, rows)
        headers = [format_header(h) for h in headers]
        categoria, tipo, _ = parse_filename(filename)

        if categoria not in categorias_data:
            categorias_data[categoria] = {}

        categorias_data[categoria][tipo] = {
            "headers": headers,
            "rows": rows,
            "comentarios": comentarios,
        }

    categorias = []
    for categoria in sorted(categorias_data.keys(), key=get_category_sort_key):
        categorias.append(
            {
                "nombre": categoria,
                "section_id": slugify(categoria),
                "tablas": categorias_data[categoria],
            }
        )

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(build_html(categorias))

    print("Página generada:", OUTPUT_FILE)


if __name__ == "__main__":
    generate_html()
