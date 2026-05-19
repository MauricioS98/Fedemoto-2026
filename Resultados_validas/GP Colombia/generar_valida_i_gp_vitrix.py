"""
Genera la página HTML de la I Válida GP Colombia - Gran Premio Vitrix.
Incluye Clasificación final, práctica clasificatoria, carreras y finales.
Femenina: clasificatoria conjunta; carrera en Expertas y Novatas.
Super Stock y X-Bikes se publican en subcategorías por columna Clase.
"""

import csv
import os
import html
import re
import sys
import unicodedata

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
FILES_DIR = os.path.join(SCRIPT_DIR, "FILES EXPORTED_Gran Premio Vitrix")
OUTPUT_FILE = os.path.join(SCRIPT_DIR, "valida_i_gp_colombia_vitrix.html")
VUELTA_DIR = os.path.join(SCRIPT_DIR, "VUELTA A VUELTA_Gran Premio Vitrix")
VUELTA_FOLDER_URL = "VUELTA A VUELTA_Gran Premio Vitrix"

_RV_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, ".."))
if _RV_ROOT not in sys.path:
    sys.path.insert(0, _RV_ROOT)
import vuelta_a_vuelta as vv

_MX_DIR = os.path.join(_RV_ROOT, "Motocross", "Primer semestre")
if _MX_DIR not in sys.path:
    sys.path.insert(0, _MX_DIR)
import generar_valida_girardota as gmx

VUELTA_A_VUELTA_FOLDER = VUELTA_FOLDER_URL
VUELTA_A_VUELTA_MAP = None

FEMENINA = "Femenina"
FEMENINA_EXPERTAS = "Femenina Expertas"
FEMENINA_NOVATAS = "Femenina Novatas"
SUPER_STOCK_600 = "Super Stock 600"
SUPER_STOCK_1000 = "Super Stock 1000"
X_BIKES_A = "X-Bikes A"
X_BIKES_B = "X-Bikes B"
COMBINED_SUPER_STOCK = "super stock 600 y 1000"
COMBINED_X_BIKES = "x-bikes a y b"

# Orden de sesiones en tablas y desglose (menor = primero).
SESSION_SORT_KEY = {
    "Final": 0,
    "Clasificación final": 1,
    "Clasificatoria": 2,
    "Carrera 1": 3,
    "Carrera 2": 4,
    "Carrera": 5,
}


def _fold_accents(text):
    return "".join(
        c
        for c in unicodedata.normalize("NFD", str(text))
        if unicodedata.category(c) != "Mn"
    )


def canonical_session_tipo(tipo):
    """Unifica variantes (tildes, mayúsculas) al nombre usado en SESSION_SORT_KEY."""
    folded = _fold_accents(tipo).lower().strip()
    if "clasificacion final" in folded or "clasificatoria final" in folded:
        return "Clasificación final"
    if folded == "final" or (folded.endswith("final") and "clasific" not in folded):
        return "Final"
    if "practica" in folded or "primera practica" in folded:
        return "Clasificatoria"
    if re.search(r"carrera\s*1", folded) or re.search(r"^1\s*carrera", folded):
        return "Carrera 1"
    if re.search(r"carrera\s*2", folded) or re.search(r"^2\s*carrera", folded):
        return "Carrera 2"
    if "carrera" in folded:
        return "Carrera"
    return str(tipo).strip()


def format_header(header):
    if not header:
        return ""
    h = str(header).strip()
    return h[0].upper() + h[1:].lower() if h else ""

