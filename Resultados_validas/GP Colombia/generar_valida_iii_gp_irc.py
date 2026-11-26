# -*- coding: utf-8 -*-
"""
Genera la página HTML de la III Válida (Válida Final) GP Colombia - Gran Premio IRC.
- Incluye Clasificatoria (extraída de QualifyReduced.pdf y enlazada al PDF oficial) y Carrera
  (enlazada a VUELTA A VUELTA_GRAN PREMIO IRC VALIDA FINAL).
- Femenina: clasificatoria conjunta en 'Femenina'; carrera en 'Femenina Expertas' (CSV) y
  'Femenina Novatas' (reconstruida exactamente desde Laptimes.pdf + QualifyReduced.pdf).
- Super Stock: dividida en 'Super Stock 600' y 'Super Stock 1000' (clasificatoria y carrera,
  con carrera de 1000 reconstruida exactamente desde Laptimes.pdf + QualifyReduced.pdf).
- X-Bikes: dividida en 'X-Bikes A' y 'X-Bikes B' (clasificatoria y carrera).
- Escuela Fedemoto: incluye 'III Válida' (disputada previamente en Rivera) y 'IV Válida'
  (disputada en el Gran Premio IRC), junto con sus sesiones clasificatorias y vuelta a vuelta.
"""

import csv
import html
import os
import re
import sys
import unicodedata
from collections import defaultdict
from urllib.parse import quote

import fitz

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
FILES_DIR = os.path.join(SCRIPT_DIR, "FILES EXPORTED_GRAN PREMIO IRC VALIDA FINAL")
ESC_III_FILES_DIR = os.path.join(SCRIPT_DIR, "FILES_EXPORTED_Escuela fedemoto III Val")
OUTPUT_FILE = os.path.join(SCRIPT_DIR, "valida_iii_gp_colombia_irc.html")

VUELTA_DIR = os.path.join(SCRIPT_DIR, "VUELTA A VUELTA_GRAN PREMIO IRC VALIDA FINAL")
VUELTA_FOLDER_URL = "VUELTA A VUELTA_GRAN PREMIO IRC VALIDA FINAL"
FILES_FOLDER_URL = "FILES EXPORTED_GRAN PREMIO IRC VALIDA FINAL"
ESC_III_VUELTA_DIR = os.path.join(SCRIPT_DIR, "VUELTA A VUELTA_ Escuela fedemoto III Val")
ESC_III_VUELTA_URL = "VUELTA A VUELTA_ Escuela fedemoto III Val"

_RV_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, ".."))
if _RV_ROOT not in sys.path:
    sys.path.insert(0, _RV_ROOT)
import vuelta_a_vuelta as vv  # noqa: E402

_MX_DIR = os.path.join(_RV_ROOT, "Motocross", "Primer semestre")
if _MX_DIR not in sys.path:
    sys.path.insert(0, _MX_DIR)
import generar_valida_girardota as gmx  # noqa: E402

FEMENINA = "Femenina"
FEMENINA_EXPERTAS = "Femenina Expertas"
FEMENINA_NOVATAS = "Femenina Novatas"
SUPER_STOCK_600 = "Super Stock 600"
SUPER_STOCK_1000 = "Super Stock 1000"
X_BIKES_A = "X-Bikes A"
X_BIKES_B = "X-Bikes B"
ESCUELA_FEDEMOTO = "Escuela Fedemoto"
SUPERMOTO_EXP_METZELER = "Supermoto Expertos Metzeler"
SUPERMOTO_NOV_METZELER = "Supermoto Novatos Metzeler"
SUZUKI_GSX = "Suzuki GSX R/S 150"
CUATRIMOTARD = "Cuatrimotard (II + III GP)"
PULSAR_NS_200 = "Pulsar NS 200 FI"

# Dorsales de Super Stock 600 y 1000 en la III Válida IRC
SS_600_NUMEROS_IRC = {"897", "141", "484", "940", "640", "816", "496", "619", "98", "542", "639"}
SS_1000_NUMEROS_IRC = {"883", "67", "703", "131", "930", "244", "558", "879", "46", "293", "779"}

SESSION_SORT_KEY = {
    "Final": 0,
    "IV Válida": 1.0,
    "III Válida": 1.2,
    "Carrera": 1.5,
    "Clasificación final": 1.8,
    "Clasificatoria": 2.0,
    "Clasificatoria (IV Válida)": 2.1,
    "Clasificatoria (III Válida)": 2.2,
    "Práctica Libre (III Válida)": 2.3,
}


def _fold_accents(text):
    return "".join(
        c for c in unicodedata.normalize("NFD", str(text or "")) if unicodedata.category(c) != "Mn"
    )


def normalize_numero(num):
    return re.sub(r"\s+", "", str(num or "").strip()).upper()


def format_header(header):
    if not header:
        return ""
    h = str(header).strip()
    return h[0].upper() + h[1:].lower() if h else ""


def format_categoria_name(name):
    if not name:
        return name
    folded = _fold_accents(name).lower().strip()
    folded_compact = re.sub(r"\s+", " ", folded)
    if "cuatrimotard" in folded_compact:
        return CUATRIMOTARD
    if "sm expertos" in folded_compact or "supermoto expertos" in folded_compact:
        return SUPERMOTO_EXP_METZELER
    if "sm novatos" in folded_compact or "supermoto novatos" in folded_compact:
        return SUPERMOTO_NOV_METZELER
    if "suzuki" in folded_compact:
        return SUZUKI_GSX
    if "pulsar" in folded_compact:
        return PULSAR_NS_200
    if "minibike fedemoto" in folded_compact or "escuela fedemoto" in folded_compact:
        return ESCUELA_FEDEMOTO
    if "mini bike 190" in folded_compact or "minibike 190" in folded_compact:
        return "Minibike 190"
    if "street race" in folded_compact:
        return "Street Race 250"
    if re.match(r"^150\s*cc\s*elite$", folded_compact) or folded_compact == "150cc":
        return "150cc"
    if re.match(r"^150\s*cc\s*inicio$", folded_compact):
        return "150cc Inicio"
    if re.match(r"^150\s*cc\s*master$", folded_compact):
        return "150cc Master"
    if re.match(r"^115\s*cc\s*elite$", folded_compact):
        return "115cc Elite"
    if re.match(r"^115\s*cc\s*infantil$", folded_compact):
        return "115cc Infantil"
    if re.match(r"^115\s*cc\s*inicio$", folded_compact):
        return "115cc Inicio"
    if re.match(r"^115\s*cc\s*master$", folded_compact):
        return "115cc Master"
    if "200" in folded_compact and "2t" in folded_compact:
        return "200cc 2T"
    if "220" in folded_compact and "4t" in folded_compact:
        return "220cc 4T"
    if "super bike" in folded_compact or "superbike" in folded_compact:
        return "Super Bike"
    if "super sport" in folded_compact or "supersport" in folded_compact:
        return "Super Sport"

    parts = re.split(r"[\s\-]+", name)
    result = []
    for p in parts:
        if p:
            if re.match(r"^\d+cc$", p, re.I):
                result.append(p.lower())
            elif re.match(r"^\d+t$", p, re.I):
                result.append(p.upper())
            elif p.upper() in ("CRS", "TVS", "A", "B", "Y", "R15"):
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
        "escuela fedemoto": 30.5,
        "minimotard": 31,
        "x-bikes a": 32,
        "x-bikes b": 33,
        "yamaha r15": 34,
        "suzuki gsx r/s 150": 35,
        "pulsar ns 200 fi": 36,
        "street race 250": 40,
        "crs expertos": 50,
        "crs novatos": 51,
        "femenina": 59,
        "femenina expertas": 60,
        "femenina novatas": 61,
        "cuatrimotard (ii + iii gp)": 70,
        "cuatrimotard": 70,
        "super bike": 80,
        "super sport": 81,
        "super stock 600": 82,
        "super stock 1000": 83,
        "supermoto expertos metzeler": 90,
        "supermoto novatos metzeler": 91,
    }
    return (order.get(c, 99), categoria)


