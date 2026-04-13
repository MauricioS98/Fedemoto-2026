# -*- coding: utf-8 -*-
"""Genera valida_ii_enduro_pasca.html desde los CSV en FILES EXPORTED."""
import csv
import html
from pathlib import Path
from urllib.parse import quote

ROOT = Path(__file__).resolve().parent
CSV_DIR = ROOT / "FILES EXPORTED"
OUT = ROOT / "valida_ii_enduro_pasca.html"

# (id, titulo h2, orden en pagina)
ORDER = [
    ("infantil-enduro-1-final", "Infantil Enduro 1"),
    ("infantil-enduro-2-carrera", "Infantil Enduro 2"),
    ("infantil-enduro-3-carrera", "Infantil Enduro 3"),
    ("inicio-carrera", "Inicio"),
    ("juvenil-carrera", "Juvenil"),
    ("junior-carrera", "Junior"),
    ("junior-novatos-carrera", "Junior Novatos"),
    ("no-racer-carrera", "No Racer"),
    ("femenino-carrera", "Femenino"),
    ("enduro-1-carrera", "Enduro 1"),
    ("enduro-2-carrera", "Enduro 2"),
    ("enduro-3-carrera", "Enduro 3"),
    ("master-a-carrera", "Master A"),
    ("master-b-carrera", "Master B"),
]

PDFS = {
    "infantil-enduro-2-carrera": "INF E2 - CARRERA  - Laptimes.pdf",
    "infantil-enduro-3-carrera": "INF E3 - CARRERA - Laptimes.pdf",
    "inicio-carrera": "INICIO - CARRERA - Laptimes.pdf",
    "juvenil-carrera": "JUVENIL - CARRERA - Laptimes.pdf",
    "junior-carrera": "JUNIOR - CARRERA - Laptimes.pdf",
    "junior-novatos-carrera": "JUNIOR NOVATOS - CARRERA - Laptimes.pdf",
    "no-racer-carrera": "NO RACER - CARRERA - Laptimes.pdf",
    "femenino-carrera": "FEM - CARRERA - Laptimes.pdf",
    "enduro-1-carrera": "E1 - CARRERA - Laptimes.pdf",
    "enduro-2-carrera": "E2 - CARRERA - Laptimes.pdf",
    "enduro-3-carrera": "E3  - CARRERA - Laptimes.pdf",
    "master-a-carrera": "MAS A - CARRERA - Laptimes.pdf",
    "master-b-carrera": "MAS B - CARRERA - Laptimes.pdf",
}

CSV_FILES = {
    "infantil-enduro-2-carrera": "INF E2 - CARRERA  - Resultados.csv",
    "infantil-enduro-3-carrera": "inf e3 - carrera - resultados.csv",
    "inicio-carrera": "inicio  - carrera - resultados.csv",
    "juvenil-carrera": "juv - carrera - resultados.csv",
    "junior-carrera": "jun - carrera - resultados.csv",
    "junior-novatos-carrera": "jun nov - carrera - resultados.csv",
    "no-racer-carrera": "no racer - carrera - resultados.csv",
    "femenino-carrera": "fem - carrera - resultados.csv",
    "enduro-1-carrera": "e1 - carrera - resultados.csv",
    "enduro-2-carrera": "e2 - carrera - resultados.csv",
    "enduro-3-carrera": "e3  - carrera - resultados.csv",
    "master-a-carrera": "mas a - carrera - resultados.csv",
    "master-b-carrera": "mas b - carrera - resultados.csv",
}


def norm_key(k):
    return k.strip() if k else k


def read_csv_rows(name):
    path = CSV_DIR / name
    with path.open(encoding="utf-8-sig", newline="") as f:
        r = csv.DictReader(f)
        rows = []
        for row in r:
            rows.append(
                {norm_key(k): (v or "").strip() for k, v in row.items() if k is not None}
            )
        return rows


def esc(s):
    return html.escape(s, quote=True)


def pos_class(pos):
    if pos == "1":
        return "pos-1"
    if pos == "2":
        return "pos-2"
    if pos == "3":
        return "pos-3"
    return ""