def parse_filename(filename):
    name = filename.replace(".csv", "").strip()
    name = re.sub(r"\s*-\s*resultados\s*$", "", name, flags=re.I).strip()
    parts = [p.strip() for p in re.split(r"\s+-\s+", name, flags=re.I) if p.strip()]
    if len(parts) < 2:
        return (format_categoria_name(parts[0] if parts else name), "Final", 0)
    rest = _fold_accents(" - ".join(parts[1:])).lower()
    tipo_str = _fold_accents(parts[-1]).lower()
    if "clasificacion final" in rest or "clasificatoria final" in rest:
        tipo = "Clasificación final"
    elif tipo_str == "final" or (tipo_str.endswith("final") and "clasific" not in tipo_str):
        tipo = "Final"
    elif "practica" in tipo_str or "primera practica" in tipo_str:
        tipo = "Clasificatoria"
    elif re.search(r"carrera\s*1", tipo_str) or re.search(r"^1\s*carrera", tipo_str):
        tipo = "Carrera 1"
    elif re.search(r"carrera\s*2", tipo_str) or re.search(r"^2\s*carrera", tipo_str):
        tipo = "Carrera 2"
    elif "carrera" in tipo_str:
        tipo = "Carrera"
    else:
        tipo = canonical_session_tipo(format_categoria_name(parts[-1]))
    tipo = canonical_session_tipo(tipo)
    sort_key = SESSION_SORT_KEY.get(tipo, 99)
    categoria = format_categoria_name(" - ".join(parts[:-1]))
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
            elif re.match(r"^\d+t$", p, re.I):
                result.append(p.upper())
            elif p.upper() in ("CRS", "TVS", "GSC", "A", "B", "Y"):
                result.append(p.upper())
            elif p.upper() == "METZELER":
                result.append("Metzeler")
            else:
                result.append(p[0].upper() + p[1:].lower() if len(p) > 1 else p.upper())
    return " ".join(result)


def get_category_sort_key(categoria):
    c = categoria.lower()
    order = {
        "115cc elite": 0,
        "115cc infantil": 1,
        "115cc inicio": 2,
        "115cc master": 3,
        "150cc": 10,
        "150cc inicio": 11,
        "150cc master": 12,
        "200cc 2t": 20,
        "220cc 4t": 21,
        "minibike 190": 30,
        "minimotard": 31,
        "x-bikes a": 32,
        "x-bikes b": 33,
        "yamaha r15": 34,
        "suzuki gsc r s 150": 35,
        "street race 250": 40,
        "crs expertos": 50,
        "crs novatos": 51,
        "femenina": 59,
        "femenina expertas": 60,
        "femenina novatas": 61,
        "cuatrimotard": 70,
        "super bike": 80,
        "super sport": 81,
        "super stock 600": 82,
        "super stock 1000": 83,
        "supermoto expertos - metzeler": 90,
        "supermoto novatos - metzeler": 91,
    }
    return (order.get(c, 99), categoria)


def normalize_numero(num):
    return re.sub(r"\s+", "", str(num or "").strip()).upper()


def femenina_bucket_from_clase(clase_val):
    c = str(clase_val or "").upper().replace(" ", "")
    if "NOV" in c:
        return "novatas"
    if "EXP" in c:
        return "expertas"
    return None


def super_stock_bucket_from_clase(clase_val):
    c = _fold_accents(clase_val).lower()
    if "1000" in c:
        return "1000"
    if "600" in c:
        return "600"
    return None


def xbikes_bucket_from_clase(clase_val):
    c = _fold_accents(clase_val).lower()
    if re.search(r"x[- ]?bikes?\s+b\b", c):
        return "b"
    if re.search(r"x[- ]?bikes?\s+a\b", c):
        return "a"
    return None


def _is_combined_super_stock(categoria):
    return "super stock" in categoria.lower()


def _is_combined_xbikes(categoria):
    c = categoria.lower()
    return "x-bikes" in c or "x bikes" in c


def build_femenina_numero_bucket_map(carrera_headers, carrera_rows):
    idx_clase = gmx.find_col_index(carrera_headers, ("clase",))
    idx_num = gmx.find_col_index(carrera_headers, ("n°", "nº", "numero", "n"))
    mapping = {}
    if idx_num < 0:
        return mapping
    for row in carrera_rows:
        need = [i for i in (idx_num, idx_clase) if i is not None and i >= 0]
        if not need or len(row) <= max(need):
            continue
        num = normalize_numero(row[idx_num])
        if not num:
            continue
        bucket = femenina_bucket_from_clase(row[idx_clase]) if idx_clase >= 0 else None
        if bucket:
            mapping[num] = bucket
    return mapping


def renumber_positions_rows(rows, idx_pos=0):
    if idx_pos < 0:
        return rows
    pos = 0
    out = []
    for row in rows:
        r = list(row)
        p = str(r[idx_pos]).strip().upper() if idx_pos < len(r) else ""
        if p in ("NT", "EX", "DNF"):
            out.append(r)
            continue
        pos += 1
        r[idx_pos] = str(pos)
        out.append(r)
    return out