def parse_filename(filename):
    name = filename.replace(".csv", "").strip()
    name = re.sub(r"\s*-\s*resultados\s*$", "", name, flags=re.I).strip()
    parts = [p.strip() for p in re.split(r"\s+-\s+", name, flags=re.I) if p.strip()]
    if len(parts) < 2:
        return (format_categoria_name(parts[0] if parts else name), "Carrera", SESSION_SORT_KEY["Carrera"])
    tipo_str = _fold_accents(parts[-1]).lower()
    cat_raw = " - ".join(parts[:-1])
    if "clasif" in tipo_str or "practica" in tipo_str:
        tipo = "Clasificatoria"
    elif "carrera" in tipo_str:
        tipo = "Carrera"
    elif "final" in tipo_str:
        tipo = "Final"
    else:
        tipo = format_categoria_name(parts[-1])
    categoria = format_categoria_name(cat_raw)
    return (categoria, tipo, SESSION_SORT_KEY.get(tipo, 99))


def parse_csv(filepath):
    with open(filepath, "r", encoding="utf-8-sig") as f:
        raw = f.read()
    if not raw.strip():
        return [], []
    lines = raw.splitlines()
    delim = ";" if lines[0].count(";") > lines[0].count(",") else ","
    rows = list(csv.reader(lines, delimiter=delim))
    if not rows:
        return [], []
    headers = [h.strip() for h in rows[0]]
    body = [[c.strip() for c in r] for r in rows[1:]]
    return headers, body


def renumber_positions_rows(rows, idx_pos=0):
    if idx_pos < 0:
        return rows
    pos = 0
    out = []
    for row in rows:
        r = list(row)
        p = str(r[idx_pos]).strip().upper() if idx_pos < len(r) else ""
        if p in ("NT", "EX", "DNF", "DQ", "NS", "NE"):
            out.append(r)
            continue
        pos += 1
        r[idx_pos] = str(pos)
        out.append(r)
    return out


def remove_columns_by_name(headers, rows, drop_names):
    drop_set = {_fold_accents(n).lower().strip() for n in drop_names}
    keep_ix = [i for i, h in enumerate(headers) if _fold_accents(h).lower().strip() not in drop_set]
    h_out = [headers[i] for i in keep_ix]
    r_out = [[r[i] if i < len(r) else "" for i in keep_ix] for r in rows]
    return h_out, r_out


def remove_comentario_and_collect(headers, rows):
    idx = gmx.find_col_index(headers, ("comentario", "comentarios", "nota", "notas"))
    if idx < 0:
        return headers, rows, [""] * len(rows)
    comentarios = [r[idx].strip() if len(r) > idx and r[idx] else "" for r in rows]
    h_out = headers[:idx] + headers[idx + 1:]
    r_out = [r[:idx] + r[idx + 1:] if len(r) > idx else r for r in rows]
    return h_out, r_out, comentarios


def time_to_seconds(t):
    if not t or not str(t).strip():
        return None
    t = str(t).strip()
    if re.match(r"^\d+:\d{2}\.?\d*$", t):
        parts = t.split(":")
        return int(parts[0]) * 60 + float(parts[1])
    if re.match(r"^\d{1,2}\.\d+$", t):
        return float(t)
    return None


def tod_to_seconds(tod):
    parts = str(tod).strip().split(":")
    if len(parts) == 3:
        return int(parts[0]) * 3600 + int(parts[1]) * 60 + float(parts[2])
    return None