def tr_carrera(row):
    pos = row.get("Pos.", "")
    num = row.get("N°", "")
    nom = row.get("Nombre", "")
    mej = row.get("Mejor Tm", "")
    env = row.get("En Vuelta", "")
    d1 = row.get("Dif. resp. 1°", "")
    pts = row.get("Puntos", "")
    tot = row.get("Total T°", "")
    vol = row.get("Vueltas", "")
    liga = row.get("LIGA", "")
    club = row.get("CLUB", "")
    moto = row.get("MOTO", "")
    com = row.get("Comentario", "")

    pc = pos_class(pos) if pos.isdigit() else ""
    trc = f'<tr class="{pc}" data-numero="{esc(num)}" data-nombre="{esc(nom)}">' if pc else f'<tr data-numero="{esc(num)}" data-nombre="{esc(nom)}">'

    pos_td = f"<td>{esc(pos)}</td>"
    if com:
        pos_td = (
            f'<td><span class="pos-cell">{esc(pos)}</span>'
            f'<button type="button" class="comentario-btn" data-comentario="{esc(com)}" aria-label="Ver comentario">i</button></td>'
        )

    inner = "".join(
        [
            pos_td,
            f"<td>{esc(num)}</td>",
            f"<td>{esc(nom)}</td>",
            f"<td>{esc(mej)}</td>",
            f"<td>{esc(env)}</td>",
            f"<td>{esc(d1)}</td>",
            f"<td>{esc(pts)}</td>",
            f"<td>{esc(tot)}</td>",
            f"<td>{esc(vol)}</td>",
            f"<td>{esc(liga)}</td>",
            f"<td>{esc(club)}</td>",
            f"<td>{esc(moto)}</td>",
        ]
    )
    return trc + inner + "</tr>"


def table_carrera(rows):
    thead = "<thead><tr><th>Pos.</th><th>N°</th><th>Nombre</th><th>Mejor tm</th><th>En vuelta</th><th>Dif. resp. 1°</th><th>Puntos</th><th>Total t°</th><th>Vueltas</th><th>Liga</th><th>Club</th><th>Moto</th></tr></thead>"
    body = "<tbody>" + "".join(tr_carrera(r) for r in rows) + "</tbody>"
    return f'<table>{thead}{body}</table>'


def tr_final_inf_e1(row):
    pos = row.get("Pos.", "")
    num = row.get("N°", "")
    nom = row.get("Nombre", "")
    tp = row.get("Total puntos", "")
    dr = row.get("Dif. resp. 1°", "")
    moto = row.get("MOTO", "")
    liga = row.get("LIGA", "")
    club = row.get("CLUB", "")
    c1 = row.get("C1", "")
    c2 = row.get("C2", "")

    pc = pos_class(pos) if pos.isdigit() else ""
    otr = f'<tr class="{pc}" data-numero="{esc(num)}" data-nombre="{esc(nom)}">' if pc else f'<tr data-numero="{esc(num)}" data-nombre="{esc(nom)}">'
    return (
        otr
        + f"<td>{esc(pos)}</td>"
        + f"<td>{esc(num)}</td>"
        + f"<td>{esc(nom)}</td>"
        + f"<td>{esc(tp)}</td>"
        + f"<td>{esc(dr)}</td>"
        + f"<td>{esc(moto)}</td>"
        + f"<td>{esc(liga)}</td>"
        + f"<td>{esc(club)}</td>"
        + f"<td>{esc(c1)}</td>"
        + f"<td>{esc(c2)}</td>"
        + "</tr>"
    )


def table_final_inf_e1(rows):
    thead = "<thead><tr><th>Pos.</th><th>N°</th><th>Nombre</th><th>Total puntos</th><th>Dif. resp. 1°</th><th>Moto</th><th>Liga</th><th>Club</th><th>C1</th><th>C2</th></tr></thead>"
    return f'<table>{thead}<tbody>{"".join(tr_final_inf_e1(r) for r in rows)}</tbody></table>'


def pdf_href(filename):
    return "Vuelta%20a%20vuelta/" + quote(filename, safe="")


def session_row(title, pdf_name):
    if not pdf_name:
        return f'<div class="session-title-row"><h3>{esc(title)}</h3></div>'
    return (
        f'<div class="session-title-row"><h3>{esc(title)}</h3>'
        f'<a class="btn-vuelta-a-vuelta" href="{pdf_href(pdf_name)}" target="_blank" rel="noopener noreferrer">Ver vuelta a vuelta</a></div>'
    )


def block_infantil_e1():
    final_rows = read_csv_rows("inf e1 - final - resultados.csv")
    c1_rows = read_csv_rows("infantil enduro 1 - carrera 1 - resultados.csv")
    c2_rows = read_csv_rows("infantil enduro 1 - carrera 2 - resultados.csv")

    parts = [
        '<div class="final-block">',
        '<div class="session-title-row"><h3>Final</h3></div>',
        '<div class="table-wrapper">',
        table_final_inf_e1(final_rows),
        "</div></div>",
        '<div class="desglose-block"><h3>Desglose por sesión</h3>',
        session_row("Carrera 1", "INF E1 - CARRERA 1 - Laptimes.pdf"),
        '<div class="table-wrapper">',
        table_carrera(c1_rows),
        "</div>",
        session_row("Carrera 2", "INF E1 - CARRERA 2 - Laptimes.pdf"),
        '<div class="table-wrapper">',
        table_carrera(c2_rows),
        "</div></div>",
    ]
    return "".join(parts)