def filter_by_clase_bucket(
    headers, rows, comentarios, bucket, bucket_from_clase, numero_bucket_map=None, use_clase_column=True
):
    idx_num = gmx.find_col_index(headers, ("n°", "nº", "numero", "n"))
    idx_clase = gmx.find_col_index(headers, ("clase",))
    idx_pos = gmx.find_col_index(headers, ("pos.", "pos"))
    filtered_rows = []
    filtered_com = []
    for i, row in enumerate(rows):
        if idx_num < 0 or len(row) <= idx_num:
            continue
        num = normalize_numero(row[idx_num])
        if use_clase_column and idx_clase >= 0 and idx_clase < len(row):
            b = bucket_from_clase(row[idx_clase])
        else:
            b = (numero_bucket_map or {}).get(num)
        if b != bucket:
            continue
        filtered_rows.append(list(row))
        filtered_com.append(comentarios[i] if i < len(comentarios) else "")
    h_out, r_out = remove_clase_column(headers, filtered_rows)
    r_out = renumber_positions_rows(r_out, idx_pos if idx_pos >= 0 else 0)
    h_out = [format_header(h) for h in h_out]
    return h_out, r_out, filtered_com


def filter_femenina_session(headers, rows, comentarios, bucket, numero_bucket_map, use_clase_column):
    return filter_by_clase_bucket(
        headers,
        rows,
        comentarios,
        bucket,
        femenina_bucket_from_clase,
        numero_bucket_map,
        use_clase_column,
    )


def _append_clase_split_categories(categorias_data, pending, bucket_fn, display_buckets):
    for display_name, bucket in display_buckets:
        sessions = []
        for tipo, sort_key, headers_raw, rows_raw, headers_nc, rows_nc, comentarios in pending:
            # Clase solo existe en CSV crudo (se quita al limpiar comentarios).
            h, r, c = filter_by_clase_bucket(
                headers_raw,
                rows_raw,
                comentarios,
                bucket,
                bucket_fn,
                numero_bucket_map=None,
                use_clase_column=True,
            )
            if r:
                sessions.append((tipo, sort_key, h, r, c))
        if sessions:
            categorias_data[display_name] = sessions


def load_categorias_data():
    categorias_data = {}
    femenina_pending = []
    super_stock_pending = []
    xbikes_pending = []

    for filename in os.listdir(FILES_DIR):
        if not filename.lower().endswith(".csv"):
            continue
        filepath = os.path.join(FILES_DIR, filename)
        if not os.path.isfile(filepath):
            continue
        headers_raw, rows_raw = parse_csv(filepath)
        categoria, tipo, sort_key = parse_filename(filename)
        tipo = canonical_session_tipo(tipo)
        sort_key = SESSION_SORT_KEY.get(tipo, 99)
        if categoria.lower() == "femenina":
            headers_nc, rows_nc, comentarios = remove_comentario_column_and_collect(
                headers_raw, rows_raw
            )
            femenina_pending.append(
                (tipo, sort_key, headers_raw, rows_raw, headers_nc, rows_nc, comentarios)
            )
            continue
        if _is_combined_super_stock(categoria):
            headers_nc, rows_nc, comentarios = remove_comentario_column_and_collect(
                headers_raw, rows_raw
            )
            super_stock_pending.append(
                (tipo, sort_key, headers_raw, rows_raw, headers_nc, rows_nc, comentarios)
            )
            continue
        if _is_combined_xbikes(categoria):
            headers_nc, rows_nc, comentarios = remove_comentario_column_and_collect(
                headers_raw, rows_raw
            )
            xbikes_pending.append(
                (tipo, sort_key, headers_raw, rows_raw, headers_nc, rows_nc, comentarios)
            )
            continue
        headers, rows, comentarios = remove_comentario_column_and_collect(headers_raw, rows_raw)
        if tipo == "Final":
            headers, rows = gmx.remove_fnrh_column(headers, rows)
        headers = [format_header(h) for h in headers]
        categorias_data.setdefault(categoria, []).append(
            (tipo, sort_key, headers, rows, comentarios)
        )

    if femenina_pending:
        clasif_item = next((x for x in femenina_pending if x[0] == "Clasificatoria"), None)
        if clasif_item:
            tipo, sort_key, headers_raw, rows_raw, _, _, comentarios = clasif_item
            headers, rows, comentarios = remove_comentario_column_and_collect(
                headers_raw, rows_raw
            )
            headers, rows = remove_clase_column(headers, rows)
            headers = [format_header(h) for h in headers]
            if rows:
                categorias_data[FEMENINA] = [(tipo, sort_key, headers, rows, comentarios)]

        carrera_item = next((x for x in femenina_pending if x[0] == "Carrera"), None)
        numero_map = {}
        if carrera_item:
            numero_map = build_femenina_numero_bucket_map(carrera_item[2], carrera_item[3])
        for display_name, bucket in ((FEMENINA_EXPERTAS, "expertas"), (FEMENINA_NOVATAS, "novatas")):
            sessions = []
            for tipo, sort_key, headers_raw, rows_raw, headers_nc, rows_nc, comentarios in femenina_pending:
                if tipo == "Clasificatoria":
                    continue
                if tipo == "Carrera":
                    h, r, c = filter_femenina_session(
                        headers_raw, rows_raw, comentarios, bucket, numero_map, True
                    )
                else:
                    h, r, c = filter_femenina_session(
                        headers_nc, rows_nc, comentarios, bucket, numero_map, False
                    )
                if r:
                    sessions.append((tipo, sort_key, h, r, c))
            if sessions:
                categorias_data[display_name] = sessions

    if super_stock_pending:
        _append_clase_split_categories(
            categorias_data,
            super_stock_pending,
            super_stock_bucket_from_clase,
            ((SUPER_STOCK_600, "600"), (SUPER_STOCK_1000, "1000")),
        )

    if xbikes_pending:
        _append_clase_split_categories(
            categorias_data,
            xbikes_pending,
            xbikes_bucket_from_clase,
            ((X_BIKES_A, "a"), (X_BIKES_B, "b")),
        )

    for cat in categorias_data:
        categorias_data[cat].sort(key=lambda x: (SESSION_SORT_KEY.get(x[0], 99), x[0]))
    return categorias_data


