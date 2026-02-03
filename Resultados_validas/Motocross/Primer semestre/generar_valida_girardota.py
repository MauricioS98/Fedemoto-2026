"""
Script para generar la página HTML de resultados de la I Válida Nacional de Motocross - Girardota
"""

import csv
import os
import html
import re

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
FILES_DIR = os.path.join(SCRIPT_DIR, "FILES EXPORTED")
OUTPUT_FILE = os.path.join(SCRIPT_DIR, "valida_i_mx_girardota.html")

def format_header(header):
    if not header:
        return ""
    h = str(header).strip()
    return h[0].upper() + h[1:].lower() if h else ""

def parse_filename(filename):
    name = filename.replace('.csv', '').strip()
    name = re.sub(r'\s*-\s*resultados\s*$', '', name, flags=re.I).strip()
    parts = [p.strip() for p in re.split(r'\s+-\s+', name, flags=re.I) if p.strip()]
    if len(parts) < 2:
        return (format_categoria_name(parts[0] if parts else name), "Final", 0)
    tipo_str = parts[-1].lower()
    if 'final' in tipo_str:
        tipo, sort_key = 'Final', 0
    elif 'clasificatoria' in tipo_str or 'clasificacion' in tipo_str:
        tipo, sort_key = 'Clasificatoria', 1
    elif '1 carrera' in tipo_str:
        tipo, sort_key = 'Carrera 1', 2
    elif '2 carrera' in tipo_str:
        tipo, sort_key = 'Carrera 2', 3
    else:
        tipo, sort_key = format_categoria_name(parts[-1]), 0
    categoria = format_categoria_name(' - '.join(parts[:-1]))
    return (categoria, tipo, sort_key)

def format_categoria_name(name):
    if not name:
        return name
    parts = re.split(r'[\s\-]+', name)
    result = []
    for p in parts:
        if p:
            if re.match(r'^\d+cc$', p, re.I):
                result.append(p.lower())
            elif p.upper() in ('A', 'B', 'MX', 'MX2'):
                result.append(p.upper())
            else:
                result.append(p[0].upper() + p[1:].lower() if len(p) > 1 else p.upper())
    return ' '.join(result)

def get_category_sort_key(categoria):
    order = {'50cc': 0, '65cc': 1, '85cc mini': 2, '85cc junior': 3, '125cc': 4,
             'femenina a': 5, 'femenina b': 6, 'femenina a y b': 7,
             'inicio': 8, 'mx master': 9, 'mx preexpertos': 10, 'mx pro': 11, 'mx2': 12}
    return (order.get(categoria.lower(), 99), categoria)

def parse_csv(filepath):
    with open(filepath, 'r', encoding='utf-8-sig') as f:
        rows = list(csv.reader(f))
    return (rows[0], rows[1:]) if rows else ([], [])

def remove_clase_column(headers, rows):
    idx = next((i for i, h in enumerate(headers) if str(h).strip().lower() == 'clase'), None)
    if idx is None:
        return headers, rows
    return ([h for i, h in enumerate(headers) if i != idx],
            [[c for i, c in enumerate(row) if i != idx] for row in rows])

def find_mejor_tm_index(headers):
    for i, h in enumerate(headers):
        hl = str(h).strip().lower()
        if 'mejor' in hl and ('tm' in hl or 'tiempo' in hl):
            return i
    return -1

def time_to_seconds(t):
    """Convierte '1:33.843' a segundos. Retorna None si no es válido."""
    if not t or not str(t).strip():
        return None
    t = str(t).strip()
    if re.match(r'^\d+:\d{2}\.?\d*$', t):  # M:SS.mmm
        parts = t.split(':')
        return int(parts[0]) * 60 + float(parts[1])
    return None

