"""
Genera la página HTML de la II Válida GP Colombia - Gran Premio BMW.
Incluye Clasificación final, práctica clasificatoria, carreras y finales.
Femenina: clasificatoria conjunta; carrera dividida en Expertas y Novatas (desde RaceReduced).
Super Stock: dividida en 600 y 1000 (clasificatoria y carrera).
X-Bikes: dividida en A y B.
Escuela Fedemoto: procesa 'MINIBIKE FEDEMOTO' con Carrera 1, Carrera 2 y Final sumada.
115cc Inicio: excluida a petición explícita del usuario.
Normalizaciones:
  - Supermoto Expertos -> Supermoto Expertos Metzeler
  - Supermoto Novatos -> Supermoto Novatos Metzeler
  - Suzuki -> Suzuki GSX R/S 150
"""

import csv
import html
import os
import re
import sys
import unicodedata
from collections import defaultdict

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
FILES_DIR = os.path.join(SCRIPT_DIR, "FILES EXPORTED_Gran Premio BMW")
OUTPUT_FILE = os.path.join(SCRIPT_DIR, "valida_ii_gp_colombia_bmw.html")
VUELTA_DIR = os.path.join(SCRIPT_DIR, "VUELTA A VUELTA_Gran Premio BMW")
VUELTA_FOLDER_URL = "VUELTA A VUELTA_Gran Premio BMW"

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
ESCUELA_FEDEMOTO = "Escuela Fedemoto"
SUPERMOTO_EXP_METZELER = "Supermoto Expertos Metzeler"
SUPERMOTO_NOV_METZELER = "Supermoto Novatos Metzeler"
SUZUKI_GSX = "Suzuki GSX R/S 150"
CUATRIMOTARD = "Cuatrimotard (II + III GP)"

COMBINED_SUPER_STOCK = "super stock 600 y 1000"
COMBINED_X_BIKES = "x-bikes a y b"

# Lista de dorsales de Super Stock 600 y 1000
SS_600_NUMEROS = {"141", "897", "98", "484", "71", "940", "619", "820", "640", "186", "544", "400", "639"}
SS_1000_NUMEROS = {"131", "244", "46", "293", "698", "360", "930", "79", "558", "879", "573", "64", "393", "280", "87", "122", "779", "964"}

# Orden de sesiones
SESSION_SORT_KEY = {
    "Final": 0,
    "Clasificación final": 1,
    "I Válida": 1.5,
    "II Válida": 1.6,
    "Clasificatoria": 2,
    "Práctica clasificatoria 1": 2,
    "Práctica clasificatoria 2": 2.5,
    "I Práctica Clasificatoria": 2.8,
    "II Práctica Clasificatoria": 2.9,
    "Carrera 1": 3,
    "Carrera 2": 4,
    "Carrera": 5,
}

def _fold_accents(text):
    return "".join(
        c for c in unicodedata.normalize("NFD", str(text)) if unicodedata.category(c) != "Mn"
    )

def canonical_session_tipo(tipo):
    folded = _fold_accents(tipo).lower().strip()
    if "clasificacion final" in folded or "clasificatoria final" in folded:
        return "Clasificación final"
    if folded == "final" or (folded.endswith("final") and "clasific" not in folded):
        return "Final"
    if "ii practica" in folded or "practica 2" in folded or "ii practica clasificatoria" in folded:
        return "II Práctica Clasificatoria"
    if "practica" in folded or "primera practica" in folded:
        return "I Práctica Clasificatoria" if "i practica" in folded else "Clasificatoria"
    if folded in ("i val", "i valida"):
        return "I Válida"
    if folded in ("ii val", "ii valida"):
        return "II Válida"
    if re.search(r"carrera\s*1", folded) or re.search(r"^1\s*carrera", folded) or folded in ("carrera 1",):
        return "Carrera 1"
    if re.search(r"carrera\s*2", folded) or re.search(r"^2\s*carrera", folded) or folded in ("carrera 2",):
        return "Carrera 2"
    if "carrera" in folded:
        return "Carrera"
    return str(tipo).strip()

def format_header(header):
    if not header:
        return ""
    h = str(header).strip()
    return h[0].upper() + h[1:].lower() if h else ""