def csv_delimiter(first_line):
    if not first_line:
        return ","
    return ";" if first_line.count(";") > first_line.count(",") else ","


def _expand_merged_headers(parts):
    out = []
    for p in parts:
        p = str(p).strip()
        if not p:
            continue
        pl = p.lower()
        if "nombre" in pl and re.search(r"n\s*[°º]", pl):
            out.extend(["N°", "Nombre"])
        else:
            out.append(p)
    return out


def _normalize_csv_table(headers, rows):
    headers = _expand_merged_headers(headers)
    if not rows:
        return headers, rows
    width = len(headers)
    norm_rows = []
    for row in rows:
        r = list(row)
        if len(r) < width:
            r.extend([""] * (width - len(r)))
        elif len(r) > width:
            r = r[:width]
        norm_rows.append(r)
    return headers, norm_rows


def parse_csv(filepath):
    with open(filepath, "r", encoding="utf-8-sig") as f:
        raw = f.read()
    if not raw.strip():
        return [], []
    lines = raw.splitlines()
    delim = csv_delimiter(lines[0])
    rows = list(csv.reader(lines, delimiter=delim))
    if not rows:
        return [], []
    headers, body = _normalize_csv_table(rows[0], rows[1:])
    return headers, body


def sort_tablas(tablas):
    return sorted(tablas, key=lambda t: (SESSION_SORT_KEY.get(t[0], 99), t[0]))


def pick_main_session(tablas, final_data, clasif_final_data, clasif_data, carrera_data, c1_data, c2_data):
    """Tabla principal: Final > Clasificación final > Clasificatoria (si hay carrera) > Carrera."""
    if final_data and any(t[0] == "Final" for t in tablas):
        return "Final", final_data
    if clasif_final_data:
        return "Clasificación final", clasif_final_data
    if clasif_data and (carrera_data or c1_data or c2_data):
        return "Clasificatoria", clasif_data
    if carrera_data:
        return "Carrera", carrera_data
    if tablas:
        t = tablas[0]
        return t[0], (t[1], t[2], t[3])
    return None, None

