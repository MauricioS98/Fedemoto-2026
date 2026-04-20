# -*- coding: utf-8 -*-
"""Regenera valida_i_velocidad_zarzal.html desde FILES EXPORTED_ZARZAL."""

import csv
import html
import re
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parent
CSV_DIR = ROOT / "FILES EXPORTED_ZARZAL"
OUT = ROOT / "valida_i_velocidad_zarzal.html"

ORDER = [
    ("50-cc", "50 CC", "50 CC"),
    ("ax-100-inicio", "Ax 100 Inicio", "AX 100 INICIO"),
    ("115-cc-infantil", "115 CC Infantil", "115 CC INFANTIL"),
    ("115-cc-inicio", "115 CC Inicio", "115 CC INICIO"),
    ("115-elite", "115 Elite", "115 ELITE"),
    ("115-cc-master", "115 CC Master", "115 CC MASTER"),
    ("150-cc-inicio", "150 CC Inicio", "150 CC INICIO"),
    ("150-cc-master", "150 CC Master", "150 CC MASTER"),
    ("150-cc", "150 CC", "150 CC"),
    ("200-cc-2t", "200 CC 2T", "200 CC 2T"),
    ("infantil", "Infantil", "INFANTIL"),
    ("pit-bike-infantil", "Pit Bike Infantil", "PIT BIKE INFANTIL"),
    ("pit-bike", "Pit Bike", "PIT BIKE"),
    ("supermoto", "Supermoto", "SUPERMOTO"),
]


def esc(s):
    return html.escape(str(s or ""), quote=True)


def normalize_text(value):
    s = str(value or "").strip()
    s = "".join(c for c in unicodedata.normalize("NFD", s) if unicodedata.category(c) != "Mn")
    s = re.sub(r"\s+", " ", s)
    return s.upper()


def normalize_header(h):
    return normalize_text(h).replace(" ", "")


def value_by_aliases(row, aliases):
    for k, v in row.items():
        nk = normalize_header(k)
        for a in aliases:
            if nk == a:
                return v
    return ""


def detect_delimiter(first_line):
    if not first_line:
        return ","
    return ";" if first_line.count(";") > first_line.count(",") else ","


def read_csv(path):
    raw = path.read_text(encoding="utf-8-sig")
    lines = raw.splitlines()
    delim = detect_delimiter(lines[0] if lines else "")
    reader = csv.DictReader(lines, delimiter=delim)
    return [{(k or "").strip(): (v or "").strip() for k, v in row.items()} for row in reader]


def parse_filename(filename):
    base = filename.replace(".csv", "").strip()
    base = re.sub(r"\s*-\s*resultados\s*$", "", base, flags=re.I).strip()
    parts = [p.strip() for p in re.split(r"\s+-\s+", base) if p.strip()]
    if len(parts) < 2:
        return normalize_text(base), "Final"
    categoria = normalize_text(" - ".join(parts[:-1]))
    last = normalize_text(parts[-1])
    if "CLASIFIC" in last:
        tipo = "Clasificatoria"
    elif "CARRERA 1" in last:
        tipo = "Carrera 1"
    elif "CARRERA 2" in last:
        tipo = "Carrera 2"
    elif "CARRERA" in last:
        tipo = "Carrera"
    elif "FINAL" in last:
        tipo = "Final"
    else:
        tipo = parts[-1].strip()
    return categoria, tipo


def parse_time_to_seconds(value):
    s = str(value or "").strip().replace(",", ".")
    if not s:
        return None
    if ":" in s:
        parts = s.split(":")
        try:
            if len(parts) == 2:
                return int(parts[0]) * 60 + float(parts[1])
            if len(parts) == 3:
                return int(parts[0]) * 3600 + int(parts[1]) * 60 + float(parts[2])
        except ValueError:
            return None
    try:
        return float(s)
    except ValueError:
        return None