def format_categoria_name(name):
    if not name:
        return name
    folded = _fold_accents(name).lower().strip()
    if "cuatrimotard" in folded:
        return CUATRIMOTARD
    if "supermoto expertos" in folded:
        return SUPERMOTO_EXP_METZELER
    if "supermoto novatos" in folded:
        return SUPERMOTO_NOV_METZELER
    if folded == "suzuki" or "suzuki gsx" in folded:
        return SUZUKI_GSX
    if "minibike fedemoto" in folded or "escuela fedemoto" in folded:
        return ESCUELA_FEDEMOTO
    
    parts = re.split(r'[\s\-]+', name)
    result = []
    for p in parts:
        if p:
            if re.match(r'^\d+cc$', p, re.I):
                result.append(p.lower())
            elif re.match(r"^\d+t$", p, re.I):
                result.append(p.upper())
            elif p.upper() in ("CRS", "TVS", "A", "B", "Y"):
                result.append(p.upper())
            elif p.upper() == "METZELER":
                result.append("Metzeler")
            else:
                result.append(p[0].upper() + p[1:].lower() if len(p) > 1 else p.upper())
    out = " ".join(result)
    out = re.sub(r"(?i)\bGsc\s+R\s+S\b", "GSX R/S", out)
    return out

def _is_combined_xbikes(categoria):
    c = _fold_accents(categoria).lower()
    return "x-bikes" in c or "x bikes" in c or "xbikes" in c

def parse_filename(filename):
    name = filename.replace(".csv", "").strip()
    name = re.sub(r"\s*-\s*resultados\s*$", "", name, flags=re.I).strip()
    parts = [p.strip() for p in re.split(r"\s+-\s+", name, flags=re.I) if p.strip()]
    if len(parts) < 2:
        return (format_categoria_name(parts[0] if parts else name), "Final", 0)
    rest = _fold_accents(" - ".join(parts[1:])).lower()
    rest_cat = _fold_accents(" - ".join(parts[:-1])).lower()
    tipo_str = _fold_accents(parts[-1]).lower()

    if "minibike fedemoto" in rest_cat or "escuela fedemoto" in rest_cat:
        if "ii val" in tipo_str:
            tipo = "II Válida"
        elif "i val" in tipo_str:
            tipo = "I Válida"
        elif "ii practica" in tipo_str:
            tipo = "II Práctica Clasificatoria"
        elif "practica" in tipo_str:
            tipo = "I Práctica Clasificatoria"
        else:
            tipo = format_categoria_name(parts[-1])
        return (ESCUELA_FEDEMOTO, tipo, SESSION_SORT_KEY.get(tipo, 99))
    
    if "clasificacion final" in rest or "clasificatoria final" in rest:
        tipo = "Clasificación final"
    elif tipo_str == "final" or (tipo_str.endswith("final") and "clasific" not in tipo_str):
        tipo = "Final"
    elif "ii practica" in tipo_str or "practica clasificatoria ii" in tipo_str or "segunda practica" in tipo_str:
        tipo = "Práctica clasificatoria 2"
    elif "practica" in tipo_str or "primera practica" in tipo_str:
        tipo = "Clasificatoria"
    elif re.search(r"carrera\s*1", tipo_str) or re.search(r"^1\s*carrera", tipo_str) or tipo_str in ("i val", "i valida"):
        tipo = "Carrera 1"
    elif re.search(r"carrera\s*2", tipo_str) or re.search(r"^2\s*carrera", tipo_str) or tipo_str in ("ii val", "ii valida"):
        tipo = "Carrera 2"
    elif "carrera" in tipo_str:
        tipo = "Carrera"
    else:
        tipo = canonical_session_tipo(format_categoria_name(parts[-1]))
    tipo = canonical_session_tipo(tipo)
    sort_key = SESSION_SORT_KEY.get(tipo, 99)
    categoria = format_categoria_name(" - ".join(parts[:-1]))
    return (categoria, tipo, sort_key)