def remove_clase_column(headers, rows):
    idx = next((i for i, h in enumerate(headers) if str(h).strip().lower() == 'clase'), None)
    if idx is None:
        return headers, rows
    return ([h for i, h in enumerate(headers) if i != idx],
            [[c for i, c in enumerate(row) if i != idx] for row in rows])

def remove_comentario_column_and_collect(headers, rows):
    """Quita columna Comentario y retorna (headers, rows, comentarios)."""
    headers, rows = remove_clase_column(headers, rows)
    idx = next((i for i, h in enumerate(headers) if str(h).strip().lower() == 'comentario'), None)
    if idx is None:
        return headers, rows, [''] * len(rows)
    comentarios = [str(row[idx]).strip() if len(row) > idx else '' for row in rows]
    new_headers = [h for i, h in enumerate(headers) if i != idx]
    new_rows = [[c for i, c in enumerate(row) if i != idx] for row in rows]
    return new_headers, new_rows, comentarios

def find_mejor_tm_index(headers):
    fallback = -1
    for i, h in enumerate(headers):
        hl = str(h).strip().lower().replace("°", " ").replace("º", " ")
        if "mejor" not in hl:
            continue
        if "tm" in hl or "tiempo" in hl:
            return i
        if "total" in hl:
            fallback = i
    return fallback

def time_to_seconds(t):
    if not t or not str(t).strip():
        return None
    t = str(t).strip()
    if re.match(r'^\d+:\d{2}\.?\d*$', t):
        parts = t.split(':')
        return int(parts[0]) * 60 + float(parts[1])
    return None

def escape_html(text):
    return html.escape(str(text)) if text else ""

def tipo_gp(last_part, format_categoria_name_fn):
    s = str(last_part).lower().strip()
    if "clasificacion final" in s or "clasificatoria final" in s:
        return "Clasificación final"
    if s == "final" or (s.endswith("final") and "clasific" not in s):
        return "Final"
    if "practica" in s or "práctica" in s or "primera practica" in s:
        return "Clasificatoria"
    if re.search(r"carrera\s*1", s) or re.search(r"^1\s*carrera", s):
        return "Carrera 1"
    if re.search(r"carrera\s*2", s) or re.search(r"^2\s*carrera", s):
        return "Carrera 2"
    if "carrera" in s:
        return "Carrera"
    return format_categoria_name_fn(last_part)


def build_vuelta_a_vuelta_map(pdf_dir):
    m = vv.build_laptimes_pdf_map(
        pdf_dir,
        format_categoria_name,
        lambda p: tipo_gp(p, format_categoria_name),
    )
    fn = m.get(("femenina", "Carrera"))
    if fn:
        m[(FEMENINA_EXPERTAS.lower(), "Carrera")] = fn
        m[(FEMENINA_NOVATAS.lower(), "Carrera")] = fn
    for combined, subs in (
        (COMBINED_SUPER_STOCK, (SUPER_STOCK_600, SUPER_STOCK_1000)),
        (COMBINED_X_BIKES, (X_BIKES_A, X_BIKES_B)),
    ):
        for ses in ("Clasificatoria", "Carrera"):
            fn = m.get((combined, ses))
            if fn:
                for sub in subs:
                    m[(sub.lower(), ses)] = fn
    return m

def session_title_block(categoria, tipo_sesion):
    return vv.session_title_block(
        categoria,
        tipo_sesion,
        escape_html,
        VUELTA_A_VUELTA_MAP,
        VUELTA_A_VUELTA_FOLDER,
    )

def slugify(text):
    s = re.sub(r'[^\w\s-]', '', str(text).lower())
    return re.sub(r'[\s_]+', '-', s).strip('-')

def get_mejor_tm_absoluto(rows, num_idx, mejor_tm_idx, nombre_idx=2):
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

def render_row(row, comentario, col_count, search_attrs):
    """Renderiza una fila de tabla, con botón de comentario en Pos si hay texto."""
    pos_val = str(row[0]).strip() if row else ''
    pos_class = ''
    if pos_val == '1':
        pos_class = ' class="pos-1"'
    elif pos_val == '2':
        pos_class = ' class="pos-2"'
    elif pos_val == '3':
        pos_class = ' class="pos-3"'
    html_parts = [f'<tr{pos_class}{search_attrs}>']
    for i, cell in enumerate(row):
        if i == 0:
            pos_content = escape_html(cell)
            if comentario:
                html_parts.append(
                    f'<td><span class="pos-cell">{pos_content}</span>'
                    f'<button type="button" class="comentario-btn" data-comentario="{escape_html(comentario)}" '
                    f'aria-label="Ver comentario">i</button></td>'
                )
            else:
                html_parts.append(f'<td>{pos_content}</td>')
        else:
            html_parts.append(f'<td>{escape_html(cell)}</td>')
    html_parts.append('</tr>')
    return ''.join(html_parts)