def block_simple_carrera(cat_id):
    rows = read_csv_rows(CSV_FILES[cat_id])
    pdf = PDFS.get(cat_id)
    inner = (
        '<div class="final-block">'
        + session_row("Carrera", pdf)
        + '<div class="table-wrapper">'
        + table_carrera(rows)
        + "</div></div>"
    )
    return inner


def section(cat_id, title_h2):
    body = ""
    if cat_id == "infantil-enduro-1-final":
        body = block_infantil_e1()
    else:
        body = block_simple_carrera(cat_id)

    return f"""            <div class="categoria-section" id="{cat_id}" data-categoria-id="{cat_id}">
                <div class="categoria-header">
                    <h2>{esc(title_h2)}</h2>
                    <button type="button" class="btn-top" title="Ir al inicio" aria-label="Ir al inicio">
                        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor"><path d="M12 4l-8 8h5v8h6v-8h5L12 4z"/></svg>
                    </button>
                </div>
                {body}
            </div>
"""


def index_cards():
    lines = []
    for cid, title in ORDER:
        lines.append(
            f'            <a href="#{cid}" class="index-card" data-categoria-id="{cid}">{esc(title)}</a>'
        )
    return "\n".join(lines)


def modal_labels():
    lines = []
    for cid, title in ORDER:
        lines.append(
            f'                <label class="modal-cat-item"><input type="checkbox" value="{cid}" checked> {esc(title)}</label>'
        )
    return "\n".join(lines)


CSS_EXTRA = """
        .session-title-row { display: flex; flex-wrap: wrap; align-items: center; justify-content: space-between; gap: 12px; margin: 25px 0 15px; padding-bottom: 8px; border-bottom: 3px solid #F7C31D; }
        .session-title-row h3 { margin: 0; padding: 0; border: none; font-family: 'Bebas Neue', sans-serif; font-size: 1.8em; color: #123E92; letter-spacing: 1px; }
        .btn-vuelta-a-vuelta { display: inline-block; padding: 8px 16px; background: #123E92; color: white; text-decoration: none; border-radius: 8px; font-family: 'Roboto Condensed', sans-serif; font-weight: 700; font-size: 0.9em; white-space: nowrap; transition: all 0.2s ease; }
        .btn-vuelta-a-vuelta:hover { background: #0f3377; color: white; }
        .desglose-block .session-title-row { margin: 20px 0 12px; padding-bottom: 6px; border-bottom: 1px solid #C0C0C0; }
        .desglose-block .session-title-row h3 { font-family: 'Roboto Condensed', sans-serif; font-size: 1.2em; color: #666; font-weight: 700; }
        .final-block .session-title-row { margin: 20px 0 12px; }
        .final-block .session-title-row h3 { font-family: 'Bebas Neue', sans-serif; font-size: 1.8em; color: #123E92; letter-spacing: 1px; }
"""