def fmt_gap_seconds(sec):
    if sec is None or sec <= 0:
        return ""
    if sec >= 60:
        m = int(sec // 60)
        rem = sec - m * 60
        return f"{m}:{rem:06.3f}"
    return f"{sec:.3f}"


def puntos_fedemoto_por_pos(pos):
    tabla = {1: 15, 2: 13, 3: 11, 4: 10, 5: 9, 6: 8, 7: 7, 8: 6, 9: 5, 10: 4, 11: 3, 12: 2, 13: 1, 14: 1, 15: 1}
    return str(tabla.get(pos, 0))


def _parse_laptimes_pdf(pdf_path):
    """Extrae vueltas, mejor vuelta y hora de meta exacta desde un PDF Laptimes de Orbits."""
    if not os.path.exists(pdf_path):
        return {}
    doc = fitz.open(pdf_path)
    riders = {}
    current_rider = None
    for page in doc:
        d = page.get_text("dict")
        lines_by_col = {0: [], 1: [], 2: []}
        for b in d["blocks"]:
            for l in b.get("lines", []):
                txt = "".join(s["text"] for s in l.get("spans", [])).strip()
                if not txt:
                    continue
                x0, y0 = l["bbox"][0], l["bbox"][1]
                if y0 < 138 or y0 > 742:
                    continue
                if txt in ("Vuelta", "u e lta", "Hora", "día") or ("Vuelta" in txt and len(txt) < 15):
                    continue
                col = 0 if x0 < 200 else (1 if x0 < 400 else 2)
                lines_by_col[col].append((y0, x0, txt))
        for col in (0, 1, 2):
            col_items = sorted(lines_by_col[col], key=lambda it: (it[0], it[1]))
            rows = []
            for y0, x0, txt in col_items:
                if not rows or abs(y0 - rows[-1][0]) > 3.5:
                    rows.append([y0, [(x0, txt)]])
                else:
                    rows[-1][1].append((x0, txt))
            for _, parts in rows:
                parts.sort(key=lambda it: it[0])
                full = " ".join(p[1] for p in parts).strip()
                m_r = re.match(r"^\(([0-9A-Za-z\-]+)\)\s+(.+)$", full)
                if m_r and not full.lower().startswith("(15:00"):
                    num, name = normalize_numero(m_r.group(1)), m_r.group(2).strip()
                    current_rider = num
                    if num not in riders:
                        riders[num] = {"num": num, "name": name, "laps": [], "order": len(riders)}
                    continue
                if not current_rider:
                    continue
                m_lap = re.match(
                    r"^(\d+)\s+(\d+:\d{2}\.\d{3}|\d{2}\.\d{3})(?:\s+\+?[0-9:\.]+)?\s+(\d{1,2}:\d{2}:\d{2}\.\d{3})$",
                    full,
                )
                if m_lap:
                    riders[current_rider]["laps"].append((int(m_lap.group(1)), m_lap.group(2), m_lap.group(3)))
    return riders


def _reconstruct_subclass_race(laptimes_pdf, exclude_nums, qual_meta_by_num, required_laps):
    """Reconstruye tabla oficial de Carrera para la subclase faltante en exportación CSV de Orbits."""
    ldata = _parse_laptimes_pdf(laptimes_pdf)
    headers = ["Pos.", "N°", "Nombre", "Puntos", "Dif. resp. 1°", "Mejor tm", "Moto", "Liga", "Club", "Vueltas"]
    classified = []
    not_classified = []

    seen_nums = set()
    for num, info in sorted(ldata.items(), key=lambda kv: kv[1]["order"]):
        if num in exclude_nums:
            continue
        seen_nums.add(num)
        laps = info["laps"]
        n_laps = len(laps)
        best_tm = min((x[1] for x in laps), key=lambda t: time_to_seconds(t) or 9999.0) if laps else ""
        last_tod = tod_to_seconds(laps[-1][2]) if laps else None
        meta = qual_meta_by_num.get(num, {})
        nombre = meta.get("nombre") or info["name"]
        moto = meta.get("moto", "")
        liga = meta.get("liga", "")
        club = meta.get("club", "")
        # Regla 75% de vueltas del ganador
        if n_laps >= int(required_laps * 0.75 + 0.999):
            classified.append({
                "num": num, "nombre": nombre, "laps": n_laps, "best_tm": best_tm,
                "last_tod": last_tod, "moto": moto, "liga": liga, "club": club,
            })
        else:
            not_classified.append({
                "num": num, "nombre": nombre, "laps": n_laps, "best_tm": best_tm,
                "moto": moto, "liga": liga, "club": club,
            })

    # Añadir inscritos de clasificatoria de esta subclase que no registraron vuelta (NT)
    for num, meta in qual_meta_by_num.items():
        if num not in exclude_nums and num not in seen_nums:
            not_classified.append({
                "num": num, "nombre": meta.get("nombre", ""), "laps": 0, "best_tm": "",
                "moto": meta.get("moto", ""), "liga": meta.get("liga", ""), "club": meta.get("club", ""),
            })

    classified.sort(key=lambda x: (-x["laps"], x["last_tod"] if x["last_tod"] is not None else 999999.0))
    rows = []
    leader_laps = classified[0]["laps"] if classified else required_laps
    leader_tod = classified[0]["last_tod"] if classified else None

    for pos, r in enumerate(classified, start=1):
        if pos == 1:
            dif = ""
        elif r["laps"] < leader_laps:
            diff_l = leader_laps - r["laps"]
            dif = f"{diff_l} Vuelta" if diff_l == 1 else f"{diff_l} Vueltas"
        else:
            dif = fmt_gap_seconds((r["last_tod"] or 0.0) - (leader_tod or 0.0))
        rows.append([
            str(pos), r["num"], r["nombre"], puntos_fedemoto_por_pos(pos),
            dif, r["best_tm"], r["moto"], r["liga"], r["club"], str(r["laps"]),
        ])

    for r in not_classified:
        rows.append([
            "NT", r["num"], r["nombre"], "0", "NT", r["best_tm"],
            r["moto"], r["liga"], r["club"], str(r["laps"]) if r["laps"] > 0 else "",
        ])

    return headers, rows


# Metadatos complementarios verificados desde los QualifyReduced.pdf de Femenina y Super Stock 1000
EXTRA_QUAL_META = {
    ("Femenina", "997"): {"nombre": "Laura Camila Castaño Vasquez", "liga": "Cundinamarca", "club": "Racing pilots Academy", "moto": "Yamaha"},
    ("Femenina", "225"): {"nombre": "Laura Sofia BARRERA ACUÑA", "liga": "Cundinamarca", "club": "CLUB GIRARDOT RACING", "moto": "AKT"},
    ("Femenina", "399"): {"nombre": "Angela Yiseth OTERO BECERRA", "liga": "Cundinamarca", "club": "CLUB GIRARDOT RACING", "moto": "AKT"},
    ("Femenina", "236"): {"nombre": "Andrea Muñoz Melo", "liga": "Tolima", "club": "CLUB PISTON RACING", "moto": "Yamaha"},
    ("Femenina", "58"): {"nombre": "Maroly Nicole BASABE", "liga": "Tolima", "club": "CLUB PISTON RACING", "moto": "Bajaj"},
    ("Femenina", "376"): {"nombre": "Laura Sabhina Franco Gonzalez", "liga": "Tolima", "club": "CLUB PISTON RACING", "moto": "Bajaj"},
    ("Femenina", "253"): {"nombre": "Nicolle Vanessa DIAZ LOPEZ", "liga": "Tolima", "club": "CLUB PISTON RACING", "moto": "Yamaha"},
    ("Femenina", "446"): {"nombre": "Diana Katherine PEÑA VILLALBA", "liga": "Bogotá D.C.", "club": "Xspeed Racing", "moto": "Yamaha"},
    ("Femenina", "298"): {"nombre": "Yury Alejandra Gomez Gil", "liga": "Cundinamarca", "club": "CLUB GIRARDOT RACING", "moto": "Bajaj"},
    ("Femenina", "247"): {"nombre": "Angie Valentina Bayona Rodriguez", "liga": "Tolima", "club": "CLUB PISTON RACING", "moto": "Bajaj"},
    ("SuperStock1000", "883"): {"nombre": "Dashua N Diaz Morales", "liga": "Bogotá D.C.", "club": "Racing pilots Academy", "moto": "BMW"},
    ("SuperStock1000", "67"): {"nombre": "Jhonny Rada", "liga": "Bogotá D.C.", "club": "Xspeed Racing", "moto": "Yamaha"},
    ("SuperStock1000", "703"): {"nombre": "Mauro Ferney Gallo Fonseca", "liga": "Antioquia", "club": "CLUB ANTIOQUIA 2 RUEDAS RACER", "moto": "Ducati"},
    ("SuperStock1000", "131"): {"nombre": "Christian Andres RUBIO PARDO", "liga": "Cundinamarca", "club": "CLUB IGUANA RACING GIRARDOT", "moto": "Kawasaki"},
    ("SuperStock1000", "930"): {"nombre": "George Michael herrera Trujillo", "liga": "Quindío", "club": "CLUB DISCOVER QUINDIO", "moto": "BMW"},
    ("SuperStock1000", "244"): {"nombre": "Andrés Felipe Aldana jaramillo", "liga": "Quindío", "club": "CLUB MONSTER GARAGE", "moto": "BMW"},
    ("SuperStock1000", "558"): {"nombre": "Fabian Yesid SANABRIA ZEA", "liga": "Bogotá D.C.", "club": "Racing pilots Academy", "moto": "Kawasaki"},
    ("SuperStock1000", "879"): {"nombre": "Sergio David PACHÓN GARZÓN", "liga": "Bogotá D.C.", "club": "Racing pilots Academy", "moto": "Aprilia"},
    ("SuperStock1000", "46"): {"nombre": "Maria Paula ARIAS MEDINA", "liga": "Meta", "club": "CLUB DE MOTOCICLISMO SANTIHC 146", "moto": "Ducati"},
    ("SuperStock1000", "293"): {"nombre": "Fenky Jhoan Infante carmona", "liga": "Bogotá D.C.", "club": "Racing pilots Academy", "moto": "BMW"},
    ("SuperStock1000", "779"): {"nombre": "Rafael Andrés Rojas Ibáñez", "liga": "Bogotá D.C.", "club": "Xspeed Racing", "moto": "Ducati"},
}


def load_categorias_data():
    categorias_data = {}
    femenina_exp_nums = set()
    xbikes_num_bucket = {}

    # Primera pasada: construir padrón global por nombre y número (de IRC, BMW y Vitrix)
    global_by_name = {}
    for search_dir in (FILES_DIR, os.path.join(SCRIPT_DIR, "FILES EXPORTED_Gran Premio BMW"), os.path.join(SCRIPT_DIR, "FILES EXPORTED_Gran Premio Vitrix")):
        if not os.path.isdir(search_dir):
            continue
        for fn in sorted(os.listdir(search_dir)):
            if not fn.lower().endswith(".csv"):
                continue
            h_r, r_r = parse_csv(os.path.join(search_dir, fn))
            ix_num = gmx.find_col_index(h_r, ("n°", "nº", "numero", "n"))
            ix_nom = gmx.find_col_index(h_r, ("nombre",))
            ix_cls = gmx.find_col_index(h_r, ("clase",))
            ix_lig = gmx.find_col_index(h_r, ("liga",))
            ix_clb = gmx.find_col_index(h_r, ("club",))
            ix_mot = gmx.find_col_index(h_r, ("moto",))
            if "x-bikes" in fn.lower() and search_dir == FILES_DIR and ix_num >= 0 and ix_cls >= 0:
                for rr in r_r:
                    if len(rr) > max(ix_num, ix_cls):
                        cl = rr[ix_cls].strip().lower()
                        if "b" in cl.split()[-1:]:
                            xbikes_num_bucket[normalize_numero(rr[ix_num])] = "B"
                        elif "a" in cl.split()[-1:]:
                            xbikes_num_bucket[normalize_numero(rr[ix_num])] = "A"
            if ix_nom < 0:
                continue
            for rr in r_r:
                if len(rr) <= ix_nom:
                    continue
                nk = re.sub(r"[^a-z0-9]+", "", _fold_accents(rr[ix_nom]).lower())
                if not nk or "secretaria" in nk:
                    continue
                rec = global_by_name.setdefault(nk, {})
                if 0 <= ix_lig < len(rr) and rr[ix_lig].strip() and not rec.get("liga"):
                    rec["liga"] = rr[ix_lig].strip()
                if 0 <= ix_clb < len(rr) and rr[ix_clb].strip() and not rec.get("club"):
                    rec["club"] = rr[ix_clb].strip()
                if 0 <= ix_mot < len(rr) and rr[ix_mot].strip() and not rec.get("moto"):
                    rec["moto"] = rr[ix_mot].strip()

    raw_super_stock_clasif = None
    raw_xbikes_items = []

    for filename in sorted(os.listdir(FILES_DIR)):
        if not filename.lower().endswith(".csv") or filename.lower().startswith("desktop"):
            continue
        filepath = os.path.join(FILES_DIR, filename)
        if not os.path.isfile(filepath):
            continue

        headers_raw, rows_raw = parse_csv(filepath)
        categoria, tipo, sort_key = parse_filename(filename)

        # Enriquecer Moto/Liga/Club en tablas de Carrera (especialmente Pulsar NS 200 FI, Suzuki, R15)
        if tipo == "Carrera":
            ix_nom = gmx.find_col_index(headers_raw, ("nombre",))
            ix_lig = gmx.find_col_index(headers_raw, ("liga",))
            ix_clb = gmx.find_col_index(headers_raw, ("club",))
            ix_mot = gmx.find_col_index(headers_raw, ("moto",))
            for r in rows_raw:
                nk = re.sub(r"[^a-z0-9]+", "", _fold_accents(r[ix_nom]).lower()) if 0 <= ix_nom < len(r) else ""
                gmeta = global_by_name.get(nk, {})
                if 0 <= ix_lig < len(r) and not r[ix_lig].strip() and gmeta.get("liga"):
                    r[ix_lig] = gmeta["liga"]
                if 0 <= ix_clb < len(r) and not r[ix_clb].strip() and gmeta.get("club"):
                    r[ix_clb] = gmeta["club"]
                if 0 <= ix_mot < len(r) and not r[ix_mot].strip():
                    if categoria == PULSAR_NS_200:
                        r[ix_mot] = "Bajaj"
                    elif categoria == SUZUKI_GSX:
                        r[ix_mot] = "Suzuki"
                    elif categoria == "Yamaha R15":
                        r[ix_mot] = "Yamaha"
                    elif gmeta.get("moto"):
                        r[ix_mot] = gmeta["moto"]

        # 1. Femenina
        if categoria.lower() == "femenina":
            if tipo == "Clasificatoria":
                h, r, com = remove_comentario_and_collect(headers_raw, rows_raw)
                h, r = remove_columns_by_name(h, r, ("clase", "liga", "club", "moto"))
                categorias_data[FEMENINA] = [(tipo, sort_key, [format_header(x) for x in h], r, com)]
            elif tipo == "Carrera":
                ix_num = gmx.find_col_index(headers_raw, ("n°", "nº", "numero", "n"))
                for rr in rows_raw:
                    if 0 <= ix_num < len(rr) and rr[ix_num].strip():
                        femenina_exp_nums.add(normalize_numero(rr[ix_num]))
                h, r, com = remove_comentario_and_collect(headers_raw, rows_raw)
                h, r = remove_columns_by_name(h, r, ("clase",))
                categorias_data.setdefault(FEMENINA_EXPERTAS, []).append(
                    (tipo, sort_key, [format_header(x) for x in h], r, com)
                )
            continue

        # 2. Super Stock 600 y 1000
        if "super stock" in categoria.lower():
            if tipo == "Clasificatoria":
                raw_super_stock_clasif = (headers_raw, rows_raw)
            elif tipo == "Carrera":
                h, r, com = remove_comentario_and_collect(headers_raw, rows_raw)
                h, r = remove_columns_by_name(h, r, ("clase",))
                categorias_data.setdefault(SUPER_STOCK_600, []).append(
                    (tipo, sort_key, [format_header(x) for x in h], r, com)
                )
            continue

        # 3. X-Bikes A y B
        if "x-bikes" in categoria.lower() or "x bikes" in categoria.lower():
            raw_xbikes_items.append((tipo, sort_key, headers_raw, rows_raw))
            continue

        # 4. Escuela Fedemoto (IV Válida disputada en IRC)
        if categoria == ESCUELA_FEDEMOTO:
            h, r, com = remove_comentario_and_collect(headers_raw, rows_raw)
            if tipo == "Clasificatoria":
                h, r = remove_columns_by_name(h, r, ("clase", "liga", "club", "moto"))
                es_tipo = "Clasificatoria (IV Válida)"
            else:
                h, r = remove_columns_by_name(h, r, ("clase",))
                es_tipo = "IV Válida"
            categorias_data.setdefault(ESCUELA_FEDEMOTO, []).append(
                (es_tipo, SESSION_SORT_KEY.get(es_tipo, 99), [format_header(x) for x in h], r, com)
            )
            continue

        # 5. Resto de categorías estándar
        h, r, com = remove_comentario_and_collect(headers_raw, rows_raw)
        if tipo == "Clasificatoria":
            h, r = remove_columns_by_name(h, r, ("clase", "liga", "club", "moto"))
        else:
            h, r = remove_columns_by_name(h, r, ("clase",))
        categorias_data.setdefault(categoria, []).append(
            (tipo, sort_key, [format_header(x) for x in h], r, com)
        )

    # Integrar III Válida Escuela Fedemoto (desde FILES_EXPORTED_Escuela fedemoto III Val)
    if os.path.isdir(ESC_III_FILES_DIR):
        for fn in sorted(os.listdir(ESC_III_FILES_DIR)):
            if not fn.lower().endswith(".csv"):
                continue
            h_raw, r_raw = parse_csv(os.path.join(ESC_III_FILES_DIR, fn))
            fn_fold = _fold_accents(fn).lower()
            if "carrera" in fn_fold:
                es_tipo = "III Válida"
                # Completar club/moto de los niños con el padrón global
                ix_nom = gmx.find_col_index(h_raw, ("nombre",))
                ix_clb = gmx.find_col_index(h_raw, ("club",))
                ix_mot = gmx.find_col_index(h_raw, ("moto",))
                for rr in r_raw:
                    nk = re.sub(r"[^a-z0-9]+", "", _fold_accents(rr[ix_nom]).lower()) if 0 <= ix_nom < len(rr) else ""
                    if "samuelvargas" in nk:
                        nk = "samuelvargasome"
                    elif "iangiovann" in nk:
                        nk = "iangiovannycandiajimenez"
                    elif "miguelangelcastillo" in nk:
                        nk = "miguelangelcastillodiago"
                    gm = global_by_name.get(nk, {})
                    if 0 <= ix_clb < len(rr) and not rr[ix_clb].strip() and gm.get("club"):
                        rr[ix_clb] = gm["club"]
                    if 0 <= ix_mot < len(rr) and not rr[ix_mot].strip():
                        rr[ix_mot] = gm.get("moto") or "YCF"
            elif "practica" in fn_fold:
                es_tipo = "Práctica Libre (III Válida)"
            else:
                es_tipo = "Clasificatoria (III Válida)"
            h, r, com = remove_comentario_and_collect(h_raw, r_raw)
            h, r = remove_columns_by_name(h, r, ("clase",))
            categorias_data.setdefault(ESCUELA_FEDEMOTO, []).append(
                (es_tipo, SESSION_SORT_KEY.get(es_tipo, 99), [format_header(x) for x in h], r, com)
            )

    # Reconstruir Carrera de Femenina Novatas desde Laptimes.pdf + metadatos de clasificatoria
    fem_qual_meta = {num: meta for (cat_k, num), meta in EXTRA_QUAL_META.items() if cat_k == "Femenina"}
    fem_nov_h, fem_nov_r = _reconstruct_subclass_race(
        os.path.join(VUELTA_DIR, "Femenina - 1 CARRERA - Laptimes.pdf"),
        femenina_exp_nums,
        fem_qual_meta,
        required_laps=8,
    )
    categorias_data.setdefault(FEMENINA_NOVATAS, []).append(
        ("Carrera", SESSION_SORT_KEY["Carrera"], fem_nov_h, fem_nov_r, [""] * len(fem_nov_r))
    )

    # Reconstruir Carrera de Super Stock 1000 desde Laptimes.pdf + metadatos de clasificatoria
    ss1000_qual_meta = {num: meta for (cat_k, num), meta in EXTRA_QUAL_META.items() if cat_k == "SuperStock1000"}
    ss1000_h, ss1000_r = _reconstruct_subclass_race(
        os.path.join(VUELTA_DIR, "Super stock 1000 600 - 1 CARRERA - Laptimes.pdf"),
        SS_600_NUMEROS_IRC,
        ss1000_qual_meta,
        required_laps=10,
    )
    categorias_data.setdefault(SUPER_STOCK_1000, []).append(
        ("Carrera", SESSION_SORT_KEY["Carrera"], ss1000_h, ss1000_r, [""] * len(ss1000_r))
    )

    # Dividir Clasificatoria de Super Stock en 600 y 1000
    if raw_super_stock_clasif:
        h_raw, r_raw = raw_super_stock_clasif
        ix_num = gmx.find_col_index(h_raw, ("n°", "nº", "numero", "n"))
        ix_tm = gmx.find_col_index(h_raw, ("mejor tm", "mejor tiempo"))
        for target_cat, num_set in ((SUPER_STOCK_600, SS_600_NUMEROS_IRC), (SUPER_STOCK_1000, SS_1000_NUMEROS_IRC)):
            sub_rows = [list(r) for r in r_raw if 0 <= ix_num < len(r) and normalize_numero(r[ix_num]) in num_set]
            h_c, r_c = remove_columns_by_name(h_raw, sub_rows, ("clase", "liga", "club", "moto", "comentario"))
            r_c = renumber_positions_rows(r_c, 0)
            # Recalcular Dif. resp. 1° y Dif. resp. anterior dentro de la subclase
            t0 = None
            tp = None
            for rr in r_c:
                sec = time_to_seconds(rr[3]) if len(rr) > 3 else None
                if sec is not None:
                    rr[4] = "" if t0 is None else fmt_gap_seconds(sec - t0)
                    rr[5] = "" if tp is None or (sec - tp) <= 1e-6 else fmt_gap_seconds(sec - tp)
                    if t0 is None:
                        t0 = sec
                    tp = sec
            categorias_data.setdefault(target_cat, []).append(
                ("Clasificatoria", SESSION_SORT_KEY["Clasificatoria"], [format_header(x) for x in h_c], r_c, [""] * len(r_c))
            )

    # Dividir X-Bikes en A y B (tanto Clasificatoria como Carrera)
    for tipo, sort_key, h_raw, r_raw in raw_xbikes_items:
        ix_num = gmx.find_col_index(h_raw, ("n°", "nº", "numero", "n"))
        ix_cls = gmx.find_col_index(h_raw, ("clase",))
        for target_cat, bucket_code in ((X_BIKES_A, "A"), (X_BIKES_B, "B")):
            sub_rows = []
            for r in r_raw:
                num = normalize_numero(r[ix_num]) if 0 <= ix_num < len(r) else ""
                b = None
                if 0 <= ix_cls < len(r) and r[ix_cls].strip():
                    cl = r[ix_cls].strip().lower()
                    b = "B" if cl.endswith("b") else ("A" if cl.endswith("a") else None)
                if not b:
                    b = xbikes_num_bucket.get(num)
                if b == bucket_code:
                    sub_rows.append(list(r))
            if not sub_rows:
                continue
            h_c, r_c, com = remove_comentario_and_collect(h_raw, sub_rows)
            if tipo == "Clasificatoria":
                h_c, r_c = remove_columns_by_name(h_c, r_c, ("clase", "liga", "club", "moto"))
                r_c = renumber_positions_rows(r_c, 0)
                t0 = tp = None
                for rr in r_c:
                    sec = time_to_seconds(rr[3]) if len(rr) > 3 else None
                    if sec is not None:
                        rr[4] = "" if t0 is None else fmt_gap_seconds(sec - t0)
                        rr[5] = "" if tp is None or (sec - tp) <= 1e-6 else fmt_gap_seconds(sec - tp)
                        if t0 is None:
                            t0 = sec
                        tp = sec
            else:
                h_c, r_c = remove_columns_by_name(h_c, r_c, ("clase",))
                r_c = renumber_positions_rows(r_c, 0)
            categorias_data.setdefault(target_cat, []).append(
                (tipo, sort_key, [format_header(x) for x in h_c], r_c, com)
            )

    for cat in categorias_data:
        categorias_data[cat].sort(key=lambda x: (SESSION_SORT_KEY.get(x[0], 99), x[0]))
    return categorias_data


def build_pdf_href_map():
    """Construye mapa (categoria_lower, tipo_sesion) -> (href_url, label_boton)."""
    hrefs = {}

    # 1. PDFs de Vuelta a Vuelta Carrera (VUELTA A VUELTA_GRAN PREMIO IRC VALIDA FINAL)
    if os.path.isdir(VUELTA_DIR):
        for fn in sorted(os.listdir(VUELTA_DIR)):
            if not fn.lower().endswith(".pdf"):
                continue
            url = f"{quote(VUELTA_FOLDER_URL)}/{quote(fn)}"
            stem = re.sub(r"(?i)\s*-\s*(Laptimes|RaceReduced)\s*\.pdf$", "", fn).strip()
            parts = [p.strip() for p in re.split(r"\s+-\s+", stem) if p.strip()]
            cat_raw = " - ".join(parts[:-1]) if len(parts) >= 2 else stem
            cat = format_categoria_name(cat_raw)
            cl = cat.lower()
            if "femenina" in cl:
                hrefs[(FEMENINA_EXPERTAS.lower(), "Carrera")] = (url, "Ver vuelta a vuelta")
                hrefs[(FEMENINA_NOVATAS.lower(), "Carrera")] = (url, "Ver vuelta a vuelta")
            elif "super stock" in cl:
                hrefs[(SUPER_STOCK_600.lower(), "Carrera")] = (url, "Ver vuelta a vuelta")
                hrefs[(SUPER_STOCK_1000.lower(), "Carrera")] = (url, "Ver vuelta a vuelta")
            elif "x-bikes" in cl or "x bikes" in cl:
                hrefs[(X_BIKES_A.lower(), "Carrera")] = (url, "Ver vuelta a vuelta")
                hrefs[(X_BIKES_B.lower(), "Carrera")] = (url, "Ver vuelta a vuelta")
            elif cat == ESCUELA_FEDEMOTO:
                hrefs[(ESCUELA_FEDEMOTO.lower(), "IV Válida")] = (url, "Ver vuelta a vuelta")
            else:
                hrefs[(cl, "Carrera")] = (url, "Ver vuelta a vuelta")

    # 2. PDFs de Clasificatoria en FILES EXPORTED_GRAN PREMIO IRC VALIDA FINAL
    if os.path.isdir(FILES_DIR):
        for fn in sorted(os.listdir(FILES_DIR)):
            if not fn.lower().endswith(".pdf"):
                continue
            if "qualifyreduced" not in fn.lower() and "clasif" not in fn.lower():
                continue
            url = f"{quote(FILES_FOLDER_URL)}/{quote(fn)}"
            btn_lbl = "Ver vuelta a vuelta" if "laptimes" in fn.lower() else "Ver clasificación (PDF)"
            stem = re.sub(r"(?i)\s*-\s*(QualifyReduced|Laptimes)\s*\.pdf$", "", fn).strip()
            parts = [p.strip() for p in re.split(r"\s+-\s+", stem) if p.strip()]
            cat_raw = " - ".join(parts[:-1]) if len(parts) >= 2 else stem
            cat = format_categoria_name(cat_raw)
            cl = cat.lower()
            if "femenina" in cl:
                hrefs[(FEMENINA.lower(), "Clasificatoria")] = (url, btn_lbl)
            elif "super stock" in cl:
                hrefs[(SUPER_STOCK_600.lower(), "Clasificatoria")] = (url, btn_lbl)
                hrefs[(SUPER_STOCK_1000.lower(), "Clasificatoria")] = (url, btn_lbl)
            elif "x-bikes" in cl or "x bikes" in cl:
                hrefs[(X_BIKES_A.lower(), "Clasificatoria")] = (url, btn_lbl)
                hrefs[(X_BIKES_B.lower(), "Clasificatoria")] = (url, btn_lbl)
            elif cat == ESCUELA_FEDEMOTO:
                hrefs[(ESCUELA_FEDEMOTO.lower(), "Clasificatoria (IV Válida)")] = (url, btn_lbl)
            else:
                # Si hay tanto Laptimes como QualifyReduced (ej. SM Expertos), preferir Laptimes o conservar QualifyReduced
                if (cl, "Clasificatoria") not in hrefs or "laptimes" in fn.lower():
                    hrefs[(cl, "Clasificatoria")] = (url, btn_lbl)

    # 3. PDFs de Escuela Fedemoto III Válida
    if os.path.isdir(ESC_III_VUELTA_DIR):
        for fn in sorted(os.listdir(ESC_III_VUELTA_DIR)):
            if not fn.lower().endswith(".pdf"):
                continue
            url = f"{quote(ESC_III_VUELTA_URL)}/{quote(fn)}"
            fl = _fold_accents(fn).lower()
            if "carrera" in fl:
                hrefs[(ESCUELA_FEDEMOTO.lower(), "III Válida")] = (url, "Ver vuelta a vuelta")
            elif "practica" in fl:
                hrefs[(ESCUELA_FEDEMOTO.lower(), "Práctica Libre (III Válida)")] = (url, "Ver vuelta a vuelta")
            elif "clasif" in fl:
                hrefs[(ESCUELA_FEDEMOTO.lower(), "Clasificatoria (III Válida)")] = (url, "Ver vuelta a vuelta")

    return hrefs


def escape_html(text):
    return html.escape(str(text)) if text else ""


def slugify(text):
    s = re.sub(r"[^\w\s-]", "", str(text).lower())
    return re.sub(r"[\s_]+", "-", s).strip("-")


def find_mejor_tm_index(headers):
    for i, h in enumerate(headers):
        hl = h.lower()
        if "mejor" in hl and ("tm" in hl or "tiempo" in hl):
            return i
    return -1


def get_mejor_tm_absoluto(rows, num_idx=1, mejor_tm_idx=-1, nombre_idx=2):
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


def render_session_title(categoria, tipo_sesion, pdf_hrefs):
    hit = pdf_hrefs.get((categoria.lower(), tipo_sesion))
    btn = ""
    if hit:
        url, lbl = hit
        btn = f'<a class="btn-vuelta-a-vuelta" href="{escape_html(url)}" target="_blank" rel="noopener noreferrer">{escape_html(lbl)}</a>'
    return f'<div class="session-title-row"><h3>{escape_html(tipo_sesion)}</h3>{btn}</div>'


def render_row(row, comentario, search_attrs):
    pos_val = str(row[0]).strip() if row else ""
    pos_class = ""
    if pos_val == "1":
        pos_class = ' class="pos-1"'
    elif pos_val == "2":
        pos_class = ' class="pos-2"'
    elif pos_val == "3":
        pos_class = ' class="pos-3"'
    parts = [f"<tr{pos_class}{search_attrs}>"]
    for i, cell in enumerate(row):
        if i == 0 and comentario:
            parts.append(
                f'<td><span class="pos-cell">{escape_html(cell)}</span>'
                f'<button type="button" class="comentario-btn" data-comentario="{escape_html(comentario)}" '
                f'aria-label="Ver comentario">i</button></td>'
            )
        else:
            parts.append(f"<td>{escape_html(cell)}</td>")
    parts.append("</tr>")
    return "".join(parts)


def pick_main_session(tablas):
    for pref in ("Final", "IV Válida", "Carrera", "Clasificatoria"):
        for t in tablas:
            if t[0] == pref:
                return t[0], (t[1], t[2], t[3])
    if tablas:
        t = tablas[0]
        return t[0], (t[1], t[2], t[3])
    return None, None


def generate_html():
    pdf_hrefs = build_pdf_href_map()
    categorias_data = load_categorias_data()
    sorted_categorias = sorted(categorias_data.keys(), key=get_category_sort_key)

    categorias_para_html = []
    for categoria in sorted_categorias:
        items = categorias_data[categoria]
        tablas = [(tipo, headers, rows, com) for tipo, _, headers, rows, com in items]
        main_tipo, _ = pick_main_session(tablas)
        section_id = slugify(f"{categoria} {main_tipo}" if main_tipo else f"{categoria} final")
        categorias_para_html.append((categoria, section_id, tablas))

    html_content = '''<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>III Válida GP Colombia - Gran Premio IRC | FEDEMOTO</title>
    <link rel="icon" type="image/png" href="../../fedemoto-logo.png">
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Montserrat:wght@500;600;700;800&family=Source+Sans+3:wght@400;500;600;700&family=Barlow+Condensed:wght@500;600;700&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="../../fedemoto-theme.css">
    <style>
''' + vv.CSS_PLACEHOLDER + r'''
        .pos-cell { display: inline-block; margin-right: 4px; }
        .comentario-btn { display: inline-flex; align-items: center; justify-content: center; width: 24px; height: 24px; margin-left: 6px; border: 1px solid #123E92; border-radius: 999px; background: #e8eef8; color: #123E92; font-size: 14px; font-weight: 700; cursor: pointer; vertical-align: middle; }
        .comentario-btn:hover, .comentario-btn:focus { background: #123E92; color: white; outline: none; }
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
    </style>
</head>
<body>
    <div id="menu-container"></div>
    <div id="contenido-exportar" class="container">
        <header>
            <h1>III Válida GP Colombia — Válida Final</h1>
            <p>Gran Premio IRC — Resultados por categoría</p>
        </header>
        <div class="toolbar">
            <input type="text" id="buscador" class="search-box" placeholder="Buscar por nombre o N° del piloto..." />
        </div>
        <div class="index-cards">
'''

    for cat, section_id, _ in categorias_para_html:
        html_content += f'            <a href="#{section_id}" class="index-card" data-categoria-id="{section_id}">{escape_html(cat)}</a>\n'

    html_content += "        </div>\n        <div class=\"content-section\">\n"

    for categoria, section_id, tablas in categorias_para_html:
        html_content += f'''
            <div class="categoria-section" id="{section_id}" data-categoria-id="{section_id}">
                <div class="categoria-header">
                    <h2>{escape_html(categoria)}</h2>
                    <button type="button" class="btn-top" title="Ir al inicio" aria-label="Ir al inicio">
                        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor"><path d="M12 4l-8 8h5v8h6v-8h5L12 4z"/></svg>
                    </button>
                </div>'''

        best_clasif = None
        best_carrera = None
        for tipo, headers, rows, _ in tablas:
            tm_idx = find_mejor_tm_index(headers)
            if tm_idx < 0:
                continue
            b = get_mejor_tm_absoluto(rows, 1, tm_idx, 2)
            if not b:
                continue
            if "Clasificatoria" in tipo and best_clasif is None:
                best_clasif = (b[0], b[1], b[2])
            elif tipo in ("Carrera", "IV Válida", "III Válida") and best_carrera is None:
                best_carrera = (b[0], b[1], b[2], tipo)

        if best_clasif or best_carrera:
            html_content += '''
                <div class="times-summary">
                    <h4>Mejores tiempos - Clasificatoria y carreras</h4>
                    <div class="times-summary-items">'''
            if best_clasif:
                html_content += f'\n                        <p><strong>Mejor tiempo Clasificatoria:</strong> {escape_html(best_clasif[2])} — N° {escape_html(best_clasif[0])} {escape_html(best_clasif[1])}</p>'
            if best_carrera:
                html_content += f'\n                        <p><strong>Mejor tiempo Carrera:</strong> {escape_html(best_carrera[2])} ({escape_html(best_carrera[3])}) — N° {escape_html(best_carrera[0])} {escape_html(best_carrera[1])}</p>'
            html_content += "</div></div>"

        main_tipo, main_table = pick_main_session(tablas)
        if main_table:
            headers, rows, comentarios = main_table
            html_content += '\n                <div class="final-block">'
            html_content += render_session_title(categoria, main_tipo, pdf_hrefs)
            html_content += '\n                <div class="table-wrapper">\n                    <table>\n                        <thead><tr>'
            for h in headers:
                html_content += f"<th>{escape_html(h)}</th>"
            html_content += "</tr></thead><tbody>"
            for i, row in enumerate(rows):
                com = comentarios[i] if i < len(comentarios) else ""
                s_attrs = f' data-numero="{escape_html(row[1] if len(row) > 1 else "")}" data-nombre="{escape_html(row[2] if len(row) > 2 else "")}"'
                html_content += render_row(row, com, s_attrs)
            html_content += "</tbody></table></div></div>"

        desglose = [t for t in tablas if t[0] != main_tipo]
        if desglose:
            html_content += '\n                <div class="desglose-block">\n                    <h3>Desglose por sesión</h3>'
            for tipo, headers, rows, comentarios in desglose:
                html_content += '\n                    <div class="session-block">'
                html_content += render_session_title(categoria, tipo, pdf_hrefs)
                html_content += '\n                    <div class="table-wrapper">\n                        <table>\n                            <thead><tr>'
                for h in headers:
                    html_content += f"<th>{escape_html(h)}</th>"
                html_content += "</tr></thead><tbody>"
                for i, row in enumerate(rows):
                    com = comentarios[i] if i < len(comentarios) else ""
                    s_attrs = f' data-numero="{escape_html(row[1] if len(row) > 1 else "")}" data-nombre="{escape_html(row[2] if len(row) > 2 else "")}"'
                    html_content += render_row(row, com, s_attrs)
                html_content += "</tbody></table></div></div>"
            html_content += "</div>"

        html_content += "\n            </div>"

    html_content += '''
        </div>
        <div class="pdf-section">
            <button id="descargarPDF" class="btn-pdf">📄 Descargar resultados en PDF</button>
            <p class="pdf-hint">Selecciona las categorías que deseas incluir en el documento oficial.</p>
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
    <script src="../../load-menu.js"></script>
    <script src="../../exportar-resultados-pdf.js"></script>
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
</html>'''

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(html_content)
    print(f"Archivo generado exitosamente: {OUTPUT_FILE}")


# --- Funciones de exportación para Informes y Resultados Generales ---

def _find_stats_indexes(headers):
    idx = {"numero": None, "nombre": None, "liga": None, "club": None, "moto": None, "pos": None, "puntos": None}
    for i, h in enumerate(headers):
        hk = _fold_accents(h).lower().strip()
        if hk in ("n", "no", "numero", "n°", "nº"):
            idx["numero"] = i
        elif "nombre" in hk:
            idx["nombre"] = i
        elif "liga" in hk:
            idx["liga"] = i
        elif "club" in hk:
            idx["club"] = i
        elif "moto" in hk:
            idx["moto"] = i
        elif "pos" in hk:
            idx["pos"] = i
        elif "puntos" in hk or "total puntos" in hk:
            idx["puntos"] = i
    return idx


def _rows_to_rider_list(headers, rows):
    idx = _find_stats_indexes(headers)
    if idx["numero"] is None:
        return []
    by_num = {}
    for row in rows:
        if len(row) <= idx["numero"]:
            continue
        numero = str(row[idx["numero"]]).strip()
        nombre = str(row[idx["nombre"]]).strip() if idx["nombre"] is not None and idx["nombre"] < len(row) else ""
        if not numero or "SECRETARIA" in nombre.upper():
            continue
        pts = 0.0
        if idx["puntos"] is not None and idx["puntos"] < len(row):
            m = re.search(r"-?\d+(\.\d+)?", str(row[idx["puntos"]]).replace(",", "."))
            pts = float(m.group(0)) if m else 0.0
        liga = str(row[idx["liga"]]).strip() if idx["liga"] is not None and idx["liga"] < len(row) else ""
        club = str(row[idx["club"]]).strip() if idx["club"] is not None and idx["club"] < len(row) else ""
        moto = str(row[idx["moto"]]).strip() if idx["moto"] is not None and idx["moto"] < len(row) else ""
        by_num[numero] = {
            "numero": numero,
            "nombre": nombre,
            "liga": liga,
            "club": club,
            "moto": moto,
            "clase": "",
            "puntos": pts,
        }
    return list(by_num.values())


def export_valida_general_rows(files_dir=None):
    """Exporta filas puntuables de la III Válida GP Colombia (para Escuela Fedemoto exporta IV Válida)."""
    categorias = load_categorias_data()
    out = {}
    for categoria, items in categorias.items():
        if categoria == FEMENINA:
            continue
        chosen = None
        for pref in ("Final", "IV Válida", "Carrera"):
            for tipo, _, headers, rows, _ in items:
                if tipo == pref:
                    chosen = (headers, rows)
                    break
            if chosen:
                break
        if not chosen:
            continue
        rlist = _rows_to_rider_list(chosen[0], chosen[1])
        if rlist:
            out[categoria] = rlist
    return out


def export_escuela_fedemoto_valida_iii_rows():
    """Exporta filas puntuables de la III Válida de Escuela Fedemoto (disputada en Rivera)."""
    categorias = load_categorias_data()
    for tipo, _, headers, rows, _ in categorias.get(ESCUELA_FEDEMOTO, []):
        if tipo == "III Válida":
            return _rows_to_rider_list(headers, rows)
    return []


def export_escuela_fedemoto_valida_iv_rows():
    """Exporta filas puntuables de la IV Válida de Escuela Fedemoto (disputada en Gran Premio IRC)."""
    categorias = load_categorias_data()
    for tipo, _, headers, rows, _ in categorias.get(ESCUELA_FEDEMOTO, []):
        if tipo == "IV Válida":
            return _rows_to_rider_list(headers, rows)
    return []


def export_valida_informe_rows(files_dir=None):
    """Exporta filas para el Informe Estadístico de la III Válida GP Colombia (incluye III y IV Válida Escuela)."""
    categorias = load_categorias_data()
    out = {}
    for categoria, items in categorias.items():
        if categoria == FEMENINA:
            continue
        if categoria == ESCUELA_FEDEMOTO:
            # En el informe del evento IRC contabilizamos los participantes de IV Válida (evento IRC)
            for tipo, _, headers, rows, _ in items:
                if tipo == "IV Válida":
                    out[categoria] = _rows_to_rider_list(headers, rows)
                    break
            continue
        for pref in ("Carrera", "Final", "Clasificatoria"):
            found = False
            for tipo, _, headers, rows, _ in items:
                if tipo == pref:
                    out[categoria] = _rows_to_rider_list(headers, rows)
                    found = True
                    break
            if found:
                break
    return out


if __name__ == "__main__":
    generate_html()