def generate_html():
    global VUELTA_A_VUELTA_MAP
    VUELTA_A_VUELTA_MAP = build_vuelta_a_vuelta_map(VUELTA_DIR)

    categorias_data = load_categorias_data()
    sorted_categorias = sorted(categorias_data.keys(), key=get_category_sort_key)
    
    categorias_para_html = []
    for categoria in sorted_categorias:
        items = categorias_data[categoria]
        tablas = sort_tablas(
            [(tipo, headers, rows, comentarios) for tipo, _, headers, rows, comentarios in items]
        )
        fd = cf = cl = cr = c1 = c2 = None
        for tipo, headers, rows, comentarios in tablas:
            if tipo == "Final":
                fd = (headers, rows, comentarios)
            elif tipo == "Clasificación final":
                cf = (headers, rows, comentarios)
            elif tipo == "Clasificatoria":
                cl = (headers, rows, comentarios)
            elif tipo == "Carrera":
                cr = (headers, rows, comentarios)
            elif tipo == "Carrera 1":
                c1 = (headers, rows)
            elif tipo == "Carrera 2":
                c2 = (headers, rows)
        main_tipo, _ = pick_main_session(tablas, fd, cf, cl, cr, c1, c2)
        section_id = slugify(f"{categoria} {main_tipo}" if main_tipo else f"{categoria} final")
        categorias_para_html.append((categoria, section_id, tablas))
    
    html_content = '''<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>I Válida GP Colombia - Gran Premio Vitrix | FEDEMOTO</title>
    <link rel="icon" type="image/png" href="../../../fedemoto-logo.png">
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
''' + vv.CSS_PLACEHOLDER + r'''
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
            <h1>I Válida GP Colombia</h1>
            <p>Gran Premio Vitrix — Resultados por categoría</p>
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
        clasif_final_data = None
        c1_data = None
        c2_data = None
        carrera_data = None
        for item in tablas:
            tipo, headers, rows, comentarios = item[0], item[1], item[2], item[3]
            if tipo == "Final":
                final_data = (headers, rows, comentarios)
            elif tipo == "Clasificación final":
                clasif_final_data = (headers, rows, comentarios)
            elif tipo == "Clasificatoria":
                clasif_data = (headers, rows, comentarios)
            elif tipo == "Carrera 1":
                c1_data = (headers, rows)
            elif tipo == "Carrera 2":
                c2_data = (headers, rows)
            elif tipo == "Carrera":
                carrera_data = (headers, rows, comentarios)

        html_content += f'''
            <div class="categoria-section" id="{section_id}" data-categoria-id="{section_id}">
                <div class="categoria-header">
                    <h2>{escape_html(categoria)}</h2>
                    <button type="button" class="btn-top" title="Ir al inicio" aria-label="Ir al inicio">
                        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor"><path d="M12 4l-8 8h5v8h6v-8h5L12 4z"/></svg>
                    </button>
                </div>'''
        
        if clasif_data:
            clasif_src = clasif_data
            clasif_label = "Mejor tiempo Clasificatoria:"
        elif clasif_final_data:
            clasif_src = clasif_final_data
            clasif_label = "Mejor tiempo Clasificación final:"
        else:
            clasif_src = None
            clasif_label = "Mejor tiempo Clasificatoria:"

        if clasif_src or c1_data or c2_data or carrera_data:
            best_clasif = None
            if clasif_src:
                ch, cr = clasif_src[0], clasif_src[1]
                tm_idx = find_mejor_tm_index(ch)
                if tm_idx >= 0:
                    best_clasif = get_mejor_tm_absoluto(cr, 1, tm_idx, 2)
            best_carreras = get_mejor_tm_carreras(c1_data, c2_data) if (c1_data or c2_data) else None
            if not best_carreras and carrera_data:
                ch, cr = carrera_data[0], carrera_data[1]
                tm_idx = find_mejor_tm_index(ch)
                best_one = get_mejor_tm_absoluto(cr, 1, tm_idx, 2) if tm_idx >= 0 else None
                if best_one:
                    best_carreras = (best_one[0], best_one[1], best_one[2], "Carrera")
            if best_clasif or best_carreras:
                html_content += '''
                <div class="times-summary">
                    <h4>Mejores tiempos - Clasificatoria y carreras</h4>
                    <div class="times-summary-items">'''
                if best_clasif:
                    num, nombre, tm = best_clasif
                    html_content += f'''
                        <p><strong>{clasif_label}</strong> {escape_html(tm)} — N° {escape_html(num)} {escape_html(nombre)}</p>'''
                if best_carreras:
                    num, nombre, tm, carrera = best_carreras
                    html_content += f'''
                        <p><strong>Mejor tiempo Carrera:</strong> {escape_html(tm)} ({escape_html(carrera)}) — N° {escape_html(num)} {escape_html(nombre)}</p>'''
                html_content += '</div></div>'
        
        main_tipo, main_table = pick_main_session(
            tablas, final_data, clasif_final_data, clasif_data, carrera_data, c1_data, c2_data
        )
        if main_table:
            headers, rows, comentarios = main_table
            html_content += '\n                <div class="final-block">'
            html_content += session_title_block(categoria, main_tipo)
            html_content += '''
                <div class="table-wrapper">
                    <table>
                        <thead><tr>'''
            for h in headers:
                html_content += f'<th>{escape_html(h)}</th>'
            html_content += '</tr></thead><tbody>'
            for i, row in enumerate(rows):
                com = comentarios[i] if i < len(comentarios) else ''
                search_attrs = f' data-numero="{escape_html(row[1] if len(row) > 1 else "")}" data-nombre="{escape_html(row[2] if len(row) > 2 else "")}"'
                html_content += render_row(row, com, len(headers), search_attrs)
            html_content += '</tbody></table></div></div>'
        
        desglose = sort_tablas(
            [(t[0], t[1], t[2], t[3]) for t in tablas if t[0] != main_tipo]
        )
        if len(tablas) > 1 and desglose:
            html_content += '\n                <div class="desglose-block">'
            html_content += '\n                    <h3>Desglose por sesión</h3>'
            for tipo, headers, rows, comentarios in desglose:
                html_content += session_title_block(categoria, tipo)
                html_content += '''
                    <div class="table-wrapper">
                        <table>
                            <thead><tr>'''
                for h in headers:
                    html_content += f'<th>{escape_html(h)}</th>'
                html_content += '</tr></thead><tbody>'
                for i, row in enumerate(rows):
                    com = comentarios[i] if i < len(comentarios) else ''
                    search_attrs = f' data-numero="{escape_html(row[1] if len(row) > 1 else "")}" data-nombre="{escape_html(row[2] if len(row) > 2 else "")}"'
                    html_content += render_row(row, com, len(headers), search_attrs)
                html_content += '</tbody></table></div>'
            html_content += '</div>'
        
        html_content += '\n            </div>'
    
    html_content += '''
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
    <div id="modalComentario" class="modal-overlay">
        <div class="modal-box">
            <h3>Comentario</h3>
            <p id="modalComentarioTexto" style="margin-bottom: 20px; font-size: 1em; color: #111827; white-space: pre-wrap;"></p>
            <div class="modal-actions">
                <button type="button" class="modal-btn modal-btn-primary" id="modalComentarioCerrar">Cerrar</button>
            </div>
        </div>
    </div>
    <script src="../../../load-menu.js"></script>
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
            modalComentarioTexto.textContent = btn.getAttribute('data-comentario') || '';
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

    html_content = vv.inject_vuelta_css(
        html_content,
        bool(VUELTA_A_VUELTA_MAP and VUELTA_A_VUELTA_FOLDER),
    )

    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print("Página generada: " + OUTPUT_FILE)