def main():
    sections_html = "\n".join(section(cid, t) for cid, t in ORDER)

    page = f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>II Válida Nacional de Enduro - Pasca, Cundinamarca | FEDEMOTO</title>
    <link rel="icon" type="image/png" href="../../../fedemoto-logo.png">
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
        .nav-menu > li > a {{ display: block; padding: 12px 25px; color: white; text-decoration: none; font-family: 'Roboto Condensed', sans-serif; font-weight: 400; font-size: 1.1em; transition: all 0.2s ease; border-radius: 8px; }}
        .nav-menu > li > a:hover {{ background: rgba(255,255,255,0.1); transform: translateY(-2px); }}
        .dropdown {{ position: relative; }}
        .dropdown > a::after {{ content: ' ▼'; font-size: 0.8em; margin-left: 5px; }}
        .dropdown-menu {{ display: none; position: absolute; top: calc(100% + 5px); left: 0; background: white; min-width: 200px; box-shadow: 0 8px 16px rgba(0,0,0,0.2); border-radius: 8px; z-index: 10001; list-style: none; padding: 0; margin: 0; border: 1px solid #d1d5db; }}
        .nav-menu > .dropdown:hover > .dropdown-menu {{ display: block; }}
        .dropdown-menu a {{ display: block; padding: 12px 20px; color: #000; text-decoration: none; font-family: 'Inter', sans-serif; font-size: 1em; transition: all 0.2s ease; border-bottom: 1px solid #f0f0f0; }}
        .dropdown-menu a:hover {{ background: #f8f9fa; color: #123E92; }}
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
        .final-block {{ padding: 0 30px 30px; }}
        .final-block h3 {{ font-family: 'Bebas Neue', sans-serif; font-size: 1.8em; color: #123E92; margin: 25px 0 15px; padding-bottom: 8px; border-bottom: 3px solid #F7C31D; letter-spacing: 1px; }}
        .desglose-block {{ padding: 0 30px 30px; background: #fafafa; border-top: 1px solid #e0e0e0; }}
        .desglose-block h3 {{ font-family: 'Roboto Condensed', sans-serif; font-size: 1.2em; color: #666; margin: 20px 0 12px; padding-bottom: 6px; border-bottom: 1px solid #C0C0C0; font-weight: 700; }}
{CSS_EXTRA}
        .table-wrapper {{ overflow-x: auto; margin-bottom: 20px; border-radius: 8px; border: 1px solid #d1d5db; }}
        table {{ width: 100%; border-collapse: collapse; font-size: 0.9em; }}
        th, td {{ padding: 12px 15px; text-align: left; border-bottom: 1px solid #e0e0e0; }}
        th {{ background: #123E92; color: white; font-family: 'Roboto Condensed', sans-serif; font-weight: 700; }}
        tr:hover {{ background: #f8f9fa; }}
        tr.search-hidden {{ display: none !important; }}
        .pos-1 {{ background: rgba(247, 195, 29, 0.15) !important; }}
        .pos-2 {{ background: rgba(192, 192, 192, 0.2) !important; }}
        .pos-3 {{ background: rgba(139, 90, 43, 0.1) !important; }}
        .pos-cell {{ display: inline-block; margin-right: 4px; }}
        .comentario-btn {{ display: inline-flex; align-items: center; justify-content: center; width: 24px; height: 24px; margin-left: 6px; border: 1px solid #123E92; border-radius: 999px; background: #e8eef8; color: #123E92; font-size: 14px; font-weight: 700; cursor: pointer; vertical-align: middle; }}
        .comentario-btn:hover, .comentario-btn:focus {{ background: #123E92; color: white; outline: none; }}
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
        @media print {{ @page {{ size: A4 landscape; margin: 15mm; }} body {{ padding: 0 !important; padding-top: 0 !important; background: white !important; }} #menu-container, .fixed-header, .pdf-section, .toolbar, .index-cards, .btn-top, footer {{ display: none !important; }} .container {{ box-shadow: none !important; max-width: 100% !important; }} .categoria-section {{ break-before: page; page-break-before: always; }} .categoria-section:first-child {{ break-before: auto; page-break-before: auto; }} .modal-overlay {{ display: none !important; }} .container > header, .categoria-header, th {{ -webkit-print-color-adjust: exact; print-color-adjust: exact; }} table {{ font-size: 0.75em; }} }}
    </style>
</head>
<body>
    <div id="menu-container"></div>
    <div id="contenido-exportar" class="container">
        <header>
            <h1>II Válida Nacional de Enduro</h1>
            <p>Pasca, Cundinamarca - Resultados por categoría</p>
        </header>
        <div class="toolbar">
            <input type="text" id="buscador" class="search-box" placeholder="Buscar por nombre o N° del piloto..." />
        </div>
        <div class="index-cards">
{index_cards()}
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
{modal_labels()}
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
        document.getElementById('descargarPDF').addEventListener('click', function() {{
            document.querySelectorAll('.search-no-results').forEach(function(el){{ el.classList.remove('search-no-results'); }});
            document.querySelectorAll('.search-hidden').forEach(function(el){{ el.classList.remove('search-hidden'); }});
            document.getElementById('modalExportar').classList.add('open');
        }});
        document.getElementById('modalSelectAll').addEventListener('click', function() {{ document.querySelectorAll('#modalCategorias input').forEach(function(cb){{ cb.checked = true; }}); }});
        document.getElementById('modalDeselectAll').addEventListener('click', function() {{ document.querySelectorAll('#modalCategorias input').forEach(function(cb){{ cb.checked = false; }}); }});
        document.getElementById('modalCancelar').addEventListener('click', function() {{ document.getElementById('modalExportar').classList.remove('open'); }});
        document.getElementById('modalExportar').addEventListener('click', function(e) {{ if (e.target === this) this.classList.remove('open'); }});
        var modalComentario = document.getElementById('modalComentario');
        var modalComentarioTexto = document.getElementById('modalComentarioTexto');
        document.addEventListener('click', function(e) {{
            var btn = e.target.closest('.comentario-btn');
            if (!btn) return;
            modalComentarioTexto.textContent = btn.getAttribute('data-comentario') || '';
            modalComentario.classList.add('open');
        }});
        document.getElementById('modalComentarioCerrar').addEventListener('click', function() {{
            modalComentario.classList.remove('open');
        }});
        modalComentario.addEventListener('click', function(e) {{
            if (e.target === this) this.classList.remove('open');
        }});
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
</html>
"""
    OUT.write_text(page, encoding="utf-8")
    print("Wrote", OUT)


if __name__ == "__main__":
    main()