def pos_class(pos):
    p = str(pos or "").strip()
    if p == "1":
        return "pos-1"
    if p == "2":
        return "pos-2"
    if p == "3":
        return "pos-3"
    return ""


def build_data():
    data = {}
    for path in sorted(CSV_DIR.glob("*.csv")):
        categoria, tipo = parse_filename(path.name)
        data.setdefault(categoria, {})[tipo] = read_csv(path)
    return data


def table_clasificatoria(rows):
    head = (
        "<thead><tr>"
        "<th>Pos.</th><th>N°</th><th>Nombre</th><th>Mejor tm</th><th>En vuelta</th>"
        "<th>Dif. resp. 1°</th><th>Dif. resp. anterior</th></tr></thead>"
    )
    body_rows = []
    for r in rows:
        pos = value_by_aliases(r, ["POS."])
        num = value_by_aliases(r, ["N°", "Nº", "N"])
        nom = value_by_aliases(r, ["NOMBRE"])
        mej = value_by_aliases(r, ["MEJORTM"])
        env = value_by_aliases(r, ["ENVUELTA"])
        d1 = value_by_aliases(r, ["DIF.RESP.1°", "DIF.RESP.1º"])
        da = value_by_aliases(r, ["DIF.RESP.ANTERIOR"])
        cls = pos_class(pos)
        tr_open = f'<tr class="{cls}" data-numero="{esc(num)}" data-nombre="{esc(nom)}">' if cls else f'<tr data-numero="{esc(num)}" data-nombre="{esc(nom)}">'
        body_rows.append(
            tr_open
            + f"<td>{esc(pos)}</td><td>{esc(num)}</td><td>{esc(nom)}</td><td>{esc(mej)}</td><td>{esc(env)}</td><td>{esc(d1)}</td><td>{esc(da)}</td></tr>"
        )
    return "<table>" + head + "<tbody>" + "".join(body_rows) + "</tbody></table>"


def table_carrera(rows):
    head = (
        "<thead><tr>"
        "<th>Pos.</th><th>N°</th><th>Nombre</th><th>Puntos</th><th>Dif. resp. 1°</th>"
        "<th>Mejor tm</th><th>Moto</th><th>Liga</th><th>Club</th><th>Vueltas</th></tr></thead>"
    )
    body_rows = []
    for r in rows:
        pos = value_by_aliases(r, ["POS."])
        num = value_by_aliases(r, ["N°", "Nº", "N"])
        nom = value_by_aliases(r, ["NOMBRE"])
        pts = value_by_aliases(r, ["PUNTOS"])
        d1 = value_by_aliases(r, ["DIF.RESP.1°", "DIF.RESP.1º"])
        mej = value_by_aliases(r, ["MEJORTM"])
        moto = value_by_aliases(r, ["MOTO"])
        liga = value_by_aliases(r, ["LIGA"])
        club = value_by_aliases(r, ["CLUB"])
        vu = value_by_aliases(r, ["VUELTAS"])
        cls = pos_class(pos)
        tr_open = f'<tr class="{cls}" data-numero="{esc(num)}" data-nombre="{esc(nom)}">' if cls else f'<tr data-numero="{esc(num)}" data-nombre="{esc(nom)}">'
        body_rows.append(
            tr_open
            + f"<td>{esc(pos)}</td><td>{esc(num)}</td><td>{esc(nom)}</td><td>{esc(pts)}</td><td>{esc(d1)}</td><td>{esc(mej)}</td>"
            + f"<td>{esc(moto)}</td><td>{esc(liga)}</td><td>{esc(club)}</td><td>{esc(vu)}</td></tr>"
        )
    return "<table>" + head + "<tbody>" + "".join(body_rows) + "</tbody></table>"