def _norm_cell_header(h):
    return re.sub(r"\s+", "", str(h or "").strip().lower())


def _find_stats_indexes(headers):
    idx = {
        "numero": None,
        "nombre": None,
        "liga": None,
        "club": None,
        "moto": None,
        "puntos": None,
        "pos": None,
    }
    for i, h in enumerate(headers):
        hl = _norm_cell_header(h)
        if hl in ("n°", "nº", "numero", "n"):
            idx["numero"] = i
        elif "nombre" in hl:
            idx["nombre"] = i
        elif "liga" in hl:
            idx["liga"] = i
        elif "club" in hl:
            idx["club"] = i
        elif hl == "moto":
            idx["moto"] = i
        elif hl in ("totalpuntos", "puntostotales", "puntos"):
            if idx["puntos"] is None or hl == "totalpuntos":
                idx["puntos"] = i
        elif hl in ("pos.", "pos"):
            idx["pos"] = i
    return idx


def _session_pick_rank(tipo):
    return SESSION_SORT_KEY.get(canonical_session_tipo(tipo), 9)


def _pick_main_session_items(items):
    sorted_items = sorted(items, key=lambda x: (_session_pick_rank(x[0]), x[1]))
    for tipo, _, headers, rows, _ in sorted_items:
        idx = _find_stats_indexes(headers)
        if idx["puntos"] is not None and idx["numero"] is not None:
            return headers, rows, "puntos"
        if canonical_session_tipo(tipo) == "Clasificación final" and idx["pos"] is not None and idx["numero"] is not None:
            return headers, rows, "position"
    for _, _, headers, rows, _ in sorted_items:
        idx = _find_stats_indexes(headers)
        if idx["puntos"] is not None and idx["numero"] is not None:
            return headers, rows, "puntos"
    return None, None, None


