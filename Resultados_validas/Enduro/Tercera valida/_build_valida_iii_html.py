# -*- coding: utf-8 -*-
"""Genera valida_iii_enduro_san_jeronimo.html desde los CSV en FILES EXPORTED."""
import csv
import html
from pathlib import Path
from urllib.parse import quote

ROOT = Path(__file__).resolve().parent
CSV_DIR = ROOT / "FILES EXPORTED"
OUT = ROOT / "valida_iii_enduro_san_jeronimo.html"
PDF_FOLDER = "Vuelta a vueltla"

ORDER = [
    ("scratch", "Scratch"),
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
    "infantil-enduro-2-carrera": "Infantil enduro 2 - CARRERA  - Laptimes.pdf",
    "infantil-enduro-3-carrera": "Infantil enduro 3 - CARRERA - Laptimes.pdf",
    "inicio-carrera": "INICIO - CARRERA - Laptimes.pdf",
    "juvenil-carrera": "Juvenil - CARRERA - Laptimes.pdf",
    "junior-carrera": "Junior - CARRERA - Laptimes.pdf",
    "junior-novatos-carrera": "Junior novatos - CARRERA - Laptimes.pdf",
    "no-racer-carrera": "NO RACER - CARRERA - Laptimes.pdf",
    "femenino-carrera": "Femenina - CARRERA - Laptimes.pdf",
    "enduro-1-carrera": "Enduro 1 - CARRERA - Laptimes.pdf",
    "enduro-2-carrera": "Enduro 2  - CARRERA - Laptimes.pdf",
    "enduro-3-carrera": "Enduro 3  - CARRERA - Laptimes.pdf",
    "master-a-carrera": "MASTER A - CARRERA - Laptimes.pdf",
    "master-b-carrera": "MASTER B - CARRERA - Laptimes.pdf",
}

INF_E1_PDFS = {
    "Carrera 1": "Infantil enduro 1 - CARRERA 1 - Laptimes.pdf",
    "Carrera 2": "Infantil enduro 1 - CARRERA 2 - Laptimes.pdf",
}

CSV_FILES = {
    "infantil-enduro-2-carrera": "infantil enduro 2 - carrera  - resultados.csv",
    "infantil-enduro-3-carrera": "infantil enduro 3 - carrera - resultados.csv",
    "inicio-carrera": "inicio - carrera - resultados.csv",
    "juvenil-carrera": "juvenil - carrera - resultados.csv",
    "junior-carrera": "junior - carrera - resultados.csv",
    "junior-novatos-carrera": "junior novatos - carrera - resultados.csv",
    "no-racer-carrera": "no racer - carrera - resultados.csv",
    "femenino-carrera": "femenina - carrera - resultados.csv",
    "enduro-1-carrera": "enduro 1 - carrera - resultados.csv",
    "enduro-2-carrera": "enduro 2  - carrera - resultados.csv",
    "enduro-3-carrera": "enduro 3  - carrera - resultados.csv",
    "master-a-carrera": "master a - carrera - resultados.csv",
    "master-b-carrera": "master b - carrera - resultados.csv",
}

INF_E1_CARRERAS = {
    "Carrera 1": "infantil enduro 1 - carrera 1 - resultados.csv",
    "Carrera 2": "infantil enduro 1 - carrera 2 - resultados.csv",
}


def norm_key(k):
    return k.strip() if k else k


def row_val(row, *keys):
    for k in keys:
        if k in row and row[k]:
            return row[k]
    return ""


def read_csv_rows(name):
    path = CSV_DIR / name
    if not path.is_file():
        return None
    sample = path.read_text(encoding="utf-8-sig")
    first = sample.splitlines()[0] if sample else ""
    delim = ";" if first.count(";") > first.count(",") else ","
    with path.open(encoding="utf-8-sig", newline="") as f:
        r = csv.DictReader(f, delimiter=delim)
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
    c1 = row_val(row, "C1", "C1 ")
    c2 = row_val(row, "C2", "C2 ")

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
    return quote(PDF_FOLDER, safe="") + "/" + quote(filename, safe="")


def session_row(title, pdf_name):
    if not pdf_name:
        return f'<div class="session-title-row"><h3>{esc(title)}</h3></div>'
    return (
        f'<div class="session-title-row"><h3>{esc(title)}</h3>'
        f'<a class="btn-vuelta-a-vuelta" href="{pdf_href(pdf_name)}" target="_blank" rel="noopener noreferrer">Ver vuelta a vuelta</a></div>'
    )


def read_scratch_raw():
    path = CSV_DIR / "Scratch - Resultados.csv"
    if not path.is_file():
        return []
    with path.open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f, delimiter=";"))