def get_category_sort_key(categoria):
    c = categoria.lower()
    order = {
        "115cc elite": 0,
        "115cc infantil": 1,
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

def normalize_numero(num):
    return re.sub(r"\s+", "", str(num or "").strip()).upper()

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

def remove_clase_column(headers, rows):
    idx = gmx.find_col_index(headers, ("clase", "categoría", "categoria"))
    if idx < 0:
        return headers, rows
    h_out = headers[:idx] + headers[idx + 1:]
    r_out = [r[:idx] + r[idx + 1:] if len(r) > idx else r for r in rows]
    return h_out, r_out

def remove_comentario_column_and_collect(headers, rows):
    idx = gmx.find_col_index(headers, ("comentario", "comentarios", "nota", "notas"))
    if idx < 0:
        return headers, rows, [""] * len(rows)
    comentarios = [r[idx].strip() if len(r) > idx and r[idx] else "" for r in rows]
    h_out = headers[:idx] + headers[idx + 1:]
    r_out = [r[:idx] + r[idx + 1:] if len(r) > idx else r for r in rows]
    return h_out, r_out, comentarios

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

def _load_femenina_race_reduced():
    """Datos oficiales completos de Carrera Femenina desde FEMENINA - CARRERA - RaceReduced.pdf."""
    expertas_rows = [
        ["1", "46", "Maria Paula ARIAS MEDINA", "15", "1:10.536", "", "Meta", "CLUB DE MOTOCICLISMO SANTIHC 146", "8", "9:37.220"],
        ["2", "156", "Karen Tatiana REYES LAMPREA", "13", "1:10.806", "0.536", "Bogotá D.C.", "Racing pilots Academy", "8", "9:37.756"],
        ["3", "290", "DANIELA TRIANA GIL", "11", "1:10.598", "0.823", "Bogotá D.C.", "Racing pilots Academy", "8", "9:38.043"],
        ["4", "546", "Katherin TORO FORERO", "10", "1:10.063", "1.143", "Tolima", "CLUB PISTON RACING", "8", "9:38.363"],
        ["5", "572", "Valeria MUÑOZ MORALES", "9", "1:10.361", "2.262", "Bogotá D.C.", "Racing pilots Academy", "8", "9:39.482"],
        ["6", "591", "Paula Fernanda PEÑA HERNANDEZ", "8", "1:12.172", "13.911", "Tolima", "CLUB PISTON RACING", "8", "9:51.131"],
        ["7", "868", "Liz Dayana LUNA GUTIERREZ", "7", "1:12.899", "20.920", "Cundinamarca", "CLUB GIRARDOT RACING", "8", "9:58.140"],
        ["8", "974", "Angie Carolina MUJICA PAEZ", "6", "1:13.785", "28.182", "Quindío", "CLUB MONSTER GARAGE", "8", "10:05.402"],
        ["9", "271", "Paula Andrea URREGO ARIAS", "5", "1:16.239", "46.777", "Cundinamarca", "CLUB GIRARDOT RACING", "8", "10:23.997"],
        ["NT", "371", "Edna Lizeth ESCOBAR CORTES", "0", "", "NT", "Cundinamarca", "CLUB IGUANA RACING GIRARDOT", "0", "7.197"],
    ]
    novatas_rows = [
        ["1", "399", "Angela Yiseth OTERO BECERRA", "15", "1:13.688", "", "Cundinamarca", "", "8", "10:02.956"],
        ["2", "225", "Laura Sofia BARRERA ACUÑA", "13", "1:14.577", "3.891", "Cundinamarca", "", "8", "10:06.847"],
        ["3", "997", "Laura Camila Castaño Vasquez", "11", "1:13.765", "4.357", "Cundinamarca", "", "8", "10:07.313"],
        ["4", "916", "Laura Sofía Barahona porras", "10", "1:13.727", "5.523", "Bogotá D.C.", "", "8", "10:08.479"],
        ["5", "58", "Maroly Nicole BASABE", "9", "1:14.721", "6.465", "Tolima", "", "8", "10:09.421"],
        ["6", "253", "Nicolle Vanessa DIAZ LOPEZ", "8", "1:15.637", "15.308", "Tolima", "", "8", "10:18.264"],
        ["7", "236", "Andrea Muñoz Melo", "7", "1:15.024", "17.346", "Tolima", "", "8", "10:20.302"],
        ["8", "247", "Angie Valentina Bayona Rodriguez", "6", "1:16.061", "20.590", "Tolima", "", "8", "10:23.546"],
        ["9", "405", "Erika Milena OVALLE OCHOA", "5", "1:16.229", "21.268", "Tolima", "", "8", "10:24.224"],
        ["10", "678", "Lizeth Johanna CARVAJALINO VASQUEZ", "4", "1:16.248", "26.161", "Tolima", "", "8", "10:29.117"],
        ["11", "318", "Manuela MORENO ESPINEL", "3", "1:19.171", "42.520", "Tolima", "", "8", "10:45.476"],
        ["12", "446", "Diana Katherine PEÑA VILLALBA", "2", "1:19.119", "45.940", "Bogotá D.C.", "", "8", "10:48.896"],
        ["13", "173", "Sinndy Cristina Arias Romero", "1", "1:21.385", "1 Vuelta", "Tolima", "", "7", "9:38.505"],
        ["14", "821", "Karen Sofía Muñoz Sanabria", "1", "1:25.564", "1 Vuelta", "Bogotá D.C.", "", "7", "10:00.451"],
        ["15", "529", "Maria Fernanda JIMENEZ VILLALBA", "1", "1:20.089", "1 Vuelta", "Tolima", "", "7", "10:57.474"],
        ["NT", "376", "Laura Sabhina Franco Gonzalez", "0", "1:14.836", "NT", "Tolima", "", "6", "7:39.576"],
        ["NT", "924", "LAURA SOFIA TAPIAS COCA", "0", "1:15.884", "NT", "Santander", "", "6", "7:45.037"],
        ["NT", "762", "Valeria ALVAREZ ALZATE", "0", "", "NT", "Cundinamarca", "", "0", "9.016"],
    ]
    headers = ["Pos.", "N°", "Nombre", "Puntos", "Mejor tm", "Dif. resp. 1°", "Liga", "Club", "Vueltas", "Total t°"]
    return headers, expertas_rows, novatas_rows

def _load_super_stock_1000_carrera():
    """Datos reconstruidos de Carrera Super Stock 1000 desde SUPER STOCK - 600 Y 1000 - CARRERA - Laptimes.pdf."""
    headers = ["Pos.", "N°", "Nombre", "Puntos", "Moto", "Liga", "Club", "Dif. resp. 1°", "Mejor tm", "Vueltas", "Total t°"]
    rows = [
        ["1", "46", "Maria Paula ARIAS MEDINA", "15", "Ducati", "Meta", "CLUB DE MOTOCICLISMO SANTIHC 146", "", "1:02.825", "9", "10:07.330"],
        ["2", "244", "Andrés Felipe Aldana jaramillo", "13", "Yamaha", "Quindío", "CLUB MONSTER GARAGE", "2.593", "1:02.766", "9", "10:09.923"],
        ["3", "930", "George Michael herrera Trujillo", "11", "BMW", "Quindío", "CLUB DISCOVER QUINDIO", "4.813", "1:03.291", "9", "10:12.143"],
        ["4", "131", "Christian Andres RUBIO PARDO", "10", "Kawasaki", "Cundinamarca", "CLUB IGUANA RACING GIRARDOT", "5.199", "1:03.291", "9", "10:12.529"],
        ["5", "558", "Fabian Yesid SANABRIA ZEA", "9", "Kawasaki", "Bogotá D.C.", "Racing pilots Academy", "16.813", "1:04.550", "9", "10:24.143"],
        ["6", "964", "Daniel Alberto Castro Hurtado", "8", "Ducati", "Bogotá D.C.", "Xspeed Racing", "20.786", "1:04.718", "9", "10:28.116"],
        ["7", "573", "Vicente Arturo Parada Reyes", "7", "BMW", "Bogotá D.C.", "Todo terreno track", "21.044", "1:04.743", "9", "10:28.374"],
        ["8", "698", "Luis Felipe Patino Lopez", "6", "Aprilia", "Bogotá D.C.", "Racing pilots Academy", "22.261", "1:03.743", "9", "10:29.591"],
        ["9", "879", "Sergio David PACHÓN GARZÓN", "5", "Aprilia", "Bogotá D.C.", "Racing pilots Academy", "26.014", "1:05.122", "9", "10:33.344"],
        ["10", "393", "daniel alejandro gomez narvaez", "4", "BMW", "Bogotá D.C.", "", "36.307", "1:06.336", "9", "10:43.637"],
        ["11", "280", "Christian David POSADA GONZALEZ", "3", "HONDA", "Santander", "", "1 Vuelta", "1:12.861", "8", "10:14.212"],
        ["NT", "293", "Fenky Jhoan Infante carmona", "0", "BMW", "Bogotá D.C.", "Racing pilots Academy", "NT", "1:03.882", "4", "4:51.726"],
    ]
    return headers, rows

def _load_xbikes_a_carrera():
    """Datos reconstruidos de Carrera X-Bikes A desde X-BIKES A Y B - CARRERA - Laptimes.pdf."""
    headers = ["Pos.", "N°", "Nombre", "Puntos", "Moto", "Liga", "Club", "Dif. resp. 1°", "Mejor tm", "Vueltas", "Total t°"]
    rows = [
        ["1", "531", "Sebastian HERRERA HERRERA", "15", "BMW", "Antioquia", "CLUB ANTIOQUIA 2 RUEDAS RACER", "", "58.245", "8", "7:51.372"],
        ["2", "9", "Christian Fernando MEJIA ALFONSO", "13", "Yamaha", "Santander", "CLUB DEPORTIVO SANTANDER MAX EXTREMO", "4.740", "58.766", "8", "7:56.112"],
        ["3", "422", "Sebastian ROMAN GARCIA", "11", "BMW", "Antioquia", "CLUB ANTIOQUIA 2 RUEDAS RACER", "5.529", "58.749", "8", "7:56.901"],
        ["4", "381", "Juan Felipe CHU OCHOA", "10", "Honda", "Bogotá D.C.", "Xspeed Racing", "30.962", "1:00.881", "8", "8:22.334"],
        ["5", "816", "Ronald ARISTIZABAL", "9", "Kawasaki", "VALLE", "Team Potenza", "39.401", "1:02.617", "8", "8:30.773"],
        ["6", "601", "Guido Alexander MORENO PARDO", "8", "BMW", "Cauca", "CLUB CORONA CLUB XTREME PARK", "43.630", "1:03.572", "8", "8:35.002"],
        ["7", "264", "Bryan Steven MANTILLA VALENCIA", "7", "BMW", "Valle del Cauca", "Team Potenza", "49.414", "1:02.904", "8", "8:40.786"],
        ["NT", "51", "Pablo SAENZ MORALES", "0", "BMW", "Bogotá D.C.", "Todo terreno track", "NT", "58.236", "2", "1:58.436"],
    ]
    return headers, rows

def load_categorias_data():
    categorias_data = {}
    femenina_clasif = None
    super_stock_clasif = None
    escuela_c1 = None
    escuela_c2 = None
    escuela_practicas = []

    for filename in os.listdir(FILES_DIR):
        if not filename.lower().endswith(".csv") or filename.lower().startswith("desktop"):
            continue
        filepath = os.path.join(FILES_DIR, filename)
        if not os.path.isfile(filepath):
            continue
        
        # Omitir 115cc Inicio a petición del usuario
        if "115cc inicio" in filename.lower():
            continue
        
        headers_raw, rows_raw = parse_csv(filepath)
        categoria, tipo, sort_key = parse_filename(filename)
        
        # Manejo Femenina
        if categoria.lower() == "femenina":
            if tipo == "Clasificatoria":
                headers, rows, comentarios = remove_comentario_column_and_collect(headers_raw, rows_raw)
                headers, rows = remove_clase_column(headers, rows)
                femenina_clasif = (tipo, sort_key, [format_header(h) for h in headers], rows, comentarios)
            continue
        
        # Manejo Super Stock
        if _fold_accents(categoria).lower() == COMBINED_SUPER_STOCK or "super stock" in categoria.lower():
            if tipo == "Clasificatoria":
                super_stock_clasif = (headers_raw, rows_raw)
                continue
            if tipo == "Carrera":
                # Super Stock 600 carrera proviene de este CSV
                headers, rows, comentarios = remove_comentario_column_and_collect(headers_raw, rows_raw)
                headers, rows = remove_clase_column(headers, rows)
                categorias_data.setdefault(SUPER_STOCK_600, []).append(
                    (tipo, sort_key, [format_header(h) for h in headers], rows, comentarios)
                )
                continue
        
        # Manejo X-Bikes
        if _is_combined_xbikes(categoria):
            if tipo == "Carrera":
                headers, rows, comentarios = remove_comentario_column_and_collect(headers_raw, rows_raw)
                headers, rows = remove_clase_column(headers, rows)
                categorias_data.setdefault(X_BIKES_B, []).append(
                    (tipo, sort_key, [format_header(h) for h in headers], rows, comentarios)
                )
                continue
        
        # Manejo Escuela Fedemoto
        if categoria == ESCUELA_FEDEMOTO:
            headers, rows, comentarios = remove_comentario_column_and_collect(headers_raw, rows_raw)
            headers, rows = remove_clase_column(headers, rows)
            # filtrar pilotos privados vacios
            rows = [r for r in rows if len(r) > 1 and r[1].strip() and r[1].strip() != "518"]
            comentarios = comentarios[:len(rows)]
            h_clean = [format_header(h) for h in headers]
            categorias_data.setdefault(ESCUELA_FEDEMOTO, []).append(
                (tipo, sort_key, h_clean, rows, comentarios)
            )
            continue
        
        headers, rows, comentarios = remove_comentario_column_and_collect(headers_raw, rows_raw)
        if tipo == "Final":
            headers, rows = gmx.remove_fnrh_column(headers, rows)
        headers = [format_header(h) for h in headers]
        categorias_data.setdefault(categoria, []).append(
            (tipo, sort_key, headers, rows, comentarios)
        )

    # 1. Integrar Femenina
    if femenina_clasif:
        categorias_data[FEMENINA] = [femenina_clasif]
    
    fem_headers, fem_exp_rows, fem_nov_rows = _load_femenina_race_reduced()
    categorias_data.setdefault(FEMENINA_EXPERTAS, []).append(
        ("Carrera", SESSION_SORT_KEY["Carrera"], fem_headers, fem_exp_rows, [""] * len(fem_exp_rows))
    )
    categorias_data.setdefault(FEMENINA_NOVATAS, []).append(
        ("Carrera", SESSION_SORT_KEY["Carrera"], fem_headers, fem_nov_rows, [""] * len(fem_nov_rows))
    )

    # 2. Integrar Super Stock 1000 Carrera
    ss_1000_h, ss_1000_r = _load_super_stock_1000_carrera()
    categorias_data.setdefault(SUPER_STOCK_1000, []).append(
        ("Carrera", SESSION_SORT_KEY["Carrera"], ss_1000_h, ss_1000_r, [""] * len(ss_1000_r))
    )

    # 3. Integrar Super Stock Clasificatoria (división por número)
    if super_stock_clasif:
        h_raw, r_raw = super_stock_clasif
        idx_num = gmx.find_col_index(h_raw, ("n°", "nº", "numero", "n"))
        idx_pos = gmx.find_col_index(h_raw, ("pos.", "pos"))
        rows_600 = []
        rows_1000 = []
        for r in r_raw:
            if idx_num >= 0 and idx_num < len(r):
                num = normalize_numero(r[idx_num])
                if num in SS_600_NUMEROS:
                    rows_600.append(list(r))
                elif num in SS_1000_NUMEROS:
                    rows_1000.append(list(r))
        h_clean = [format_header(h) for h in h_raw]
        rows_600 = renumber_positions_rows(rows_600, idx_pos)
        rows_1000 = renumber_positions_rows(rows_1000, idx_pos)
        categorias_data.setdefault(SUPER_STOCK_600, []).append(
            ("Clasificatoria", SESSION_SORT_KEY["Clasificatoria"], h_clean, rows_600, [""] * len(rows_600))
        )
        categorias_data.setdefault(SUPER_STOCK_1000, []).append(
            ("Clasificatoria", SESSION_SORT_KEY["Clasificatoria"], h_clean, rows_1000, [""] * len(rows_1000))
        )

    # 4. Integrar X-Bikes A Carrera
    xb_a_h, xb_a_r = _load_xbikes_a_carrera()
    categorias_data.setdefault(X_BIKES_A, []).append(
        ("Carrera", SESSION_SORT_KEY["Carrera"], xb_a_h, xb_a_r, [""] * len(xb_a_r))
    )

    # Ordenar sesiones dentro de cada categoría
    for cat in categorias_data:
        categorias_data[cat].sort(key=lambda x: (SESSION_SORT_KEY.get(x[0], 99), x[0]))

    return categorias_data

def sort_tablas(tablas):
    return sorted(tablas, key=lambda t: (SESSION_SORT_KEY.get(t[0], 99), t[0]))

def pick_main_session(tablas, final_data, clasif_final_data, clasif_data, carrera_data, c1_data, c2_data):
    if final_data:
        return "Final", final_data
    if clasif_final_data:
        return "Clasificación final", clasif_final_data
    for t in tablas:
        if t[0] == "I Válida":
            return "I Válida", (t[1], t[2], t[3])
    if c1_data and c2_data:
        return "Carrera 1", c1_data
    if carrera_data:
        return "Carrera", carrera_data
    if clasif_data:
        return "Clasificatoria", clasif_data
    if tablas:
        return tablas[0][0], (tablas[0][1], tablas[0][2], tablas[0][3])
    return None, None

def find_mejor_tm_index(headers):
    fallback = -1
    for i, h in enumerate(headers):
        hl = h.lower()
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
    elif re.match(r'^\d{1,2}\.\d+$', t):
        return float(t)
    return None

def escape_html(text):
    return html.escape(str(text)) if text else ""

def tipo_gp(last_part, format_categoria_name_fn):
    s = str(last_part).lower().strip()
    if "clasificacion final" in s or "clasificatoria final" in s:
        return "Clasificación final"
    if s == "final" or (s.endswith("final") and "clasific" not in s):
        return "Final"
    if "ii practica" in s or "segunda practica" in s:
        return "Práctica clasificatoria 2"
    if "practica" in s or "primera practica" in s:
        return "Clasificatoria"
    if re.search(r"carrera\s*1", s) or re.search(r"^1\s*carrera", s) or s in ("i val", "i valida"):
        return "Carrera 1"
    if re.search(r"carrera\s*2", s) or re.search(r"^2\s*carrera", s) or s in ("ii val", "ii valida"):
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
    # Soporte para archivos RaceReduced
    for fn in os.listdir(pdf_dir):
        if not fn.lower().endswith(".pdf"):
            continue
        stem = fn[:-4]
        if re.search(r"RaceReduced", stem, re.I):
            clean_stem = re.sub(r"\s*-\s*RaceReduced\s*$", "", stem, flags=re.I).strip()
            parts = [p.strip() for p in re.split(r"\s+-\s+", clean_stem, flags=re.I) if p.strip()]
            if len(parts) >= 2:
                cat_part = " - ".join(parts[:-1])
                categoria = format_categoria_name(cat_part)
                tipo = tipo_gp(parts[-1], format_categoria_name)
                m[(categoria.lower(), tipo)] = fn

    # Femenina
    fn_fem = m.get(("femenina", "Carrera"))
    if fn_fem:
        m[(FEMENINA_EXPERTAS.lower(), "Carrera")] = fn_fem
        m[(FEMENINA_NOVATAS.lower(), "Carrera")] = fn_fem
    
    # Super Stock
    fn_ss = m.get((COMBINED_SUPER_STOCK, "Carrera")) or m.get(("super stock 600 y 1000", "Carrera"))
    if not fn_ss:
        for f in os.listdir(pdf_dir):
            if "super stock" in f.lower():
                fn_ss = f
                break
    if fn_ss:
        m[(SUPER_STOCK_600.lower(), "Carrera")] = fn_ss
        m[(SUPER_STOCK_1000.lower(), "Carrera")] = fn_ss

    # X-Bikes
    fn_xb = m.get((COMBINED_X_BIKES, "Carrera")) or m.get(("x bikes a y b", "Carrera"))
    if not fn_xb:
        for f in os.listdir(pdf_dir):
            if "x-bikes" in f.lower() or "x bikes" in f.lower():
                fn_xb = f
                break
    if fn_xb:
        m[(X_BIKES_A.lower(), "Carrera")] = fn_xb
        m[(X_BIKES_B.lower(), "Carrera")] = fn_xb

    # Escuela Fedemoto
    for f in os.listdir(pdf_dir):
        fl = f.lower()
        if "minibike fedemoto" in fl or "escuela fedemoto" in fl:
            if "ii val" in fl:
                m[(ESCUELA_FEDEMOTO.lower(), "II Válida")] = f
                m[(ESCUELA_FEDEMOTO.lower(), "II Valida")] = f
                m[(ESCUELA_FEDEMOTO.lower(), "ii válida")] = f
                m[(ESCUELA_FEDEMOTO.lower(), "ii valida")] = f
            elif "i val" in fl:
                m[(ESCUELA_FEDEMOTO.lower(), "I Válida")] = f
                m[(ESCUELA_FEDEMOTO.lower(), "I Valida")] = f
                m[(ESCUELA_FEDEMOTO.lower(), "i válida")] = f
                m[(ESCUELA_FEDEMOTO.lower(), "i valida")] = f

    # Cuatrimotard (II + III GP)
    for ses in ("Carrera 1", "Carrera 2", "Final", "Clasificatoria"):
        fn = m.get(("cuatrimotard", ses))
        if fn:
            m[(CUATRIMOTARD.lower(), ses)] = fn

    # Supermoto Metzeler
    for sub, raw_name in (
        (SUPERMOTO_EXP_METZELER, "supermoto expertos"),
        (SUPERMOTO_NOV_METZELER, "supermoto novatos"),
    ):
        for ses in ("Carrera 1", "Carrera 2"):
            fn = m.get((raw_name, ses))
            if fn:
                m[(sub.lower(), ses)] = fn
    
    # Suzuki GSX R/S 150
    fn_suzuki = m.get(("suzuki", "Carrera"))
    if fn_suzuki:
        m[(SUZUKI_GSX.lower(), "Carrera")] = fn_suzuki

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
        headers, rows = data[0], data[1]
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
                c1 = (headers, rows, comentarios)
            elif tipo == "Carrera 2":
                c2 = (headers, rows, comentarios)
        main_tipo, _ = pick_main_session(tablas, fd, cf, cl, cr, c1, c2)
        section_id = slugify(f"{categoria} {main_tipo}" if main_tipo else f"{categoria} final")
        categorias_para_html.append((categoria, section_id, tablas))
    
    html_content = '''<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>II Válida GP Colombia - Gran Premio BMW | FEDEMOTO</title>
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
            <h1>II Válida GP Colombia</h1>
            <p>Gran Premio BMW — Resultados por categoría</p>
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
                c1_data = (headers, rows, comentarios)
            elif tipo == "Carrera 2":
                c2_data = (headers, rows, comentarios)
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

def _pick_main_session_items(items):
    tipos = {canonical_session_tipo(x[0]) for x in items}
    has_two_races = "Carrera 1" in tipos and "Carrera 2" in tipos
    priority = ["Final"] if has_two_races else ["Carrera", "I Válida", "II Válida"]

    by_tipo = defaultdict(list)
    for item in items:
        by_tipo[canonical_session_tipo(item[0])].append(item)

    for tipo in priority:
        for _, _, headers, rows, _ in by_tipo.get(tipo, []):
            idx = _find_stats_indexes(headers)
            if idx["numero"] is None:
                continue
            if idx["puntos"] is not None:
                return headers, rows, "puntos"
            if idx["pos"] is not None:
                return headers, rows, "position"
    return None, None, None

def _pick_main_session_items_informe(items):
    tipos = {canonical_session_tipo(x[0]) for x in items}
    has_two_races = "Carrera 1" in tipos and "Carrera 2" in tipos
    if has_two_races:
        priority = ["Final", "Clasificación final", "Carrera 1", "Clasificatoria"]
    else:
        priority = ["Carrera", "I Válida", "II Válida", "Clasificación final", "Clasificatoria", "Final"]

    by_tipo = defaultdict(list)
    for item in items:
        by_tipo[canonical_session_tipo(item[0])].append(item)

    for tipo in priority:
        for _, _, headers, rows, _ in by_tipo.get(tipo, []):
            idx = _find_stats_indexes(headers)
            if idx["numero"] is not None:
                return headers, rows, "raw"
    return None, None, None

def _export_valida_rows(files_dir, pick_session_fn):
    categorias = load_categorias_data()
    out = {}
    for categoria, items in categorias.items():
        headers, rows, mode = pick_session_fn(items)
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
            if not numero or numero == "518":
                continue
            pts = 0.0
            if mode == "puntos" and idx["puntos"] is not None and idx["puntos"] < len(row):
                try:
                    pts = float(re.search(r"-?\d+(\.\d+)?", str(row[idx["puntos"]]).replace(",", ".")).group(0))
                except Exception:
                    pts = 0.0
            cat_rows.append({
                "numero": numero,
                "nombre": str(row[idx["nombre"]]).strip() if idx["nombre"] is not None and idx["nombre"] < len(row) else "",
                "liga": str(row[idx["liga"]]).strip() if idx["liga"] is not None and idx["liga"] < len(row) else "",
                "club": str(row[idx["club"]]).strip() if idx["club"] is not None and idx["club"] < len(row) else "",
                "moto": str(row[idx["moto"]]).strip() if idx["moto"] is not None and idx["moto"] < len(row) else "",
                "clase": "",
                "puntos": pts,
            })
        if cat_rows:
            out[categoria] = cat_rows
    return out

def _load_escuela_val_rows(filename):
    path = os.path.join(FILES_DIR, filename)
    if not os.path.exists(path):
        return []
    headers, rows = parse_csv(path)
    idx_num = gmx.find_col_index(headers, ("n°", "nº", "numero", "n"))
    idx_nom = gmx.find_col_index(headers, ("nombre",))
    idx_pts = gmx.find_col_index(headers, ("puntos", "total puntos"))
    idx_liga = gmx.find_col_index(headers, ("liga",))
    idx_club = gmx.find_col_index(headers, ("club",))
    idx_moto = gmx.find_col_index(headers, ("moto",))
    out = []
    for r in rows:
        if len(r) <= max(idx_num, idx_nom):
            continue
        num = str(r[idx_num]).strip()
        if not num or num == "518":
            continue
        try:
            pts = float(re.search(r"-?\d+(\.\d+)?", str(r[idx_pts]).replace(",", ".")).group(0)) if idx_pts >= 0 else 0.0
        except Exception:
            pts = 0.0
        out.append({
            "numero": num,
            "nombre": str(r[idx_nom]).strip() if idx_nom >= 0 else "",
            "liga": str(r[idx_liga]).strip() if idx_liga >= 0 and idx_liga < len(r) else "",
            "club": str(r[idx_club]).strip() if idx_club >= 0 and idx_club < len(r) else "",
            "moto": str(r[idx_moto]).strip() if idx_moto >= 0 and idx_moto < len(r) else "",
            "clase": "",
            "puntos": pts,
        })
    return out

def export_escuela_fedemoto_valida_i_rows(files_dir=None):
    global FILES_DIR
    prev = FILES_DIR
    if files_dir:
        FILES_DIR = files_dir
    try:
        return _load_escuela_val_rows("MINIBIKE FEDEMOTO - I VAL - Resultados.csv")
    finally:
        FILES_DIR = prev

def export_escuela_fedemoto_valida_ii_rows(files_dir=None):
    global FILES_DIR
    prev = FILES_DIR
    if files_dir:
        FILES_DIR = files_dir
    try:
        return _load_escuela_val_rows("MINIBIKE FEDEMOTO - II VAL - Resultados.csv")
    finally:
        FILES_DIR = prev

def export_valida_general_rows(files_dir=None):
    return _export_valida_rows(files_dir, _pick_main_session_items)

def export_valida_informe_rows(files_dir=None):
    return _export_valida_rows(files_dir, _pick_main_session_items_informe)

if __name__ == '__main__':
    generate_html()