def table_supermoto_final(rows):
    head = (
        "<thead><tr>"
        "<th>Pos.</th><th>N°</th><th>Nombre</th><th>Total puntos</th><th>Dif. resp. 1°</th>"
        "<th>Moto</th><th>Liga</th><th>Club</th><th>C1</th><th>C2</th></tr></thead>"
    )
    body_rows = []
    for r in rows:
        pos = value_by_aliases(r, ["POS."])
        num = value_by_aliases(r, ["N°", "Nº", "N"])
        nom = value_by_aliases(r, ["NOMBRE"])
        total_pts = value_by_aliases(r, ["TOTALPUNTOS"])
        d1 = value_by_aliases(r, ["DIF.RESP.1°", "DIF.RESP.1º"])
        moto = value_by_aliases(r, ["MOTO"])
        liga = value_by_aliases(r, ["LIGA"])
        club = value_by_aliases(r, ["CLUB"])
        c1 = value_by_aliases(r, ["R1", "C1"])
        c2 = value_by_aliases(r, ["R2", "C2"])
        cls = pos_class(pos)
        tr_open = f'<tr class="{cls}" data-numero="{esc(num)}" data-nombre="{esc(nom)}">' if cls else f'<tr data-numero="{esc(num)}" data-nombre="{esc(nom)}">'
        body_rows.append(
            tr_open
            + f"<td>{esc(pos)}</td><td>{esc(num)}</td><td>{esc(nom)}</td><td>{esc(total_pts)}</td>"
            + f"<td>{esc(d1)}</td><td>{esc(moto)}</td><td>{esc(liga)}</td><td>{esc(club)}</td><td>{esc(c1)}</td><td>{esc(c2)}</td></tr>"
        )
    return "<table>" + head + "<tbody>" + "".join(body_rows) + "</tbody></table>"


def find_best_lap(rows):
    best = None
    for r in rows:
        t_raw = value_by_aliases(r, ["MEJORTM"])
        t = parse_time_to_seconds(t_raw)
        if t is None:
            continue
        if best is None or t < best["time"]:
            best = {
                "time": t,
                "time_txt": t_raw,
                "numero": value_by_aliases(r, ["N°", "Nº", "N"]),
                "nombre": value_by_aliases(r, ["NOMBRE"]),
            }
    return best


def times_summary(category_sessions):
    clasif_best = find_best_lap(category_sessions.get("Clasificatoria", []))
    carrera_candidates = []
    for label in ("Carrera", "Carrera 1", "Carrera 2"):
        best = find_best_lap(category_sessions.get(label, []))
        if best:
            carrera_candidates.append((label, best))
    carrera_best = sorted(carrera_candidates, key=lambda it: it[1]["time"])[0] if carrera_candidates else None

    lines = []
    if clasif_best:
        lines.append(
            "<p><strong>Mejor tiempo Clasificatoria:</strong> "
            f"{esc(clasif_best['time_txt'])} - N° {esc(clasif_best['numero'])} {esc(clasif_best['nombre'])}</p>"
        )
    if carrera_best:
        label, best = carrera_best
        lines.append(
            "<p><strong>Mejor tiempo Carrera:</strong> "
            f"{esc(best['time_txt'])} ({esc(label)}) - N° {esc(best['numero'])} {esc(best['nombre'])}</p>"
        )
    return (
        '<div class="times-summary"><h4>Mejores tiempos - Clasificatoria y carreras</h4>'
        f'<div class="times-summary-items">{"".join(lines)}</div></div>'
        if lines
        else ""
    )