def tr_scratch(row):
    pos = (row.get("Pos.") or row.get("Pos") or "").strip()
    num = (row.get("N°") or row.get("Nº") or row.get("No") or "").strip()
    nom = (row.get("Nombre") or "").strip()
    liga = (row.get("LIGA") or row.get("Liga") or "").strip()
    moto = (row.get("MOTO") or row.get("Moto") or "").strip()
    clase = (row.get("Clase") or "").strip()
    vueltas = (row.get("Vueltas") or "").strip()
    tot = (row.get("Total T°") or "").strip()
    if not tot:
        for k in row:
            if "total" in k.lower() and "t" in k.lower():
                tot = (row.get(k) or "").strip()
                break
    t_aj = (row.get("Tiempo ajustado") or "").strip()
    if not t_aj:
        for k in row:
            if "tiempo" in k.lower() and "ajust" in k.lower():
                t_aj = (row.get(k) or "").strip()
                break

    pc = pos_class(pos) if pos.isdigit() else ""
    otr = f'<tr class="{pc}" data-numero="{esc(num)}" data-nombre="{esc(nom)}">' if pc else f'<tr data-numero="{esc(num)}" data-nombre="{esc(nom)}">'
    return (
        otr
        + f"<td>{esc(pos)}</td>"
        + f"<td>{esc(num)}</td>"
        + f"<td>{esc(nom)}</td>"
        + f"<td>{esc(liga)}</td>"
        + f"<td>{esc(moto)}</td>"
        + f"<td>{esc(clase)}</td>"
        + f"<td>{esc(vueltas)}</td>"
        + f"<td>{esc(tot)}</td>"
        + f"<td>{esc(t_aj)}</td>"
        + "</tr>"
    )


def _scratch_row_nonempty(row):
    for k in ("Pos.", "Pos", "N°", "Nº", "Nombre"):
        if (row.get(k) or "").strip():
            return True
    return False


def table_scratch(rows):
    thead = "<thead><tr><th>Pos.</th><th>N°</th><th>Nombre</th><th>Liga</th><th>Moto</th><th>Clase</th><th>Vueltas</th><th>Total t°</th><th>Tiempo ajustado</th></tr></thead>"
    body = "<tbody>" + "".join(tr_scratch(r) for r in rows if _scratch_row_nonempty(r)) + "</tbody>"
    return f"<table>{thead}{body}</table>"


def block_scratch():
    rows = read_scratch_raw()
    return (
        '<div class="final-block"><h3>Resultados</h3><div class="table-wrapper">'
        + table_scratch(rows)
        + "</div></div>"
    )


def block_infantil_e1():
    final_rows = read_csv_rows("infantil enduro 1 - final - resultados.csv") or []
    parts = [
        '<div class="final-block">',
        '<div class="session-title-row"><h3>Final</h3></div>',
        '<div class="table-wrapper">',
        table_final_inf_e1(final_rows),
        "</div></div>",
    ]

    desglose_parts = []
    for title, csv_name in INF_E1_CARRERAS.items():
        rows = read_csv_rows(csv_name)
        if rows:
            desglose_parts.append(session_row(title, INF_E1_PDFS.get(title)))
            desglose_parts.append('<div class="table-wrapper">')
            desglose_parts.append(table_carrera(rows))
            desglose_parts.append("</div>")

    if desglose_parts:
        parts.append('<div class="desglose-block"><h3>Desglose por sesión</h3>')
        parts.extend(desglose_parts)
        parts.append("</div>")

    return "".join(parts)


def block_simple_carrera(cat_id):
    rows = read_csv_rows(CSV_FILES[cat_id]) or []
    pdf = PDFS.get(cat_id)
    return (
        '<div class="final-block">'
        + session_row("Carrera", pdf)
        + '<div class="table-wrapper">'
        + table_carrera(rows)
        + "</div></div>"
    )


def section(cat_id, title_h2):
    if cat_id == "scratch":
        body = block_scratch()
    elif cat_id == "infantil-enduro-1-final":
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
    return "\n".join(
        f'            <a href="#{cid}" class="index-card" data-categoria-id="{cid}">{esc(title)}</a>'
        for cid, title in ORDER
    )


def modal_labels():
    return "\n".join(
        f'                <label class="modal-cat-item"><input type="checkbox" value="{cid}" checked> {esc(title)}</label>'
        for cid, title in ORDER
    )


def main():
    sections_html = "\n".join(section(cid, t) for cid, t in ORDER)

    page = f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>III Válida Nacional de Enduro - San Jerónimo, Antioquia | FEDEMOTO</title>
    <link rel="icon" type="image/png" href="../../../fedemoto-logo.png">
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Montserrat:wght@500;600;700;800&family=Source+Sans+3:wght@400;500;600;700&family=Barlow+Condensed:wght@500;600;700&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="../../../fedemoto-theme.css">
    
</head>
<body>
    <div id="menu-container"></div>
    <div id="contenido-exportar" class="container">
        <header>
            <h1>III Válida Nacional de Enduro</h1>
            <p>San Jerónimo, Antioquia - Resultados por categoría</p>
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