def format_time(seconds):
    if seconds is None:
        return '-'
    m = int(seconds // 60)
    s = seconds % 60
    return f"{m}:{s:06.3f}" if s >= 10 else f"{m}:0{s:.3f}"

def escape_html(text):
    return html.escape(str(text)) if text else ""

def slugify(text):
    s = re.sub(r'[^\w\s-]', '', str(text).lower())
    return re.sub(r'[\s_]+', '-', s).strip('-')

def get_pilotos_from_final(final_rows):
    """Extrae (numero, nombre) de las filas del Final, en orden."""
    pilots = []
    for row in final_rows:
        if len(row) >= 3 and row[1].strip():  # N° y Nombre
            pilots.append((str(row[1]).strip(), str(row[2]).strip()))
    return pilots

def get_mejor_tm_by_numero(rows, num_idx, mejor_tm_idx, nombre_idx=2):
    """Retorna dict numero -> (mejor_tm_string, nombre)"""
    if mejor_tm_idx < 0 or num_idx < 0:
        return {}
    d = {}
    for row in rows:
        if len(row) > max(num_idx, mejor_tm_idx):
            num = str(row[num_idx]).strip()
            tm = str(row[mejor_tm_idx]).strip()
            nombre = str(row[nombre_idx]).strip() if len(row) > nombre_idx else ""
            if num and tm and time_to_seconds(tm) is not None:
                d[num] = (tm, nombre)
    return d

def get_mejor_tm_absoluto(rows, num_idx, mejor_tm_idx, nombre_idx=2):
    """Retorna (numero, nombre, tiempo_str) del mejor tiempo en las filas, o None."""
    if mejor_tm_idx < 0 or num_idx < 0:
        return None
    best = None
    for row in rows:
        if len(row) > max(num_idx, mejor_tm_idx):
            num = str(row[num_idx]).strip()
            tm = str(row[mejor_tm_idx]).strip()
            nombre = str(row[nombre_idx]).strip() if len(row) > nombre_idx else ""
            s = time_to_seconds(tm)
            if num and s is not None and (best is None or s < best[2]):
                best = (num, nombre, s, tm)
    return (best[0], best[1], best[3]) if best else None

def get_mejor_tm_carreras(c1_data, c2_data, num_idx=1, nombre_idx=2):
    """Retorna (numero, nombre, tiempo_str, "Carrera 1"|"Carrera 2") del mejor tiempo entre C1 y C2."""
    best = None
    for nombre_carrera, data in [("Carrera 1", c1_data), ("Carrera 2", c2_data)]:
        if not data:
            continue
        headers, rows = data
        idx = find_mejor_tm_index(headers)
        if idx < 0:
            continue
        for row in rows:
            if len(row) > max(num_idx, idx):
                num = str(row[num_idx]).strip()
                tm = str(row[idx]).strip()
                nombre = str(row[nombre_idx]).strip() if len(row) > nombre_idx else ""
                s = time_to_seconds(tm)
                if num and s is not None and (best is None or s < best[2]):
                    best = (num, nombre, s, tm, nombre_carrera)
    return (best[0], best[1], best[3], best[4]) if best else None

def generate_html():
    categorias_data = {}
    for filename in os.listdir(FILES_DIR):
        if not filename.lower().endswith('.csv'):
            continue
        filepath = os.path.join(FILES_DIR, filename)
        if not os.path.isfile(filepath):
            continue
        headers, rows = parse_csv(filepath)
        headers, rows = remove_clase_column(headers, rows)
        headers = [format_header(h) for h in headers]
        categoria, tipo, sort_key = parse_filename(filename)
        if categoria not in categorias_data:
            categorias_data[categoria] = []
        categorias_data[categoria].append((tipo, sort_key, headers, rows))
    
    for cat in categorias_data:
        categorias_data[cat].sort(key=lambda x: (x[1], x[0]))
    
    sorted_categorias = sorted(categorias_data.keys(), key=get_category_sort_key)
    
    categorias_para_html = []
    for categoria in sorted_categorias:
        items = categorias_data[categoria]
        tablas = [(tipo, headers, rows) for tipo, _, headers, rows in items]
        first_tipo = tablas[0][0] if tablas else "Final"
        section_id = slugify(f"{categoria} {first_tipo}")
        categorias_para_html.append((categoria, section_id, tablas))
    
    html_content = '''<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>I Válida Nacional de Motocross - Girardota, Antioquia | FEDEMOTO</title>
    <link rel="icon" type="image/png" href="../../../../fedemoto-logo.png">
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Roboto+Condensed:wght@300;400;700&family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Inter', sans-serif; background: #f5f5f5; color: #000; line-height: 1.6; padding: 20px; padding-top: 120px; min-height: 100vh; }
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
        .times-summary table { width: 100%; border-collapse: collapse; font-size: 0.9em; }
        .times-summary th, .times-summary td { padding: 8px 12px; text-align: left; border-bottom: 1px solid #e0e0e0; }
        .times-summary th { background: #123E92; color: white; font-family: 'Roboto Condensed', sans-serif; }
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
        @media print {
            @page { size: A4 landscape; margin: 15mm; }
            body { padding: 0 !important; padding-top: 0 !important; background: white !important; }
            #menu-container, .fixed-header, .pdf-section, .toolbar, .index-cards, .btn-top { display: none !important; }
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
            <h1>I Válida Nacional de Motocross</h1>
            <p>Girardota, Antioquia - Resultados por categoría</p>
        </header>
        <div class="toolbar">
            <input type="text" id="buscador" class="search-box" placeholder="Buscar por nombre o N° del piloto..." />
        </div>
        <div class="index-cards">
'''
    
    for cat, section_id, _ in categorias_para_html:
        html_content += f'            <a href="#{section_id}" class="index-card" data-categoria-id="{section_id}">{escape_html(cat)}</a>\n'
    
    html_content += '        </div>\n        <div class="content-section">\n'
    
    for categoria, section_id, tablas in categorias_para_html:
        final_data = None
        clasif_data = None
        c1_data = None
        c2_data = None
        for tipo, headers, rows in tablas:
            if tipo == 'Final':
                final_data = (headers, rows)
            elif tipo == 'Clasificatoria':
                clasif_data = (headers, rows)
            elif tipo == 'Carrera 1':
                c1_data = (headers, rows)
            elif tipo == 'Carrera 2':
                c2_data = (headers, rows)
        
        # Si no hay Final (ej. 50cc), la primera tabla es la principal
        if not final_data and tablas:
            final_data = (tablas[0][1], tablas[0][2])
        
        html_content += f'''
            <div class="categoria-section" id="{section_id}" data-categoria-id="{section_id}">
                <div class="categoria-header">
                    <h2>{escape_html(categoria)}</h2>
                    <button type="button" class="btn-top" title="Ir al inicio" aria-label="Ir al inicio">
                        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor"><path d="M12 4l-8 8h5v8h6v-8h5L12 4z"/></svg>
                    </button>
                </div>'''
        
        # Resumen de tiempos: solo el mejor en clasificatoria y el mejor en carreras (indicando en cuál)
        if final_data and (clasif_data or c1_data or c2_data):
            best_clasif = get_mejor_tm_absoluto(clasif_data[1], 1, find_mejor_tm_index(clasif_data[0]), 2) if clasif_data else None
            best_carreras = get_mejor_tm_carreras(c1_data, c2_data) if (c1_data or c2_data) else None
            if best_clasif or best_carreras:
                html_content += '''
                <div class="times-summary">
                    <h4>Mejores tiempos - Clasificatoria y carreras</h4>
                    <div class="times-summary-items">'''
                if best_clasif:
                    num, nombre, tm = best_clasif
                    html_content += f'''
                        <p><strong>Mejor tiempo Clasificatoria:</strong> {escape_html(tm)} — N° {escape_html(num)} {escape_html(nombre)}</p>'''
                if best_carreras:
                    num, nombre, tm, carrera = best_carreras
                    html_content += f'''
                        <p><strong>Mejor tiempo Carrera:</strong> {escape_html(tm)} ({escape_html(carrera)}) — N° {escape_html(num)} {escape_html(nombre)}</p>'''
                html_content += '</div></div>'
        
        # Bloque principal (Final o primera tabla)
        main_tipo = 'Final' if final_data and any(t == 'Final' for t, _, _ in tablas) else (tablas[0][0] if tablas else 'Resultados')
        main_table = final_data if final_data else (tablas[0][1], tablas[0][2]) if tablas else (None, None)
        if main_table:
            headers, rows = main_table
            html_content += '\n                <div class="final-block">'
            html_content += f'''
                <h3>{escape_html(main_tipo)}</h3>
                <div class="table-wrapper">
                    <table>
                        <thead><tr>'''
            for h in headers:
                html_content += f'<th>{escape_html(h)}</th>'
            html_content += '</tr></thead><tbody>'
            for row in rows:
                pos_class = ''
                if row and str(row[0]).strip() == '1':
                    pos_class = ' class="pos-1"'
                elif row and str(row[0]).strip() == '2':
                    pos_class = ' class="pos-2"'
                elif row and str(row[0]).strip() == '3':
                    pos_class = ' class="pos-3"'
                search_attrs = f' data-numero="{escape_html(row[1] if len(row) > 1 else "")}" data-nombre="{escape_html(row[2] if len(row) > 2 else "")}"'
                html_content += f'<tr{pos_class}{search_attrs}>'
                for cell in row:
                    html_content += f'<td>{escape_html(cell)}</td>'
                html_content += '</tr>'
            html_content += '</tbody></table></div></div>'
        
        # Bloque Desglose: solo si hay más de una tabla (evitar repetir info en 50cc, etc.)
        main_tipo_for_desglose = main_tipo
        desglose = [(t, h, r) for t, h, r in tablas if t != main_tipo_for_desglose]
        if len(tablas) > 1 and desglose:
            html_content += '\n                <div class="desglose-block">'
            html_content += '\n                    <h3>Desglose por sesión</h3>'
            for tipo, headers, rows in desglose:
                html_content += f'''
                    <h3>{escape_html(tipo)}</h3>
                    <div class="table-wrapper">
                        <table>
                            <thead><tr>'''
                for h in headers:
                    html_content += f'<th>{escape_html(h)}</th>'
                html_content += '</tr></thead><tbody>'
                for row in rows:
                    pos_class = ''
                    if row and str(row[0]).strip() == '1':
                        pos_class = ' class="pos-1"'
                    elif row and str(row[0]).strip() == '2':
                        pos_class = ' class="pos-2"'
                    elif row and str(row[0]).strip() == '3':
                        pos_class = ' class="pos-3"'
                    search_attrs = f' data-numero="{escape_html(row[1] if len(row) > 1 else "")}" data-nombre="{escape_html(row[2] if len(row) > 2 else "")}"'
                    html_content += f'<tr{pos_class}{search_attrs}>'
                    for cell in row:
                        html_content += f'<td>{escape_html(cell)}</td>'
                    html_content += '</tr>'
                html_content += '</tbody></table></div>'
            html_content += '</div>'
        
        html_content += '\n            </div>'
    
    html_content += '''
        </div>
        <div class="pdf-section">
            <button id="descargarPDF" class="btn-pdf">Exportar a PDF</button>
            <p class="pdf-hint">En el dialogo de impresion, elige "Guardar como PDF" o "Microsoft Print to PDF" como destino.</p>
        </div>
    </div>
    <div id="modalExportar" class="modal-overlay">
        <div class="modal-box">
            <h3>Exportar a PDF</h3>
            <p style="margin-bottom: 16px; font-size: 0.95em; color: #374151;">Selecciona las categorías que deseas incluir:</p>
            <div class="modal-categorias" id="modalCategorias">
'''
    
    for cat, section_id, _ in categorias_para_html:
        html_content += f'                <label class="modal-cat-item"><input type="checkbox" value="{section_id}" checked> {escape_html(cat)}</label>\n'
    
    html_content += '''            </div>
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
    <script src="../../../../load-menu.js"></script>
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
        document.getElementById('modalExportarBtn').addEventListener('click', function() {
            var selected = [];
            document.querySelectorAll('#modalCategorias input:checked').forEach(function(cb){ selected.push(cb.value); });
            if (selected.length === 0) {
                alert('Selecciona al menos una categoria.');
                return;
            }
            document.querySelectorAll('.categoria-section').forEach(function(section) {
                var id = section.getAttribute('data-categoria-id');
                section.classList.toggle('pdf-exclude', selected.indexOf(id) === -1);
            });
            document.getElementById('modalExportar').classList.remove('open');
            window.print();
        });
        window.addEventListener('afterprint', function() {
            document.querySelectorAll('.categoria-section').forEach(function(section) {
                section.classList.remove('pdf-exclude');
            });
        });
        document.querySelectorAll('.btn-top').forEach(function(btn) {
            btn.addEventListener('click', function() { window.scrollTo({ top: 0, behavior: 'smooth' }); });
        });
        var buscador = document.getElementById('buscador');
        buscador.addEventListener('input', function() {
            var q = this.value.trim().toLowerCase();
            var sections = document.querySelectorAll('.categoria-section');
            var cards = document.querySelectorAll('.index-card');
            cards.forEach(function(c){ c.classList.remove('search-match', 'search-no-results'); });
            sections.forEach(function(s){ s.classList.remove('search-match', 'search-no-results'); });
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
'''
    
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print("Pagina generada: " + OUTPUT_FILE)

if __name__ == '__main__':
    generate_html()