def section_html(section_id, title, cat_key, all_data):
    sessions = all_data.get(cat_key, {})
    content = [times_summary(sessions)]

    def add_session_block(label, builder):
        rows = sessions.get(label, [])
        if not rows:
            return
        content.append('<div class="final-block">')
        content.append(f"<h3>{esc(label)}</h3>")
        content.append('<div class="table-wrapper">')
        content.append(builder(rows))
        content.append("</div></div>")

    if cat_key == "SUPERMOTO":
        add_session_block("Clasificatoria", table_clasificatoria)
        add_session_block("Final", table_supermoto_final)
        add_session_block("Carrera 1", table_carrera)
        add_session_block("Carrera 2", table_carrera)
    else:
        add_session_block("Clasificatoria", table_clasificatoria)
        add_session_block("Carrera", table_carrera)

    return f"""            <div class="categoria-section" id="{section_id}" data-categoria-id="{section_id}">
                <div class="categoria-header">
                    <h2>{esc(title)}</h2>
                    <button type="button" class="btn-top" title="Ir al inicio" aria-label="Ir al inicio">
                        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor"><path d="M12 4l-8 8h5v8h6v-8h5L12 4z"/></svg>
                    </button>
                </div>
                {''.join(content)}
            </div>
"""


def index_cards_html():
    return "\n".join(
        f'            <a href="#{section_id}" class="index-card" data-categoria-id="{section_id}">{esc(title)}</a>'
        for section_id, title, _cat in ORDER
    )


def modal_labels_html():
    return "\n".join(
        f'                <label class="modal-cat-item"><input type="checkbox" value="{section_id}" checked> {esc(title)}</label>'
        for section_id, title, _cat in ORDER
    )