def _parse_pos_int(val):
    s = str(val or "").strip().upper()
    if s in ("NT", "EX", "DNF"):
        return 0
    m = re.search(r"\d+", s)
    return int(m.group(0)) if m else 0


def _puntos_fedemoto_pos(pos):
    if pos <= 0:
        return 0.0
    tabla = {
        1: 15, 2: 13, 3: 11, 4: 10, 5: 9, 6: 8, 7: 7, 8: 6, 9: 5, 10: 4, 11: 3, 12: 2,
    }
    if pos in tabla:
        return float(tabla[pos])
    if 13 <= pos <= 15:
        return 1.0
    return 0.0


def _parse_puntos_cell(val):
    s = str(val or "").strip().replace(",", ".")
    m = re.search(r"-?\d+(\.\d+)?", s)
    return float(m.group(0)) if m else 0.0


def export_valida_general_rows(files_dir=None):
    """Filas por categoría (display) para informes y resultados generales."""
    global FILES_DIR
    prev = FILES_DIR
    if files_dir:
        FILES_DIR = files_dir
    try:
        categorias = load_categorias_data()
    finally:
        FILES_DIR = prev

    out = {}
    for categoria, items in categorias.items():
        headers, rows, mode = _pick_main_session_items(items)
        if not headers:
            continue
        idx = _find_stats_indexes(headers)
        if idx["numero"] is None:
            continue
        cat_rows = []
        for row in rows:
            if len(row) <= idx["numero"]:
                continue
            numero = str(row[idx["numero"]]).strip()
            if not numero:
                continue
            if mode == "puntos":
                if idx["puntos"] is None or len(row) <= idx["puntos"]:
                    continue
                pts = _parse_puntos_cell(row[idx["puntos"]])
            else:
                pos_val = row[idx["pos"]] if idx["pos"] is not None and idx["pos"] < len(row) else ""
                pts = _puntos_fedemoto_pos(_parse_pos_int(pos_val))
            cat_rows.append({
                "numero": numero,
                "nombre": (
                    str(row[idx["nombre"]]).strip()
                    if idx["nombre"] is not None and idx["nombre"] < len(row)
                    else ""
                ),
                "liga": (
                    str(row[idx["liga"]]).strip()
                    if idx["liga"] is not None and idx["liga"] < len(row)
                    else ""
                ),
                "club": (
                    str(row[idx["club"]]).strip()
                    if idx["club"] is not None and idx["club"] < len(row)
                    else ""
                ),
                "moto": (
                    str(row[idx["moto"]]).strip()
                    if idx["moto"] is not None and idx["moto"] < len(row)
                    else ""
                ),
                "clase": "",
                "puntos": pts,
            })
        if cat_rows:
            out[categoria] = cat_rows
    return out


if __name__ == '__main__':
    generate_html()