def main():
    all_data = build_data()
    sections_html = "\n".join(
        section_html(section_id, title, cat, all_data) for section_id, title, cat in ORDER
    )

    page = f"""<!DOCTYPE html>
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
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: 'Inter', sans-serif; background: #f5f5f5; color: #000; line-height: 1.6; padding: 20px; padding-top: 120px; min-height: 100vh; }}
        .container {{ max-width: 1400px; margin: 0 auto; background: white; border-radius: 12px; box-shadow: 0 20px 60px rgba(0,0,0,0.3); overflow: hidden; margin-bottom: 40px; }}
        .container > header {{ background: linear-gradient(135deg, #123E92 0%, #0f3377 100%); color: white; padding: 40px; text-align: center; }}
        .container > header h1 {{ font-family: 'Bebas Neue', sans-serif; font-size: 2.2em; margin-bottom: 10px; letter-spacing: 2px; }}
        .container > header p {{ font-family: 'Roboto Condensed', sans-serif; font-size: 1.2em; opacity: 0.95; }}
        .toolbar {{ padding: 25px 40px; background: #f8f9fa; border-bottom: 1px solid #C0C0C0; }}
        .search-box {{ width: 100%; padding: 12px 20px; font-family: 'Inter', sans-serif; font-size: 1em; border: 2px solid #d1d5db; border-radius: 8px; }}
        .search-box:focus {{ outline: none; border-color: #123E92; box-shadow: 0 0 0 3px rgba(18, 62, 146, 0.2); }}
        .index-cards {{ display: flex; flex-wrap: wrap; gap: 12px; padding: 25px 40px; background: #f8f9fa; border-bottom: 1px solid #C0C0C0; }}
        .index-card {{ display: inline-block; padding: 10px 20px; background: white; color: #123E92; border: 2px solid #123E92; border-radius: 8px; font-family: 'Roboto Condensed', sans-serif; font-weight: 700; text-decoration: none; transition: all 0.2s ease; }}
        .index-card:hover {{ background: #123E92; color: white; transform: translateY(-2px); }}
        .index-card.search-match {{ background: #F7C31D; color: #123E92; border-color: #F7C31D; }}
        .index-card.search-no-results {{ display: none !important; }}
        .content-section {{ padding: 40px; }}
        .categoria-section {{ margin-bottom: 50px; scroll-margin-top: 120px; border: 2px solid #e0e0e0; border-radius: 12px; overflow: hidden; }}
        .categoria-section:last-child {{ margin-bottom: 0; }}
        .categoria-section.search-match {{ border-color: #F7C31D; box-shadow: 0 0 0 3px rgba(247, 195, 29, 0.4); }}
        .categoria-section.search-no-results {{ display: none !important; }}
        .categoria-header {{ background: linear-gradient(135deg, #123E92 0%, #0f3377 100%); color: white; padding: 25px 30px; display: flex; align-items: center; justify-content: space-between; gap: 15px; }}
        .categoria-header h2 {{ font-family: 'Bebas Neue', sans-serif; font-size: 2em; letter-spacing: 2px; }}
        .btn-top {{ display: inline-flex; align-items: center; justify-content: center; width: 40px; height: 40px; background: rgba(255,255,255,0.2); color: white; border: 2px solid rgba(255,255,255,0.6); border-radius: 8px; cursor: pointer; transition: all 0.2s ease; flex-shrink: 0; }}
        .btn-top:hover {{ background: #F7C31D; color: #123E92; border-color: #F7C31D; }}
        .btn-top svg {{ width: 20px; height: 20px; }}
        .times-summary {{ margin: 20px 30px; padding: 20px; background: #f8f9fa; border-radius: 8px; border-left: 5px solid #123E92; }}
        .times-summary h4 {{ font-family: 'Roboto Condensed', sans-serif; color: #123E92; margin-bottom: 15px; font-size: 1.1em; }}
        .times-summary-items p {{ margin-bottom: 10px; font-size: 1em; }}
        .times-summary-items p:last-child {{ margin-bottom: 0; }}
        .final-block {{ padding: 0 30px 30px; }}
        .final-block h3 {{ font-family: 'Bebas Neue', sans-serif; font-size: 1.8em; color: #123E92; margin: 25px 0 15px; padding-bottom: 8px; border-bottom: 3px solid #F7C31D; letter-spacing: 1px; }}
        .table-wrapper {{ overflow-x: auto; margin-bottom: 20px; border-radius: 8px; border: 1px solid #d1d5db; }}
        table {{ width: 100%; border-collapse: collapse; font-size: 0.9em; }}
        th, td {{ padding: 12px 15px; text-align: left; border-bottom: 1px solid #e0e0e0; }}
        th {{ background: #123E92; color: white; font-family: 'Roboto Condensed', sans-serif; font-weight: 700; }}
        tr:hover {{ background: #f8f9fa; }}
        tr.search-hidden {{ display: none !important; }}
        .pos-1 {{ background: rgba(247, 195, 29, 0.15) !important; }}
        .pos-2 {{ background: rgba(192, 192, 192, 0.2) !important; }}
        .pos-3 {{ background: rgba(139, 90, 43, 0.1) !important; }}
        .pdf-section {{ text-align: center; padding: 40px 20px; border-top: 1px solid #C0C0C0; background: #f8f9fa; }}
        .btn-pdf {{ display: inline-block; padding: 14px 32px; background: #123E92; color: white; border: none; border-radius: 8px; font-family: 'Roboto Condensed', sans-serif; font-size: 1.1em; font-weight: 700; cursor: pointer; transition: all 0.2s ease; }}
        .btn-pdf:hover {{ background: #0f3377; transform: translateY(-2px); }}
        .pdf-hint {{ margin-top: 12px; font-size: 0.9em; color: #666; }}
        .modal-overlay {{ display: none; position: fixed; top: 0; left: 0; right: 0; bottom: 0; background: rgba(0,0,0,0.5); z-index: 10000; align-items: center; justify-content: center; }}
        .modal-overlay.open {{ display: flex; }}
        .modal-box {{ background: white; border-radius: 12px; padding: 30px; max-width: 450px; width: 90%; max-height: 80vh; overflow-y: auto; box-shadow: 0 20px 60px rgba(0,0,0,0.3); }}
        .modal-box h3 {{ font-family: 'Bebas Neue', sans-serif; font-size: 1.6em; color: #123E92; margin-bottom: 20px; }}
        .modal-categorias {{ display: flex; flex-wrap: wrap; gap: 8px 16px; margin-bottom: 20px; }}
        .modal-cat-item {{ display: flex; align-items: center; gap: 8px; cursor: pointer; }}
        .modal-cat-item input {{ cursor: pointer; width: 18px; height: 18px; accent-color: #123E92; }}
        .modal-actions {{ display: flex; gap: 12px; flex-wrap: wrap; }}
        .modal-btn {{ padding: 10px 20px; border-radius: 8px; font-family: 'Roboto Condensed', sans-serif; font-weight: 700; cursor: pointer; border: none; font-size: 1em; transition: all 0.2s ease; }}
        .modal-btn-primary {{ background: #123E92; color: white; }}
        .modal-btn-primary:hover {{ background: #0f3377; }}
        .modal-btn-secondary {{ background: #e5e7eb; color: #374151; }}
        .modal-btn-secondary:hover {{ background: #d1d5db; }}
        .modal-btn-link {{ background: transparent; color: #123E92; text-decoration: underline; }}
        .modal-btn-link:hover {{ color: #0f3377; }}
        .categoria-section.pdf-exclude {{ display: none !important; }}
        footer {{ background: #f8f9fa; padding: 30px 40px; text-align: center; border-top: 1px solid #C0C0C0; color: #000; font-family: 'Inter', sans-serif; font-size: 0.9em; font-weight: 400; line-height: 1.8; }}
        footer .developer {{ font-family: 'Roboto Condensed', sans-serif; font-weight: 700; color: #123E92; }}
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
{index_cards_html()}
        </div>
        <div class="content-section">
{sections_html}
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
{modal_labels_html()}
            </div>
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
    <script src="../../load-menu.js"></script>
    <script>
        document.getElementById('descargarPDF').addEventListener('click', function() {{
            document.querySelectorAll('.search-no-results').forEach(function(el){{ el.classList.remove('search-no-results'); }});
            document.querySelectorAll('.search-hidden').forEach(function(el){{ el.classList.remove('search-hidden'); }});
            document.getElementById('modalExportar').classList.add('open');
        }});
        document.getElementById('modalSelectAll').addEventListener('click', function() {{ document.querySelectorAll('#modalCategorias input').forEach(function(cb){{ cb.checked = true; }}); }});
        document.getElementById('modalDeselectAll').addEventListener('click', function() {{ document.querySelectorAll('#modalCategorias input').forEach(function(cb){{ cb.checked = false; }}); }});
        document.getElementById('modalCancelar').addEventListener('click', function() {{ document.getElementById('modalExportar').classList.remove('open'); }});
        document.getElementById('modalExportar').addEventListener('click', function(e) {{ if (e.target === this) this.classList.remove('open'); }});
        document.getElementById('modalExportarBtn').addEventListener('click', function() {{
            var selected = [];
            document.querySelectorAll('#modalCategorias input[type="checkbox"]').forEach(function(cb) {{ if (cb.checked) selected.push(cb.value); }});
            if (selected.length === 0) {{ alert('Selecciona al menos una categoría.'); return; }}
            document.querySelectorAll('.categoria-section').forEach(function(section) {{
                section.classList.toggle('pdf-exclude', selected.indexOf(section.getAttribute('data-categoria-id')) === -1);
            }});
            document.getElementById('modalExportar').classList.remove('open');
            void document.body.offsetHeight;
            setTimeout(function() {{ window.print(); }}, 150);
        }});
        window.addEventListener('afterprint', function() {{
            document.querySelectorAll('.categoria-section').forEach(function(section) {{ section.classList.remove('pdf-exclude'); }});
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
                var card = document.querySelector('.index-card[data-categoria-id="' + id + '"]');
                if (visible > 0) {{ section.classList.add('search-match'); if (card) card.classList.add('search-match'); }}
                else {{ section.classList.add('search-no-results'); if (card) card.classList.add('search-no-results'); }}
            }});
        }});
    </script>
</body>
</html>"""
    OUT.write_text(page, encoding="utf-8")
    print("Wrote", OUT)


if __name__ == "__main__":
    main()
