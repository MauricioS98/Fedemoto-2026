# -*- coding: utf-8 -*-
"""
Genera el Informe Anual Consolidado FEDEMOTO 2026 (Informes/informe_2026_fedemoto.html)
a partir de los CSVs oficiales de cada válida y las tablas acumuladas de
Resultados generales/generar_resultados_generales.py.

Niveles cubiertos:
1. General Anual 2026 (KPIs, Medallero, Ligas, Categorías Formativas, Femenina, Polivalencia)
2. Por Modalidad (Enduro, GP Colombia, Motocross, Velocidad, Velotierra)
3. Por Campeonato (8 campeonatos con estado Finalizado / En curso)
4. Por Modalidad por Semestre (1S vs 2S para Motocross, Velocidad y Velotierra)
5. Por Semestre en General (Opción A: 3 modalidades semestrales + bloque anual aparte)
6. Inteligencia Comercial (Marcas OEM + podios, Clubes, Sedes/Visitantes, Licencias -E)
"""

import csv
import json
import os
import re
import sys
import unicodedata
from collections import Counter, defaultdict
from datetime import datetime

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.normpath(os.path.join(SCRIPT_DIR, ".."))
GEN_DIR = os.path.join(ROOT_DIR, "Resultados generales")

if GEN_DIR not in sys.path:
    sys.path.insert(0, GEN_DIR)

import generar_resultados_generales as grg  # noqa: E402
from enduro_categorias import canonical_enduro_categoria  # noqa: E402

OUTPUT_HTML = os.path.join(SCRIPT_DIR, "informe_2026_fedemoto.html")

VENUE_META = {
    "I Válida Enduro 2026": ("Tuluá", "Valle del Cauca"),
    "II Válida Enduro - Pasca": ("Pasca", "Cundinamarca"),
    "III Válida Enduro - San Jerónimo": ("San Jerónimo", "Antioquia"),
    "IV Válida Enduro - Salento": ("Salento", "Quindío"),
    "I Válida MX - Girardota": ("Girardota", "Antioquia"),
    "II Válida MX - Barranquilla": ("Barranquilla", "Atlántico"),
    "III Válida MX - Tocancipá": ("Tocancipá", "Cundinamarca"),
    "IV Válida MX - Manizales": ("Manizales", "Caldas"),
    "II Válida MX - Yopal": ("Yopal", "Casanare"),
    "III Válida MX - Villagarzón": ("Villagarzón", "Putumayo"),
    "I Válida Velocidad - Zarzal": ("Zarzal", "Valle del Cauca"),
    "II Válida Velocidad - Chachagüi": ("Chachagüí", "Nariño"),
    "III Válida Velocidad - Popayán": ("Popayán", "Cauca"),
    "I Válida Velocidad - Manizales": ("Manizales", "Caldas"),
    "II Válida Velocidad - Girardot": ("Girardot", "Cundinamarca"),
    "III Válida Velocidad - Rivera": ("Rivera", "Huila"),
    "I Válida VT - Tuluá": ("Tuluá", "Valle del Cauca"),
    "II Válida VT - Barcelona": ("Barcelona", "Quindío"),
    "III Válida VT - Ibagué": ("Ibagué", "Tolima"),
    "I Válida VT - Villa Garzón": ("Villagarzón", "Putumayo"),
    "II Válida VT - Popayán": ("Popayán", "Cauca"),
    "III Válida VT - Cartago": ("Cartago", "Valle del Cauca"),
    "I Válida GP Colombia - Gran Premio Vitrix": ("Tocancipá", "Cundinamarca"),
    "II Válida GP Colombia - Gran Premio BMW": ("Tocancipá", "Cundinamarca"),
}

CANONICAL_LIGAS = {
    "ANTIOQUIA": "Antioquia",
    "ARAUCA": "Arauca",
    "ATLANTICO": "Atlántico",
    "BOGOTA": "Bogotá",
    "BOGOTADC": "Bogotá",
    "BOLIVAR": "Bolívar",
    "BOYACA": "Boyacá",
    "CALDAS": "Caldas",
    "CAQUETA": "Caquetá",
    "CASANARE": "Casanare",
    "CAUCA": "Cauca",
    "CESAR": "Cesar",
    "CHOCO": "Chocó",
    "CORDOBA": "Córdoba",
    "COSTARICA": "Costa Rica",
    "CUNDINAMARCA": "Cundinamarca",
    "GUAVIARE": "Guaviare",
    "HUILA": "Huila",
    "LAGUAJIRA": "La Guajira",
    "MAGDALENA": "Magdalena",
    "META": "Meta",
    "NARINO": "Nariño",
    "NORTEDESANTANDER": "Norte de Santander",
    "PUTUMAYO": "Putumayo",
    "QUINDIO": "Quindío",
    "QUNDIO": "Quindío",
    "RISARALDA": "Risaralda",
    "SANTANDER": "Santander",
    "SUCRE": "Sucre",
    "TOLIMA": "Tolima",
    "TOLIMADEPARTAMENTAL": "Tolima",
    "VALLE": "Valle del Cauca",
    "VALLEDELCAUCA": "Valle del Cauca",
    "VALLEDELCAUCADEPARTAMENTAL": "Valle del Cauca",
}

MARCA_MAP = {
    "AKT": "AKT",
    "APRILIA": "Aprilia",
    "APRILLA": "Aprilia",
    "BMW": "BMW",
    "BAJAJ": "Bajaj",
    "BETA": "Beta",
    "COBRA": "Cobra",
    "DUCATI": "Ducati",
    "GASGAS": "GasGas",
    "HERO": "Hero",
    "HONDA": "Honda",
    "HUSQ": "Husqvarna",
    "HUSQVARN": "Husqvarna",
    "HUSQVARNA": "Husqvarna",
    "KTM": "KTM",
    "KAWASAKI": "Kawasaki",
    "KYMCO": "Kymco",
    "LGPMOBILITY": "LGP Mobility",
    "SHERCO": "Sherco",
    "SUZUKI": "Suzuki",
    "TVS": "TVS",
    "TRIUMPH": "Triumph",
    "UNITEMOTOR": "Unite Motor",
    "VICTORY": "Victory",
    "YAMAHA": "Yamaha",
    "YCF": "YCF",
}

FORMATIVE_KEYWORDS = (
    "50cc", "65cc", "85cc", "infantil", "juvenil", "escuela", "junior", "pit bike infantil"
)
FEMENINA_KEYWORDS = ("femenin",)


def strip_accents(text):
    return "".join(
        c for c in unicodedata.normalize("NFD", str(text or "")) if unicodedata.category(c) != "Mn"
    )


def key_alnum(text):
    s = str(text or "").replace("Ã\x8d", "I").replace("Ã\xad", "i").replace("Ã³", "o").replace("Ã±", "n")
    s = strip_accents(s).upper()
    return re.sub(r"[^A-Z0-9]", "", s)


def clean_liga(raw):
    s = str(raw or "").strip()
    if not s or s in ("-", "--", "N/A", "SIN LIGA"):
        return ""
    k = key_alnum(s)
    if k in CANONICAL_LIGAS:
        return CANONICAL_LIGAS[k]
    return ""


def clean_marca(raw):
    s = str(raw or "").strip()
    if not s or s in ("-", "--", "N/A"):
        return ""
    k = key_alnum(s)
    if k in MARCA_MAP:
        return MARCA_MAP[k]
    return s.title()


def clean_club(raw):
    s = " ".join(str(raw or "").strip().split())
    if not s:
        return ""
    u = s.upper()
    if u in ("-", "--", "N/A", "SIN CLUB", "LISTO PILOTO", "SE82", "SANITAS", "NUEVA EPS", "ALIANSALUD"):
        return ""
    if key_alnum(s) in CANONICAL_LIGAS:
        return ""
    words = []
    for w in s.split():
        wu = w.upper()
        if wu in ("JHC", "GR", "BMW", "MX", "VT", "JP36", "XTREM"):
            words.append(wu if wu != "XTREM" else "Xtrem")
        elif re.match(r"^[A-Z]+\d+$", wu):
            words.append(wu)
        else:
            words.append(w[0].upper() + w[1:].lower() if len(w) > 1 else wu)
    out = " ".join(words)
    out = out.replace("Rancing", "Racing")
    return out


def canonical_categoria(modalidad, cat_raw):
    c = str(cat_raw or "").strip()
    if modalidad == "Enduro":
        c = canonical_enduro_categoria(c)
    elif modalidad == "Velotierra":
        c = grg.canonical_velotierra_categoria(c)
    elif modalidad == "GP Colombia":
        k = c.lower()
        if "supermoto expertos" in k:
            c = "Supermoto Expertos Metzeler"
        elif "supermoto novatos" in k:
            c = "Supermoto Novatos Metzeler"
        elif k in ("minibike fedemoto", "escuela fedemoto"):
            c = "Escuela Fedemoto"
        elif "cuatrimotard" in k:
            c = "Cuatrimotard (II + III GP)"
    return grg.pretty_categoria(c)


def is_excluded_non_category(modalidad, cat_name):
    # En Enduro, Scratch es una tabla general absoluta combinada, no una categoría independiente
    return modalidad == "Enduro" and strip_accents(cat_name).strip().lower() == "scratch"


def is_formative_cat(cat_name):
    cl = strip_accents(cat_name).lower()
    return any(kw in cl for kw in FORMATIVE_KEYWORDS)


def is_femenina_cat(cat_name):
    cl = strip_accents(cat_name).lower()
    return any(kw in cl for kw in FEMENINA_KEYWORDS)


def rider_uid(nombre, numero, liga):
    nk = grg.normalize_rider_name(nombre)
    if nk:
        return nk
    return f"__NUM_{str(numero).strip()}_{key_alnum(liga)}"


def build_global_rider_metadata():
    """Escanea todos los CSVs de 2026 para crear un índice maestro limpio por nombre normalizado."""
    meta_by_name = {}
    for champ in grg.CHAMPIONSHIPS:
        for v in champ["validas"]:
            files_dir = v["files_dir"]
            if not os.path.isdir(files_dir):
                continue
            for fn in os.listdir(files_dir):
                if not fn.lower().endswith(".csv"):
                    continue
                path = os.path.join(files_dir, fn)
                with open(path, "r", encoding="utf-8-sig", errors="ignore", newline="") as f:
                    lines = f.read().splitlines()
                if not lines:
                    continue
                delim = grg.csv_delimiter_from_first_line(lines[0])
                rows = list(csv.reader(lines, delimiter=delim))
                if not rows:
                    continue
                idx = grg.find_indexes(rows[0])
                for r in rows[1:]:
                    nom = str(r[idx["nombre"]]).strip() if idx["nombre"] is not None and idx["nombre"] < len(r) else ""
                    nk = grg.normalize_rider_name(nom)
                    if not nk:
                        continue
                    entry = meta_by_name.setdefault(nk, {"nombre": nom, "liga": "", "club": "", "moto": ""})
                    if len(nom) > len(entry["nombre"]):
                        entry["nombre"] = nom
                    if idx["liga"] is not None and idx["liga"] < len(r):
                        lv = clean_liga(r[idx["liga"]])
                        if lv and not entry["liga"]:
                            entry["liga"] = lv
                        if not lv and r[idx["liga"]].strip().upper().startswith("CLUB") and not entry["club"]:
                            cv_alt = clean_club(r[idx["liga"]])
                            if cv_alt:
                                entry["club"] = cv_alt
                    if idx["club"] is not None and idx["club"] < len(r):
                        cv = clean_club(r[idx["club"]])
                        if cv and not entry["club"]:
                            entry["club"] = cv
                    if idx["moto"] is not None and idx["moto"] < len(r):
                        mv = clean_marca(r[idx["moto"]])
                        if mv and not entry["moto"]:
                            entry["moto"] = mv

    if "samuelvargasome" in meta_by_name:
        sv = meta_by_name.setdefault("samuelvargas", dict(meta_by_name["samuelvargasome"]))
        sv["moto"] = "YCF"
    return meta_by_name


def parse_valida_raw_stats(champ, valida_cfg, global_meta):
    modalidad = champ["modalidad"]
    files_dir = valida_cfg["files_dir"]
    exclude_nums = set(str(n).strip() for n in champ.get("exclude_pilotos_recalcular", []))

    by_cat_files = defaultdict(list)
    folder_meta_num = {}
    folder_meta_name = {}

    for fn in os.listdir(files_dir):
        if not fn.lower().endswith(".csv"):
            continue
        filename = fn[:-4]
        if not filename.endswith(" - Resultados") and not filename.lower().endswith(" - resultados"):
            continue
        cat_raw, tipo = grg.parse_filename(filename)
        cat = canonical_categoria(modalidad, cat_raw)
        if is_excluded_non_category(modalidad, cat):
            continue
        path = os.path.join(files_dir, fn)
        by_cat_files[cat].append((tipo, path))

        with open(path, "r", encoding="utf-8-sig", errors="ignore", newline="") as fp:
            lines = fp.read().splitlines()
        if not lines:
            continue
        delim = grg.csv_delimiter_from_first_line(lines[0])
        rows = list(csv.reader(lines, delimiter=delim))
        if not rows:
            continue
        idx = grg.find_indexes(rows[0])
        for r in rows[1:]:
            c_num = str(r[idx["numero"]]).strip() if idx["numero"] is not None and idx["numero"] < len(r) else ""
            c_nom = str(r[idx["nombre"]]).strip() if idx["nombre"] is not None and idx["nombre"] < len(r) else ""
            c_liga = clean_liga(r[idx["liga"]]) if idx["liga"] is not None and idx["liga"] < len(r) else ""
            c_club = clean_club(r[idx["club"]]) if idx["club"] is not None and idx["club"] < len(r) else ""
            c_moto = clean_marca(r[idx["moto"]]) if idx["moto"] is not None and idx["moto"] < len(r) else ""
            for k, target in ((c_num, folder_meta_num), (grg.normalize_rider_name(c_nom), folder_meta_name)):
                if not k:
                    continue
                d = target.setdefault(k, {})
                if c_liga and not d.get("liga"):
                    d["liga"] = c_liga
                if c_club and not d.get("club"):
                    d["club"] = c_club
                if c_moto and not d.get("moto"):
                    d["moto"] = c_moto

    participations = []
    finish_stats = defaultdict(lambda: {"starts": 0, "finished": 0, "dnf": 0})

    for cat, files in by_cat_files.items():
        for tipo, path in files:
            t_low = strip_accents(tipo).lower()
            if "final" in t_low or "practica" in t_low:
                continue
            with open(path, "r", encoding="utf-8-sig", errors="ignore", newline="") as fp:
                lines = fp.read().splitlines()
            if not lines:
                continue
            delim = grg.csv_delimiter_from_first_line(lines[0])
            rows = list(csv.reader(lines, delimiter=delim))
            if not rows:
                continue
            idx = grg.find_indexes(rows[0])
            if idx["pos"] is None or idx["numero"] is None:
                continue
            for r in rows[1:]:
                if len(r) <= max(idx["pos"], idx["numero"]):
                    continue
                num = str(r[idx["numero"]]).strip()
                if not num or num in exclude_nums:
                    continue
                pos_str = str(r[idx["pos"]]).strip().upper()
                finish_stats[cat]["starts"] += 1
                if re.match(r"^\d+$", pos_str):
                    finish_stats[cat]["finished"] += 1
                else:
                    finish_stats[cat]["dnf"] += 1

        seen_in_cat = {}
        main_tipo, main_path = grg.choose_main_file(files)
        ordered_files = [(main_tipo, main_path)] + [x for x in files if x[1] != main_path]
        for tipo, path in ordered_files:
            with open(path, "r", encoding="utf-8-sig", errors="ignore", newline="") as fp:
                lines = fp.read().splitlines()
            if not lines:
                continue
            delim = grg.csv_delimiter_from_first_line(lines[0])
            rows = list(csv.reader(lines, delimiter=delim))
            if not rows:
                continue
            idx = grg.find_indexes(rows[0])
            if idx["numero"] is None:
                continue
            for r in rows[1:]:
                if len(r) <= idx["numero"]:
                    continue
                num = str(r[idx["numero"]]).strip()
                if not num or num in exclude_nums:
                    continue
                nom = str(r[idx["nombre"]]).strip() if idx["nombre"] is not None and idx["nombre"] < len(r) else ""
                raw_l = clean_liga(r[idx["liga"]]) if idx["liga"] is not None and idx["liga"] < len(r) else ""
                raw_c = clean_club(r[idx["club"]]) if idx["club"] is not None and idx["club"] < len(r) else ""
                raw_m = clean_marca(r[idx["moto"]]) if idx["moto"] is not None and idx["moto"] < len(r) else ""

                nk = grg.normalize_rider_name(nom)
                fmeta = folder_meta_num.get(num) or folder_meta_name.get(nk) or {}
                gmeta = global_meta.get(nk) or {}

                liga = raw_l or fmeta.get("liga") or gmeta.get("liga") or ""
                club = raw_c or fmeta.get("club") or gmeta.get("club") or ""
                moto = raw_m or fmeta.get("moto") or gmeta.get("moto") or ""

                if not moto:
                    cl_low = cat.lower()
                    if "suzuki" in cl_low:
                        moto = "Suzuki"
                    elif "yamaha r15" in cl_low:
                        moto = "Yamaha"

                uid = rider_uid(nom, num, liga)
                if uid not in seen_in_cat:
                    seen_in_cat[uid] = {
                        "uid": uid,
                        "numero": num,
                        "nombre": gmeta.get("nombre") or nom or f"Piloto #{num}",
                        "liga": liga,
                        "club": club,
                        "moto": moto,
                        "categoria": cat,
                        "es_evento": num.upper().endswith("-E"),
                    }
                else:
                    cur = seen_in_cat[uid]
                    if liga and not cur["liga"]:
                        cur["liga"] = liga
                    if club and not cur["club"]:
                        cur["club"] = club
                    if moto and not cur["moto"]:
                        cur["moto"] = moto

        participations.extend(seen_in_cat.values())

    return participations, finish_stats


def aggregate_data():
    global_meta = build_global_rider_metadata()

    all_participations = []
    championship_summaries = []
    medallero_global_liga = defaultdict(lambda: {"oro": 0, "plata": 0, "bronce": 0, "total": 0})
    medallero_global_club = defaultdict(lambda: {"oro": 0, "plata": 0, "bronce": 0, "total": 0})
    medallero_global_marca = defaultdict(lambda: {"oro": 0, "plata": 0, "bronce": 0, "total": 0})
    marca_podiums_by_mod = defaultdict(lambda: defaultdict(lambda: {"oro": 0, "plata": 0, "bronce": 0, "total": 0}))
    finish_by_mod_cat = defaultdict(lambda: defaultdict(lambda: {"starts": 0, "finished": 0, "dnf": 0}))

    for champ in grg.CHAMPIONSHIPS:
        cid = champ["id"]
        modalidad = champ["modalidad"]
        semestre_label = champ["campeonato"]
        is_finalized = bool(champ.get("final_valida_bonus", 0) >= 8)
        estado = "Finalizado" if is_finalized else "En curso"

        valida_curves = []
        champ_rider_validas = defaultdict(set)
        champ_participations = []

        for v_idx, v in enumerate(champ["validas"]):
            ciudad, depto = VENUE_META.get(v["label"], (v["label"], ""))
            v_parts, v_finish = parse_valida_raw_stats(champ, v, global_meta)

            for cat, st in v_finish.items():
                finish_by_mod_cat[modalidad][cat]["starts"] += st["starts"]
                finish_by_mod_cat[modalidad][cat]["finished"] += st["finished"]
                finish_by_mod_cat[modalidad][cat]["dnf"] += st["dnf"]

            v_unique_riders = set()
            v_event_riders = set()
            v_visitors = set()
            for p in v_parts:
                rec = {
                    **p,
                    "champ_id": cid,
                    "modalidad": modalidad,
                    "semestre": semestre_label,
                    "valida_idx": v_idx,
                    "valida_label": v["label"],
                    "ciudad": ciudad,
                    "depto_sede": depto,
                }
                all_participations.append(rec)
                champ_participations.append(rec)
                champ_rider_validas[p["uid"]].add(v_idx)
                v_unique_riders.add(p["uid"])
                if p["es_evento"]:
                    v_event_riders.add(p["uid"])
                if depto and p["liga"] and key_alnum(p["liga"]) != key_alnum(depto):
                    v_visitors.add(p["uid"])

            valida_curves.append({
                "label": v["label"],
                "ciudad": ciudad,
                "depto": depto,
                "participaciones": len(v_parts),
                "pilotos_unicos": len(v_unique_riders),
                "evento_unicos": len(v_event_riders),
                "visitantes_pct": round((len(v_visitors) / len(v_unique_riders) * 100), 1) if v_unique_riders else 0.0,
            })

        n_validas = len(champ["validas"])
        retention_counts = Counter(len(vs) for vs in champ_rider_validas.values())
        retention_dist = [
            {"validas_corridas": k, "pilotos": retention_counts.get(k, 0)}
            for k in range(1, n_validas + 1)
        ]

        table = grg.build_general_table(champ)
        champ_med_liga = defaultdict(lambda: {"oro": 0, "plata": 0, "bronce": 0, "total": 0})
        champ_med_club = defaultdict(lambda: {"oro": 0, "plata": 0, "bronce": 0, "total": 0})
        cuadro_honor = []
        parity_gaps = []

        for cat_raw in table.keys():
            rows = table[cat_raw]
            if not rows:
                continue
            cat = canonical_categoria(modalidad, cat_raw)
            if is_excluded_non_category(modalidad, cat):
                continue

            def enrich_row(row):
                nk = grg.normalize_rider_name(row.get("nombre", ""))
                gm = global_meta.get(nk, {})
                return {
                    "numero": row.get("numero", ""),
                    "nombre": gm.get("nombre") or row.get("nombre", "") or f"Piloto #{row.get('numero', '')}",
                    "liga": clean_liga(row.get("liga")) or gm.get("liga") or "Sin Liga",
                    "club": clean_club(row.get("club")) or gm.get("club") or "Sin Club",
                    "moto": clean_marca(row.get("moto")) or gm.get("moto") or "N/D",
                    "total": round(float(row.get("total", 0.0)), 1),
                }

            podium = [enrich_row(r) for r in rows[:3]]
            p1 = podium[0]
            p2 = podium[1] if len(podium) > 1 else None
            p3 = podium[2] if len(podium) > 2 else None

            gap_1_2 = round(p1["total"] - p2["total"], 1) if p2 else None
            gap_1_3 = round(p1["total"] - p3["total"], 1) if p3 else None
            if gap_1_3 is not None and p1["total"] > 0:
                parity_gaps.append({"categoria": cat, "gap_1_3": gap_1_3, "pts_1": p1["total"]})

            cuadro_honor.append({
                "categoria": cat,
                "pilotos": len(rows),
                "p1": p1,
                "p2": p2,
                "p3": p3,
                "gap_1_2": gap_1_2,
                "gap_1_3": gap_1_3,
            })

            for idx_pos, med_key in enumerate(("oro", "plata", "bronce")):
                if idx_pos >= len(podium):
                    break
                pr = podium[idx_pos]
                if pr["liga"] and pr["liga"] != "Sin Liga":
                    champ_med_liga[pr["liga"]][med_key] += 1
                    champ_med_liga[pr["liga"]]["total"] += 1
                    medallero_global_liga[pr["liga"]][med_key] += 1
                    medallero_global_liga[pr["liga"]]["total"] += 1
                if pr["club"] and pr["club"] != "Sin Club":
                    champ_med_club[pr["club"]][med_key] += 1
                    champ_med_club[pr["club"]]["total"] += 1
                    medallero_global_club[pr["club"]][med_key] += 1
                    medallero_global_club[pr["club"]]["total"] += 1
                if pr["moto"] and pr["moto"] != "N/D":
                    medallero_global_marca[pr["moto"]][med_key] += 1
                    medallero_global_marca[pr["moto"]]["total"] += 1
                    marca_podiums_by_mod[modalidad][pr["moto"]][med_key] += 1
                    marca_podiums_by_mod[modalidad][pr["moto"]]["total"] += 1

        cuadro_honor.sort(key=lambda x: (-x["pilotos"], x["categoria"]))
        rel_general = os.path.relpath(champ["output_html"], SCRIPT_DIR).replace("\\", "/")

        championship_summaries.append({
            "id": cid,
            "modalidad": modalidad,
            "semestre": semestre_label,
            "nombre": f"{modalidad} — {semestre_label}",
            "estado": estado,
            "finalizado": is_finalized,
            "validas_count": n_validas,
            "pilotos_unicos": len(champ_rider_validas),
            "participaciones": len(champ_participations),
            "categorias_count": len(cuadro_honor),
            "retencion_completa_pct": round(
                (retention_counts.get(n_validas, 0) / len(champ_rider_validas) * 100), 1
            ) if champ_rider_validas else 0.0,
            "valida_curves": valida_curves,
            "retention_dist": retention_dist,
            "cuadro_honor": cuadro_honor,
            "medallero_ligas": [
                {"nombre": k, **v}
                for k, v in sorted(champ_med_liga.items(), key=lambda x: (-x[1]["oro"], -x[1]["plata"], -x[1]["bronce"], x[0]))
            ],
            "medallero_clubes": [
                {"nombre": k, **v}
                for k, v in sorted(champ_med_club.items(), key=lambda x: (-x[1]["oro"], -x[1]["plata"], -x[1]["bronce"], x[0]))
            ],
            "parity_avg_gap_1_3": round(sum(x["gap_1_3"] for x in parity_gaps) / len(parity_gaps), 1) if parity_gaps else None,
            "url_general": rel_general,
        })

    # === CONSOLIDACIÓN GENERAL ANUAL ===
    all_uids = set(p["uid"] for p in all_participations)
    all_event_uids = set(p["uid"] for p in all_participations if p["es_evento"])
    all_ligas = sorted(set(p["liga"] for p in all_participations if p["liga"]))
    all_clubes = sorted(set(p["club"] for p in all_participations if p["club"]))
    all_marcas = sorted(set(p["moto"] for p in all_participations if p["moto"]))
    all_sedes = sorted(set((p["ciudad"], p["depto_sede"]) for p in all_participations))
    all_validas_set = set((p["modalidad"], p["semestre"], p["valida_label"]) for p in all_participations)

    liga_riders = defaultdict(set)
    liga_parts = defaultdict(int)
    for p in all_participations:
        if p["liga"]:
            liga_riders[p["liga"]].add(p["uid"])
            liga_parts[p["liga"]] += 1

    # Criterio estricto: 1) Oro, 2) Plata, 3) Bronce, 4) Participaciones
    ligas_ranking = []
    for l_name in all_ligas:
        med = medallero_global_liga.get(l_name, {"oro": 0, "plata": 0, "bronce": 0, "total": 0})
        ligas_ranking.append({
            "liga": l_name,
            "pilotos_unicos": len(liga_riders[l_name]),
            "participaciones": liga_parts[l_name],
            "oro": med["oro"],
            "plata": med["plata"],
            "bronce": med["bronce"],
            "podios": med["total"],
        })
    ligas_ranking.sort(key=lambda x: (-x["oro"], -x["plata"], -x["bronce"], -x["participaciones"], x["liga"]))

    # Top Ligas por Pilotos Únicos (para la barra visual de alcance geográfico)
    top_ligas_pilotos = sorted(ligas_ranking, key=lambda x: (-x["pilotos_unicos"], -x["participaciones"]))[:12]

    formative_uids = set(p["uid"] for p in all_participations if is_formative_cat(p["categoria"]))
    femenina_uids = set(p["uid"] for p in all_participations if is_femenina_cat(p["categoria"]))
    formative_parts = sum(1 for p in all_participations if is_formative_cat(p["categoria"]))
    femenina_parts = sum(1 for p in all_participations if is_femenina_cat(p["categoria"]))

    rider_mods = defaultdict(set)
    rider_cats = defaultdict(set)
    rider_info = {}
    rider_total_parts = Counter()
    for p in all_participations:
        uid = p["uid"]
        rider_mods[uid].add(p["modalidad"])
        rider_cats[uid].add(f"{p['modalidad']}: {p['categoria']}")
        rider_total_parts[uid] += 1
        if uid not in rider_info or (p["liga"] and not rider_info[uid]["liga"]):
            rider_info[uid] = {"nombre": p["nombre"], "liga": p["liga"], "club": p["club"]}

    multimodal_count = sum(1 for uid, ms in rider_mods.items() if len(ms) >= 2)
    multicat_count = sum(1 for uid, cs in rider_cats.items() if len(cs) >= 2)
    top_polivalentes = []
    for uid in all_uids:
        if len(rider_mods[uid]) >= 2 or len(rider_cats[uid]) >= 3:
            top_polivalentes.append({
                "nombre": rider_info[uid]["nombre"],
                "liga": rider_info[uid]["liga"] or "Sin Liga",
                "modalidades": sorted(rider_mods[uid]),
                "categorias_count": len(rider_cats[uid]),
                "participaciones": rider_total_parts[uid],
            })
    top_polivalentes.sort(key=lambda x: (-len(x["modalidades"]), -x["categorias_count"], -x["participaciones"]))

    # === POR MODALIDAD ===
    modalidades_list = ["Enduro", "GP Colombia", "Motocross", "Velocidad", "Velotierra"]
    modalidades_data = {}
    for mod in modalidades_list:
        m_parts = [p for p in all_participations if p["modalidad"] == mod]
        m_uids = set(p["uid"] for p in m_parts)
        m_validas = set((p["semestre"], p["valida_label"]) for p in m_parts)

        cat_uids = defaultdict(set)
        cat_parts = defaultdict(int)
        cat_validas = defaultdict(set)
        m_liga_uids = defaultdict(set)
        m_club_uids = defaultdict(set)
        m_marca_parts = Counter()
        m_marca_uids = defaultdict(set)

        for p in m_parts:
            cat_uids[p["categoria"]].add(p["uid"])
            cat_parts[p["categoria"]] += 1
            cat_validas[p["categoria"]].add((p["semestre"], p["valida_label"]))
            if p["liga"]:
                m_liga_uids[p["liga"]].add(p["uid"])
            if p["club"]:
                m_club_uids[p["club"]].add(p["uid"])
            if p["moto"]:
                m_marca_parts[p["moto"]] += 1
                m_marca_uids[p["moto"]].add(p["uid"])

        total_starts = sum(v["starts"] for v in finish_by_mod_cat[mod].values())
        total_finished = sum(v["finished"] for v in finish_by_mod_cat[mod].values())

        cats_detail = []
        for cat in cat_uids.keys():
            if is_excluded_non_category(mod, cat):
                continue
            n_val_cat = len(cat_validas[cat]) or 1
            fst = finish_by_mod_cat[mod].get(cat, {"starts": 0, "finished": 0, "dnf": 0})
            eff = round((fst["finished"] / fst["starts"] * 100), 1) if fst["starts"] else 100.0
            cats_detail.append({
                "categoria": cat,
                "pilotos_unicos": len(cat_uids[cat]),
                "participaciones": cat_parts[cat],
                "grilla_promedio": round(cat_parts[cat] / n_val_cat, 1),
                "efectividad_llegada_pct": eff,
            })
        # Ordenar TODAS las categorías por pilotos únicos (descendente)
        cats_detail.sort(key=lambda x: (-x["pilotos_unicos"], -x["participaciones"], x["categoria"]))

        m_champs = [c for c in championship_summaries if c["modalidad"] == mod]
        m_estado = "Finalizado" if m_champs and all(c["finalizado"] for c in m_champs) else "En curso"

        modalidades_data[mod] = {
            "modalidad": mod,
            "estado": m_estado,
            "validas_count": len(m_validas),
            "pilotos_unicos": len(m_uids),
            "participaciones": len(m_parts),
            "promedio_validas_piloto": round(len(m_parts) / len(m_uids), 2) if m_uids else 0.0,
            "efectividad_general_pct": round((total_finished / total_starts * 100), 1) if total_starts else 100.0,
            "categorias": cats_detail,
            "ligas": [{"nombre": k, "pilotos": len(v)} for k, v in sorted(m_liga_uids.items(), key=lambda x: -len(x[1]))],
            "clubes": [{"nombre": k, "pilotos": len(v)} for k, v in sorted(m_club_uids.items(), key=lambda x: -len(x[1]))[:15]],
            "marcas": [
                {
                    "marca": k,
                    "participaciones": m_marca_parts[k],
                    "pilotos_unicos": len(m_marca_uids[k]),
                    "podios": marca_podiums_by_mod[mod][k]["total"],
                    "oros": marca_podiums_by_mod[mod][k]["oro"],
                }
                for k in sorted(m_marca_parts.keys(), key=lambda x: -m_marca_parts[x])
            ],
        }

    # Ordenar modalidades por participaciones (descendente) para la gráfica
    modalidades_resumen_ordenado = sorted(
        [
            {
                "modalidad": m,
                "estado": modalidades_data[m]["estado"],
                "validas": modalidades_data[m]["validas_count"],
                "pilotos_unicos": modalidades_data[m]["pilotos_unicos"],
                "participaciones": modalidades_data[m]["participaciones"],
            }
            for m in modalidades_list
        ],
        key=lambda x: (-x["participaciones"], -x["pilotos_unicos"]),
    )

    # === POR MODALIDAD POR SEMESTRE ===
    sem_modalidades = ["Motocross", "Velocidad", "Velotierra"]
    modalidad_semestre = {}
    for mod in sem_modalidades:
        p1 = [p for p in all_participations if p["modalidad"] == mod and p["semestre"] == "Primer semestre"]
        p2 = [p for p in all_participations if p["modalidad"] == mod and p["semestre"] == "Segundo semestre"]
        u1 = set(p["uid"] for p in p1)
        u2 = set(p["uid"] for p in p2)
        rep = u1.intersection(u2)

        c1_map, c2_map = defaultdict(set), defaultdict(set)
        l1_map, l2_map = defaultdict(set), defaultdict(set)
        for p in p1:
            c1_map[p["categoria"]].add(p["uid"])
            if p["liga"]:
                l1_map[p["liga"]].add(p["uid"])
        for p in p2:
            c2_map[p["categoria"]].add(p["uid"])
            if p["liga"]:
                l2_map[p["liga"]].add(p["uid"])

        cats_all = sorted(
            set(c1_map.keys()) | set(c2_map.keys()),
            key=lambda c: (-(len(c1_map[c] | c2_map[c])), c),
        )
        ligas_all = sorted(
            set(l1_map.keys()) | set(l2_map.keys()),
            key=lambda l: (-(len(l1_map[l] | l2_map[l])), l),
        )

        ch1 = next((c for c in championship_summaries if c["modalidad"] == mod and c["semestre"] == "Primer semestre"), None)
        ch2 = next((c for c in championship_summaries if c["modalidad"] == mod and c["semestre"] == "Segundo semestre"), None)

        modalidad_semestre[mod] = {
            "modalidad": mod,
            "estado_1s": ch1["estado"] if ch1 else "N/D",
            "estado_2s": ch2["estado"] if ch2 else "N/D",
            "validas_1s": ch1["validas_count"] if ch1 else 0,
            "validas_2s": ch2["validas_count"] if ch2 else 0,
            "pilotos_1s": len(u1),
            "pilotos_2s": len(u2),
            "participaciones_1s": len(p1),
            "participaciones_2s": len(p2),
            "continuidad_repiten": len(rep),
            "solo_1s": len(u1 - u2),
            "nuevos_2s": len(u2 - u1),
            "tasa_continuidad_pct": round((len(rep) / len(u1) * 100), 1) if u1 else 0.0,
            "categorias": [{"nombre": c, "s1": len(c1_map[c]), "s2": len(c2_map[c])} for c in cats_all],
            "ligas": [{"nombre": l, "s1": len(l1_map[l]), "s2": len(l2_map[l])} for l in ligas_all],
        }

    # === POR SEMESTRE EN GENERAL (Opción A) ===
    sem1_parts = [p for p in all_participations if p["modalidad"] in sem_modalidades and p["semestre"] == "Primer semestre"]
    sem2_parts = [p for p in all_participations if p["modalidad"] in sem_modalidades and p["semestre"] == "Segundo semestre"]
    sem1_uids = set(p["uid"] for p in sem1_parts)
    sem2_uids = set(p["uid"] for p in sem2_parts)
    sem_rep = sem1_uids.intersection(sem2_uids)

    sem_ligas_1 = defaultdict(set)
    sem_ligas_2 = defaultdict(set)
    for p in sem1_parts:
        if p["liga"]:
            sem_ligas_1[p["liga"]].add(p["uid"])
    for p in sem2_parts:
        if p["liga"]:
            sem_ligas_2[p["liga"]].add(p["uid"])

    all_sem_ligas = sorted(
        set(sem_ligas_1.keys()) | set(sem_ligas_2.keys()),
        key=lambda l: -(len(sem_ligas_1[l]) + len(sem_ligas_2[l])),
    )

    semestre_general = {
        "pilotos_1s": len(sem1_uids),
        "pilotos_2s": len(sem2_uids),
        "participaciones_1s": len(sem1_parts),
        "participaciones_2s": len(sem2_parts),
        "validas_1s": sum(modalidad_semestre[m]["validas_1s"] for m in sem_modalidades),
        "validas_2s": sum(modalidad_semestre[m]["validas_2s"] for m in sem_modalidades),
        "repiten_ambos_semestres": len(sem_rep),
        "tasa_continuidad_pct": round((len(sem_rep) / len(sem1_uids) * 100), 1) if sem1_uids else 0.0,
        "por_modalidad": sorted(
            [
                {
                    "modalidad": m,
                    "s1_pilotos": modalidad_semestre[m]["pilotos_1s"],
                    "s2_pilotos": modalidad_semestre[m]["pilotos_2s"],
                    "s1_parts": modalidad_semestre[m]["participaciones_1s"],
                    "s2_parts": modalidad_semestre[m]["participaciones_2s"],
                    "estado_1s": modalidad_semestre[m]["estado_1s"],
                    "estado_2s": modalidad_semestre[m]["estado_2s"],
                }
                for m in sem_modalidades
            ],
            key=lambda x: -(x["s1_pilotos"] + x["s2_pilotos"]),
        ),
        "por_liga": [
            {"liga": l, "s1": len(sem_ligas_1[l]), "s2": len(sem_ligas_2[l])}
            for l in all_sem_ligas[:20]
        ],
        "campeonatos_anuales": [
            {
                "nombre": c["nombre"],
                "modalidad": c["modalidad"],
                "estado": c["estado"],
                "validas_count": c["validas_count"],
                "pilotos_unicos": c["pilotos_unicos"],
                "participaciones": c["participaciones"],
            }
            for c in championship_summaries if c["semestre"] == "Campeonato 2026"
        ],
    }

    # === INTELIGENCIA COMERCIAL ===
    marca_parts_tot = Counter()
    marca_uids_tot = defaultdict(set)
    for p in all_participations:
        if p["moto"]:
            marca_parts_tot[p["moto"]] += 1
            marca_uids_tot[p["moto"]].add(p["uid"])

    total_motos_registradas = sum(marca_parts_tot.values()) or 1
    marcas_ranking = []
    for m_name, cnt in marca_parts_tot.most_common():
        med = medallero_global_marca.get(m_name, {"oro": 0, "plata": 0, "bronce": 0, "total": 0})
        marcas_ranking.append({
            "marca": m_name,
            "participaciones": cnt,
            "cuota_pct": round(cnt / total_motos_registradas * 100, 1),
            "pilotos_unicos": len(marca_uids_tot[m_name]),
            "oro": med["oro"],
            "podios": med["total"],
        })

    club_uids_tot = defaultdict(set)
    club_parts_tot = Counter()
    club_ligas = defaultdict(set)
    for p in all_participations:
        if p["club"]:
            club_uids_tot[p["club"]].add(p["uid"])
            club_parts_tot[p["club"]] += 1
            if p["liga"]:
                club_ligas[p["club"]].add(p["liga"])

    clubes_ranking = []
    for c_name, uids in sorted(club_uids_tot.items(), key=lambda x: (-len(x[1]), -club_parts_tot[x[0]])):
        med = medallero_global_club.get(c_name, {"oro": 0, "plata": 0, "bronce": 0, "total": 0})
        clubes_ranking.append({
            "club": c_name,
            "pilotos_unicos": len(uids),
            "participaciones": club_parts_tot[c_name],
            "ligas": ", ".join(sorted(club_ligas[c_name])) or "N/D",
            "oro": med["oro"],
            "podios": med["total"],
        })

    sede_events = defaultdict(set)
    sede_parts = Counter()
    sede_uids = defaultdict(set)
    sede_visitors = defaultdict(set)
    sede_depto = {}
    sede_event_lic = defaultdict(set)
    for p in all_participations:
        c = p["ciudad"]
        sede_depto[c] = p["depto_sede"]
        sede_events[c].add(f"{p['modalidad']} ({p['valida_label']})")
        sede_parts[c] += 1
        sede_uids[c].add(p["uid"])
        if p["es_evento"]:
            sede_event_lic[c].add(p["uid"])
        if p["depto_sede"] and p["liga"] and key_alnum(p["liga"]) != key_alnum(p["depto_sede"]):
            sede_visitors[c].add(p["uid"])

    sedes_ranking = []
    for ciudad, cnt in sede_parts.most_common():
        u_cnt = len(sede_uids[ciudad])
        sedes_ranking.append({
            "ciudad": ciudad,
            "depto": sede_depto[ciudad],
            "validas_albergadas": len(sede_events[ciudad]),
            "participaciones": cnt,
            "pilotos_unicos": u_cnt,
            "visitantes_pct": round(len(sede_visitors[ciudad]) / u_cnt * 100, 1) if u_cnt else 0.0,
            "licencias_evento": len(sede_event_lic[ciudad]),
        })

    lic_por_mod = []
    for mod in modalidades_list:
        mp = [p for p in all_participations if p["modalidad"] == mod]
        mu = set(p["uid"] for p in mp)
        me = set(p["uid"] for p in mp if p["es_evento"])
        lic_por_mod.append({
            "modalidad": mod,
            "pilotos_unicos": len(mu),
            "evento_unicos": len(me),
            "nacionales_unicos": len(mu - me),
            "evento_pct": round(len(me) / len(mu) * 100, 1) if mu else 0.0,
        })
    lic_por_mod.sort(key=lambda x: -x["pilotos_unicos"])

    finalizados_count = sum(1 for c in championship_summaries if c["finalizado"])
    total_champs = len(championship_summaries)

    return {
        "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "year_status": {
            "estado": "Finalizado" if finalizados_count == total_champs else "En curso",
            "finalizados": finalizados_count,
            "total": total_champs,
        },
        "general": {
            "pilotos_unicos": len(all_uids),
            "participaciones": len(all_participations),
            "validas_disputadas": len(all_validas_set),
            "campeonatos": total_champs,
            "sedes_count": len(all_sedes),
            "ligas_count": len(all_ligas),
            "clubes_count": len(all_clubes),
            "marcas_count": len(all_marcas),
            "licencias_evento": len(all_event_uids),
            "licencias_evento_pct": round(len(all_event_uids) / len(all_uids) * 100, 1) if all_uids else 0.0,
            "semillero_unicos": len(formative_uids),
            "semillero_parts": formative_parts,
            "femenina_unicos": len(femenina_uids),
            "femenina_parts": femenina_parts,
            "multimodal_count": multimodal_count,
            "multicat_count": multicat_count,
            "top_polivalentes": top_polivalentes[:25],
            "ligas_ranking": ligas_ranking,
            "top_ligas_pilotos": top_ligas_pilotos,
            "modalidades_resumen": modalidades_resumen_ordenado,
        },
        "modalidades": modalidades_data,
        "championships": championship_summaries,
        "modalidad_semestre": modalidad_semestre,
        "semestre_general": semestre_general,
        "comercial": {
            "marcas": marcas_ranking,
            "clubes": clubes_ranking[:40],
            "sedes": sedes_ranking,
            "licencias_modalidad": lic_por_mod,
        },
    }


def render_html(data):
    data_json = json.dumps(data, ensure_ascii=False)
    return f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Informe Anual FEDEMOTO 2026 | Estadísticas Deportivas y Comerciales</title>
    <link rel="icon" type="image/png" href="../fedemoto-logo.png">
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Montserrat:wght@500;600;700;800&family=Source+Sans+3:wght@400;500;600;700&family=Barlow+Condensed:wght@500;600;700&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="../fedemoto-theme.css">
    <style>
        .estado-tag {{
            display: inline-flex;
            align-items: center;
            gap: 5px;
            padding: 3px 9px;
            border-radius: 5px;
            font-family: var(--fdm-font-heading);
            font-size: 0.72rem;
            font-weight: 700;
            letter-spacing: 0.03em;
            text-transform: uppercase;
            white-space: nowrap;
            border: 1px solid #cbd5e1;
            background: #f8fafc;
            color: #334155;
        }}
        .estado-tag svg {{
            width: 13px;
            height: 13px;
            flex-shrink: 0;
        }}
        .estado-tag.finalizado svg {{
            color: #15803d;
        }}
        .estado-tag.en-curso svg {{
            color: #b45309;
        }}
        .season-status-line {{
            margin-top: 12px;
            font-size: 0.92rem;
            color: rgba(255, 255, 255, 0.88);
            font-weight: 500;
        }}
        .top-actions-bar {{
            padding: 16px 32px;
            background: var(--fdm-surface-alt);
            border-bottom: 1px solid var(--fdm-border);
        }}
        .main-tabs {{
            display: grid;
            grid-template-columns: repeat(6, 1fr);
            gap: 10px;
            width: 100%;
        }}
        .main-tab-btn {{
            padding: 11px 10px;
            border-radius: var(--fdm-radius-sm);
            border: 1px solid var(--fdm-border-dark);
            background: #ffffff;
            color: var(--fdm-primary);
            font-family: var(--fdm-font-heading);
            font-weight: 700;
            font-size: 0.82rem;
            text-align: center;
            cursor: pointer;
            transition: var(--fdm-transition);
            white-space: nowrap;
        }}
        .main-tab-btn:hover {{
            background: #edf2fa;
            border-color: var(--fdm-primary);
        }}
        .main-tab-btn.active {{
            background: var(--fdm-primary);
            color: #ffffff;
            border-color: var(--fdm-primary);
            box-shadow: 0 3px 10px rgba(0, 56, 147, 0.22);
        }}
        .btn-export-annual {{
            display: none !important;
        }}
        .tab-panel {{
            display: none;
            padding: 32px 36px;
        }}
        .tab-panel.active {{
            display: block;
            animation: fdmFadeIn 0.25s ease;
        }}
        .kpi-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(185px, 1fr));
            gap: 16px;
            margin-bottom: 28px;
        }}
        .kpi-card {{
            background: #ffffff;
            border: 1px solid var(--fdm-border);
            border-top: 3px solid var(--fdm-primary);
            border-radius: var(--fdm-radius-md);
            padding: 18px 16px;
            box-shadow: var(--fdm-shadow-soft);
        }}
        .kpi-card.accent {{
            border-top-color: var(--fdm-accent);
        }}
        .kpi-val {{
            font-family: var(--fdm-font-racing);
            font-size: 2.15rem;
            font-weight: 700;
            color: var(--fdm-primary);
            line-height: 1.05;
        }}
        .kpi-lbl {{
            font-family: var(--fdm-font-heading);
            font-size: 0.76rem;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            color: var(--fdm-text-muted);
            margin-top: 6px;
        }}
        .kpi-sub {{
            font-size: 0.84rem;
            color: var(--fdm-text-muted);
            margin-top: 5px;
            line-height: 1.35;
        }}
        .sub-section {{
            margin-top: 32px;
        }}
        .section-title-bar {{
            display: flex;
            flex-wrap: wrap;
            align-items: center;
            justify-content: space-between;
            gap: 12px;
            margin-bottom: 16px;
            padding-bottom: 8px;
            border-bottom: 2px solid var(--fdm-accent);
        }}
        .section-title-bar h2 {{
            font-size: 1.3rem;
            color: var(--fdm-primary);
            margin: 0;
        }}
        .section-title-actions {{
            display: flex;
            align-items: center;
            gap: 10px;
        }}
        .two-col {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(420px, 1fr));
            gap: 24px;
        }}
        .card-box {{
            background: var(--fdm-surface-alt);
            border: 1px solid var(--fdm-border);
            border-radius: var(--fdm-radius-md);
            padding: 20px;
            position: relative;
        }}
        .card-box-header {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 10px;
            margin-bottom: 14px;
        }}
        .card-box-header h3 {{
            font-size: 1.06rem;
            color: var(--fdm-primary);
            margin: 0;
        }}
        .help-btn {{
            display: inline-flex;
            align-items: center;
            justify-content: center;
            width: 24px;
            height: 24px;
            border-radius: 999px;
            border: 1px solid #cbd5e1;
            background: #ffffff;
            color: var(--fdm-primary);
            font-family: var(--fdm-font-heading);
            font-size: 0.78rem;
            font-weight: 700;
            cursor: pointer;
            flex-shrink: 0;
            transition: var(--fdm-transition);
        }}
        .help-btn:hover {{
            background: var(--fdm-primary);
            color: #ffffff;
            border-color: var(--fdm-primary);
        }}
        .data-table-wrap {{
            overflow-x: auto;
            border: 1px solid var(--fdm-border);
            border-radius: var(--fdm-radius-sm);
            background: #ffffff;
        }}
        .data-table {{
            width: 100%;
            border-collapse: collapse;
            font-size: 0.9rem;
        }}
        .data-table th, .data-table td {{
            padding: 10px 12px;
            border-bottom: 1px solid var(--fdm-border);
            text-align: left;
        }}
        .data-table th {{
            background: var(--fdm-primary);
            color: #ffffff;
            font-family: var(--fdm-font-heading);
            font-size: 0.78rem;
            text-transform: uppercase;
            letter-spacing: 0.04em;
            white-space: nowrap;
        }}
        .data-table th.num, .data-table td.num {{
            text-align: right;
            font-variant-numeric: tabular-nums;
        }}
        .data-table tr:hover {{
            background: #f5f8fd;
        }}
        .bar-row {{
            display: grid;
            grid-template-columns: 185px 1fr 78px;
            align-items: center;
            gap: 12px;
            margin-bottom: 10px;
            font-size: 0.9rem;
        }}
        .bar-label {{
            font-weight: 600;
            color: var(--fdm-text);
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
        }}
        .bar-track {{
            height: 22px;
            background: #e2e8f0;
            border-radius: 6px;
            overflow: hidden;
        }}
        .bar-fill {{
            height: 100%;
            background: linear-gradient(90deg, var(--fdm-primary) 0%, #2563eb 100%);
            border-radius: 6px;
        }}
        .bar-fill.gold {{
            background: linear-gradient(90deg, #d97706 0%, var(--fdm-accent) 100%);
        }}
        .bar-val {{
            text-align: right;
            font-family: var(--fdm-font-racing);
            font-weight: 700;
            font-size: 1.05rem;
            color: var(--fdm-primary);
        }}
        .delta-pos {{ color: #15803d; font-weight: 700; }}
        .delta-neg {{ color: #b91c1c; font-weight: 700; }}
        .delta-neu {{ color: var(--fdm-text-muted); font-weight: 600; }}
        .champ-status-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(265px, 1fr));
            gap: 14px;
        }}
        .champ-status-card {{
            background: #ffffff;
            border: 1px solid var(--fdm-border);
            border-radius: var(--fdm-radius-md);
            padding: 16px;
            display: flex;
            flex-direction: column;
            gap: 8px;
            box-shadow: var(--fdm-shadow-soft);
        }}
        .champ-status-top {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 10px;
        }}
        .champ-status-title {{
            font-family: var(--fdm-font-heading);
            font-weight: 700;
            color: var(--fdm-text);
            font-size: 0.94rem;
        }}
        .champ-status-meta {{
            font-size: 0.85rem;
            color: var(--fdm-text-muted);
        }}
        .btn-link-small {{
            display: inline-block;
            margin-top: 2px;
            font-size: 0.84rem;
            font-weight: 700;
            color: var(--fdm-primary);
            text-decoration: none;
        }}
        .btn-link-small:hover {{ text-decoration: underline; }}
        .controls-row {{
            display: flex;
            flex-wrap: wrap;
            gap: 12px;
            align-items: center;
            margin-bottom: 20px;
        }}
        .notice-box {{
            padding: 14px 18px;
            background: #eff6ff;
            border-left: 4px solid var(--fdm-primary);
            border-radius: 6px;
            font-size: 0.92rem;
            color: #1e3a8a;
            margin-bottom: 20px;
        }}
        .help-modal-overlay {{
            display: none;
            position: fixed;
            inset: 0;
            background: rgba(15, 23, 42, 0.55);
            z-index: 10050;
            align-items: center;
            justify-content: center;
            padding: 16px;
        }}
        .help-modal-overlay.open {{
            display: flex;
        }}
        .help-modal-box {{
            background: #ffffff;
            border-radius: 12px;
            max-width: 520px;
            width: 100%;
            padding: 26px 28px;
            box-shadow: 0 24px 60px rgba(0, 0, 0, 0.28);
            border-top: 4px solid var(--fdm-primary);
        }}
        .help-modal-box h3 {{
            font-size: 1.2rem;
            color: var(--fdm-primary);
            margin-bottom: 14px;
        }}
        .help-modal-block {{
            margin-bottom: 14px;
            font-size: 0.95rem;
            line-height: 1.55;
            color: var(--fdm-text);
        }}
        .help-modal-block strong {{
            display: block;
            font-family: var(--fdm-font-heading);
            font-size: 0.8rem;
            text-transform: uppercase;
            letter-spacing: 0.04em;
            color: var(--fdm-primary);
            margin-bottom: 4px;
        }}
        .help-modal-close {{
            margin-top: 8px;
            padding: 9px 18px;
            background: var(--fdm-primary);
            color: #ffffff;
            border: none;
            border-radius: 8px;
            font-family: var(--fdm-font-heading);
            font-weight: 700;
            font-size: 0.85rem;
            cursor: pointer;
        }}
        .help-modal-close:hover {{
            background: var(--fdm-primary-hover);
        }}
        @media (max-width: 1100px) {{
            .main-tabs {{ grid-template-columns: repeat(3, 1fr); }}
        }}
        @media (max-width: 768px) {{
            .top-actions-bar, .tab-panel {{ padding: 18px 16px; }}
            .main-tabs {{ grid-template-columns: repeat(2, 1fr); }}
            .two-col {{ grid-template-columns: 1fr; }}
            .bar-row {{ grid-template-columns: 120px 1fr 60px; }}
        }}
        @media print {{
            .top-actions-bar, .controls-row, #menu-container, .help-btn {{ display: none !important; }}
            .tab-panel {{ display: block !important; page-break-after: always; }}
        }}
    </style>
</head>
<body>
    <div id="menu-container"></div>

    <div class="container">
        <header>
            <h1>
                <img src="../fedemoto-logo.png" alt="FEDEMOTO Logo" style="height: 54px; vertical-align: middle; margin-right: 12px;">
                Informe Anual FEDEMOTO 2026
            </h1>
            <p>Análisis Estadístico Deportivo y Comercial · General, Modalidades, Campeonatos y Semestres</p>
            <div class="season-status-line" id="seasonStatusLine"></div>
        </header>

        <div class="top-actions-bar">
            <div class="main-tabs" id="mainTabs">
                <button class="main-tab-btn active" data-tab="general">General Anual</button>
                <button class="main-tab-btn" data-tab="modalidad">Por Modalidad</button>
                <button class="main-tab-btn" data-tab="campeonato">Por Campeonato</button>
                <button class="main-tab-btn" data-tab="modalidad-semestre">Modalidad por Semestre</button>
                <button class="main-tab-btn" data-tab="semestre-general">Semestre en General</button>
                <button class="main-tab-btn" data-tab="comercial">Inteligencia Comercial</button>
            </div>
            <button class="btn-export-annual" id="btnExportAnnual" aria-hidden="true">Exportar a PDF</button>
        </div>

        <section class="tab-panel active" id="tab-general"></section>
        <section class="tab-panel" id="tab-modalidad"></section>
        <section class="tab-panel" id="tab-campeonato"></section>
        <section class="tab-panel" id="tab-modalidad-semestre"></section>
        <section class="tab-panel" id="tab-semestre-general"></section>
        <section class="tab-panel" id="tab-comercial"></section>

        <footer>
            <p><span class="developer">Developed by Mauricio Sánchez Aguilar - Fedemoto</span></p>
            <p>Actualizado automáticamente desde los resultados oficiales 2026 · Generado el <span id="genDate"></span></p>
        </footer>
    </div>

    <!-- Modal de explicación para gráficos y tablas -->
    <div class="help-modal-overlay" id="modalHelp">
        <div class="help-modal-box">
            <h3 id="modalHelpTitle">Información del indicador</h3>
            <div class="help-modal-block">
                <strong>Qué significa</strong>
                <p id="modalHelpMeaning"></p>
            </div>
            <div class="help-modal-block">
                <strong>Importancia deportiva y comercial</strong>
                <p id="modalHelpImportance"></p>
            </div>
            <button type="button" class="help-modal-close" id="modalHelpClose">Entendido</button>
        </div>
    </div>

    <script src="../load-menu.js"></script>
    <script>
        const DATA = {data_json};

        const HELP_DOCS = {{
            estado_campeonatos: {{
                title: "Estado de los Campeonatos 2026",
                meaning: "Muestra el estado oficial de cada uno de los 8 campeonatos del calendario 2026. Un campeonato figura como Finalizado únicamente cuando ya se integró su válida final y se aplicó el bono de asistencia de 8 puntos; de lo contrario aparece En curso.",
                importance: "Permite validar qué títulos y medallas ya son definitivos frente a cuáles siguen en disputa antes de emitir comunicaciones oficiales o premiaciones."
            }},
            part_modalidad: {{
                title: "Participación por Modalidad",
                meaning: "Suma total de participaciones en grilla registradas en todas las válidas de cada modalidad, ordenadas de mayor a menor volumen.",
                importance: "Identifica las disciplinas con mayor demanda operativa y comercial, orientando la asignación de presupuesto, personal técnico y visibilidad para patrocinadores."
            }},
            top_ligas: {{
                title: "Top 12 Ligas por Pilotos Únicos",
                meaning: "Cantidad de deportistas distintos (deduplicados por nombre) adscritos a cada liga departamental durante todo 2026.",
                importance: "Mide el alcance territorial real de la federación y el tamaño efectivo de la base de pilotos afiliados por departamento, sin inflarlo por correr varias categorías."
            }},
            medallero_ligas: {{
                title: "Medallero y Ranking Nacional de Ligas",
                meaning: "Clasifica a las ligas departamentales siguiendo el orden olímpico oficial: primero cantidad de medallas de oro (1° puesto en campeonato), luego plata (2°), bronce (3°) y, como desempate, total de participaciones.",
                importance: "Evalúa el rendimiento deportivo de alto nivel de cada liga frente al volumen de su delegación, sirviendo como indicador de gestión técnica regional."
            }},
            polivalencia: {{
                title: "Índice de Polivalencia: Multimodales y Multicategoría",
                meaning: "Identifica a los pilotos que compitieron en 2 o más modalidades distintas en el año (ej. Motocross y Velotierra) o en múltiples categorías.",
                importance: "Revela los perfiles de pilotos más activos del país (clientes de alto valor para marcas de llantas, lubricantes y concesionarios) y la sinergia entre disciplinas."
            }},
            mod_categorias: {{
                title: "Categorías por Pilotos Únicos y Grilla Promedio",
                meaning: "Lista las categorías oficiales de la modalidad ordenadas de mayor a menor por cantidad de pilotos únicos, mostrando además su grilla promedio por válida y porcentaje de llegada a meta (clasificados vs NT/NE/EX).",
                importance: "Ayuda a las comisiones técnicas a detectar categorías consolidadas, categorías con baja convocatoria y posibles problemas mecánicos o de exigencia de pista según la tasa de finalización."
            }},
            mod_ligas: {{
                title: "Ligas en la Modalidad",
                meaning: "Número de pilotos únicos que aportó cada liga departamental dentro de la modalidad seleccionada.",
                importance: "Muestra en qué departamentos tiene mayor arraigo cada disciplina para focalizar fechas del calendario y escuelas regionales."
            }},
            mod_marcas: {{
                title: "Marcas y Podios en la Modalidad",
                meaning: "Distribución de máquinas en grilla por fabricante dentro de la modalidad junto con los títulos (oros) y podios totales obtenidos.",
                importance: "Mide tanto la preferencia de compra del piloto en esa disciplina como la competitividad real de cada marca."
            }},
            champ_asistencia: {{
                title: "Evolución de Asistencia por Válida",
                meaning: "Compara fecha a fecha el número de participaciones, pilotos únicos y el porcentaje de pilotos visitantes (de ligas externas al departamento anfitrión).",
                importance: "Permite evaluar qué sedes convocan más público viajero y cómo evoluciona la asistencia desde la apertura hasta el cierre del campeonato."
            }},
            champ_retencion: {{
                title: "Retención del Campeonato",
                meaning: "Muestra cuántos pilotos disputaron 1, 2, 3 o todas las válidas del campeonato.",
                importance: "Mide la fidelidad al torneo completo y el efecto de incentivos reglamentarios como el bono de asistencia final de 8 puntos."
            }},
            champ_honor: {{
                title: "Cuadro de Honor y Paridad Competitiva",
                meaning: "Presenta el podio general acumulado por categoría, su puntaje total y la brecha de puntos entre el 1° y el 3° puesto.",
                importance: "Resume los campeones o líderes oficiales y permite medir qué categorías tuvieron definiciones más cerradas y emocionantes."
            }},
            champ_med_liga: {{
                title: "Medallero por Liga del Campeonato",
                meaning: "Conteo de podios generales (1°, 2° y 3° puesto) obtenidos por cada liga departamental en el campeonato seleccionado.",
                importance: "Resume el dominio deportivo regional específico de ese torneo."
            }},
            champ_med_club: {{
                title: "Medallero por Club del Campeonato",
                meaning: "Conteo de podios generales obtenidos por los clubes deportivos dentro del campeonato.",
                importance: "Visibiliza y reconoce a los clubes con mejor formación y desempeño competitivo."
            }},
            mod_sem_cats: {{
                title: "Comparación Semestral por Categoría (1S vs 2S)",
                meaning: "Contrasta los pilotos únicos de cada categoría entre el primer y segundo semestre junto con su variación absoluta y porcentual.",
                importance: "Detecta qué categorías crecieron, se mantuvieron o cayeron entre semestres para ajustar reglamentos o promoción."
            }},
            mod_sem_ligas: {{
                title: "Comparación Semestral por Liga (1S vs 2S)",
                meaning: "Compara la presencia de pilotos únicos por liga entre el 1er y el 2do semestre dentro de la modalidad.",
                importance: "Evidencia cómo influye la ubicación geográfica de las pistas de cada semestre en la asistencia de las delegaciones."
            }},
            sem_gen_mod: {{
                title: "Estacionalidad por Modalidad Semestral",
                meaning: "Consolida únicamente las 3 modalidades divididas en semestres (Motocross, Velocidad y Velotierra), comparando pilotos y participaciones entre 1S y 2S.",
                importance: "Permite planificar recursos federativos y paquetes comerciales diferenciados según la dinámica de cada mitad del año."
            }},
            sem_gen_ligas: {{
                title: "Top Ligas por Semestre (1S vs 2S)",
                meaning: "Comparativo de pilotos únicos movilizados por las 20 ligas principales en el primer semestre frente al segundo semestre.",
                importance: "Identifica caídas o picos regionales entre semestres para apoyar a las ligas con menor actividad en la segunda mitad del año."
            }},
            com_marcas: {{
                title: "Cuota de Mercado y Efectividad por Marca (OEM)",
                meaning: "Calcula el porcentaje de participación de cada marca de motocicleta sobre el total de entradas en grilla, junto con los pilotos únicos, oros y podios totales.",
                importance: "Es el indicador comercial principal para negociar patrocinios con marcas e importadores, demostrando presencia de marca y retorno deportivo."
            }},
            com_licencias: {{
                title: "Conversión de Licencias: Nacionales vs. Evento (-E)",
                meaning: "Compara cuántos pilotos compiten con licencia nacional anual frente a pilotos con licencia de evento (-E) en cada modalidad.",
                importance: "Cuantifica la oportunidad comercial directa de convertir corredores ocasionales (-E) en afiliados anuales para la temporada 2027."
            }},
            com_sedes: {{
                title: "Poder de Convocatoria por Sede (Turismo Deportivo)",
                meaning: "Mide el total de eventos, participaciones, pilotos únicos y porcentaje de visitantes externos recibidos por cada ciudad anfitriona.",
                importance: "Argumento clave ante alcaldías, gobernaciones e institutos de deporte para demostrar derrama turística, ocupación hotelera y retorno de inversión."
            }},
            com_clubes: {{
                title: "Ranking Nacional de Clubes Deportivos",
                meaning: "Clasifica los clubes deportivos según su número de pilotos únicos, participaciones totales y medallas conseguidas.",
                importance: "Identifica los clubes más influyentes del país para convenios comerciales, capacitaciones y programas de beneficios."
            }}
        }};

        function openHelp(key) {{
            const doc = HELP_DOCS[key];
            if (!doc) return;
            document.getElementById("modalHelpTitle").textContent = doc.title;
            document.getElementById("modalHelpMeaning").textContent = doc.meaning;
            document.getElementById("modalHelpImportance").textContent = doc.importance;
            document.getElementById("modalHelp").classList.add("open");
        }}

        function helpBtn(key) {{
            return `<button type="button" class="help-btn" data-help="${{key}}" title="¿Qué significa este gráfico?" aria-label="Información del gráfico">?</button>`;
        }}

        document.addEventListener("click", e => {{
            const hb = e.target.closest(".help-btn");
            if (hb) {{
                openHelp(hb.dataset.help);
                return;
            }}
            if (e.target.id === "modalHelp" || e.target.id === "modalHelpClose") {{
                document.getElementById("modalHelp").classList.remove("open");
            }}
        }});

        function esc(s) {{
            return String(s == null ? "" : s)
                .replace(/&/g, "&amp;")
                .replace(/</g, "&lt;")
                .replace(/>/g, "&gt;")
                .replace(/"/g, "&quot;");
        }}

        const SVG_CHECK = `<svg viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><polyline points="4 10.5 8 14.5 16 6"></polyline></svg>`;
        const SVG_CLOCK = `<svg viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="10" cy="10" r="7.5"></circle><polyline points="10 6 10 10 13 11.5"></polyline></svg>`;

        function estadoBadge(estado) {{
            const isFin = estado === "Finalizado";
            const cls = isFin ? "finalizado" : "en-curso";
            const icon = isFin ? SVG_CHECK : SVG_CLOCK;
            return `<span class="estado-tag ${{cls}}">${{icon}}<span>${{esc(estado)}}</span></span>`;
        }}

        function deltaHtml(s1, s2) {{
            const diff = s2 - s1;
            const pct = s1 > 0 ? ((diff / s1) * 100).toFixed(1) : (s2 > 0 ? "100.0" : "0.0");
            const cls = diff > 0 ? "delta-pos" : (diff < 0 ? "delta-neg" : "delta-neu");
            const sign = diff > 0 ? "+" : "";
            return `<span class="${{cls}}">${{sign}}${{diff}} (${{sign}}${{pct}}%)</span>`;
        }}

        function renderBarList(items, labelKey, valKey, maxVal, gold) {{
            const mx = maxVal || Math.max(1, ...items.map(i => i[valKey] || 0));
            return items.map(it => {{
                const v = it[valKey] || 0;
                const w = Math.max(2, Math.round((v / mx) * 100));
                return `
                    <div class="bar-row">
                        <div class="bar-label" title="${{esc(it[labelKey])}}">${{esc(it[labelKey])}}</div>
                        <div class="bar-track"><div class="bar-fill ${{gold ? 'gold' : ''}}" style="width:${{w}}%"></div></div>
                        <div class="bar-val">${{v}}</div>
                    </div>`;
            }}).join("");
        }}

        document.getElementById("genDate").textContent = DATA.generated_at;
        const ys = DATA.year_status;
        document.getElementById("seasonStatusLine").textContent =
            `Temporada 2026: ${{ys.estado}} (${{ys.finalizados}} de ${{ys.total}} campeonatos finalizados) · ${{DATA.general.pilotos_unicos}} pilotos únicos · ${{DATA.general.participaciones}} participaciones`;

        document.querySelectorAll(".main-tab-btn").forEach(btn => {{
            btn.addEventListener("click", () => {{
                document.querySelectorAll(".main-tab-btn").forEach(b => b.classList.remove("active"));
                document.querySelectorAll(".tab-panel").forEach(p => p.classList.remove("active"));
                btn.classList.add("active");
                document.getElementById("tab-" + btn.dataset.tab).classList.add("active");
            }});
        }});
        document.getElementById("btnExportAnnual").addEventListener("click", () => window.print());

        // ================= TAB 1: GENERAL ANUAL =================
        function renderGeneral() {{
            const g = DATA.general;
            const el = document.getElementById("tab-general");

            const champCards = DATA.championships.map(c => `
                <div class="champ-status-card">
                    <div class="champ-status-top">
                        <span class="champ-status-title">${{esc(c.nombre)}}</span>
                        ${{estadoBadge(c.estado)}}
                    </div>
                    <div class="champ-status-meta">
                        <strong>${{c.validas_count}}</strong> válidas · <strong>${{c.pilotos_unicos}}</strong> pilotos únicos · <strong>${{c.participaciones}}</strong> participaciones
                    </div>
                    <div class="champ-status-meta">
                        ${{c.finalizado ? "Bono de asistencia final (8 pts) aplicado" : "Sin válida final / bono de 8 pts aún no aplicado"}}
                    </div>
                    <a class="btn-link-small" href="../Resultados generales/${{esc(c.url_general)}}">Ver tabla acumulada →</a>
                </div>
            `).join("");

            el.innerHTML = `
                <div class="kpi-grid">
                    <div class="kpi-card"><div class="kpi-val">${{g.pilotos_unicos}}</div><div class="kpi-lbl">Pilotos Únicos 2026</div><div class="kpi-sub">${{g.licencias_evento}} con licencia evento (-E) · ${{(100 - g.licencias_evento_pct).toFixed(1)}}% licencias anuales</div></div>
                    <div class="kpi-card"><div class="kpi-val">${{g.participaciones}}</div><div class="kpi-lbl">Participaciones en Grilla</div><div class="kpi-sub">${{g.validas_disputadas}} válidas en ${{g.sedes_count}} ciudades sede</div></div>
                    <div class="kpi-card accent"><div class="kpi-val">${{g.ligas_count}}</div><div class="kpi-lbl">Ligas Activas</div><div class="kpi-sub">${{g.clubes_count}} clubes deportivos registrados</div></div>
                    <div class="kpi-card accent"><div class="kpi-val">${{g.marcas_count}}</div><div class="kpi-lbl">Marcas en Grilla</div><div class="kpi-sub">${{g.campeonatos}} campeonatos en 2026</div></div>
                    <div class="kpi-card"><div class="kpi-val">${{g.semillero_unicos}}</div><div class="kpi-lbl">Pilotos Categorías Formativas</div><div class="kpi-sub">Niños y jóvenes (50cc-85cc, Infantil, Juvenil, Escuela) · ${{g.semillero_parts}} salidas</div></div>
                    <div class="kpi-card"><div class="kpi-val">${{g.femenina_unicos}}</div><div class="kpi-lbl">Pilotos Categoría Femenina</div><div class="kpi-sub">${{g.femenina_parts}} participaciones femeninas</div></div>
                    <div class="kpi-card"><div class="kpi-val">${{g.multimodal_count}}</div><div class="kpi-lbl">Pilotos Multimodales</div><div class="kpi-sub">Corrieron 2+ modalidades (${{g.multicat_count}} multicategoría)</div></div>
                </div>

                <div class="sub-section">
                    <div class="section-title-bar">
                        <h2>Estado de los Campeonatos 2026</h2>
                        <div class="section-title-actions">${{helpBtn("estado_campeonatos")}}</div>
                    </div>
                    <div class="champ-status-grid">${{champCards}}</div>
                </div>

                <div class="sub-section two-col">
                    <div class="card-box">
                        <div class="card-box-header">
                            <h3>Participación por Modalidad (Ordenado de mayor a menor)</h3>
                            ${{helpBtn("part_modalidad")}}
                        </div>
                        ${{renderBarList(g.modalidades_resumen, "modalidad", "participaciones", null, false)}}
                    </div>
                    <div class="card-box">
                        <div class="card-box-header">
                            <h3>Top 12 Ligas por Pilotos Únicos</h3>
                            ${{helpBtn("top_ligas")}}
                        </div>
                        ${{renderBarList(g.top_ligas_pilotos, "liga", "pilotos_unicos", null, true)}}
                    </div>
                </div>

                <div class="sub-section">
                    <div class="section-title-bar">
                        <h2>Medallero y Ranking Nacional de Ligas</h2>
                        <div class="section-title-actions">
                            <input type="text" class="search-box" id="searchLigaGen" placeholder="Filtrar liga..." style="max-width:240px; padding:8px 12px;">
                            ${{helpBtn("medallero_ligas")}}
                        </div>
                    </div>
                    <div class="data-table-wrap">
                        <table class="data-table" id="tablaLigasGen">
                            <thead>
                                <tr>
                                    <th>#</th><th>Liga</th><th class="num">Oro (1°)</th><th class="num">Plata (2°)</th><th class="num">Bronce (3°)</th>
                                    <th class="num">Total Podios</th><th class="num">Participaciones</th><th class="num">Pilotos Únicos</th>
                                </tr>
                            </thead>
                            <tbody></tbody>
                        </table>
                    </div>
                </div>

                <div class="sub-section">
                    <div class="section-title-bar">
                        <h2>Índice de Polivalencia: Pilotos Multimodales y Multicategoría</h2>
                        <div class="section-title-actions">${{helpBtn("polivalencia")}}</div>
                    </div>
                    <div class="data-table-wrap">
                        <table class="data-table">
                            <thead>
                                <tr><th>#</th><th>Piloto</th><th>Liga</th><th>Modalidades</th><th class="num">Categorías</th><th class="num">Participaciones</th></tr>
                            </thead>
                            <tbody>
                                ${{g.top_polivalentes.map((p, i) => `
                                    <tr>
                                        <td>${{i + 1}}</td><td><strong>${{esc(p.nombre)}}</strong></td><td>${{esc(p.liga)}}</td>
                                        <td>${{p.modalidades.map(m => esc(m)).join(", ")}}</td>
                                        <td class="num">${{p.categorias_count}}</td><td class="num">${{p.participaciones}}</td>
                                    </tr>
                                `).join("")}}
                            </tbody>
                        </table>
                    </div>
                </div>
            `;

            function fillLigasGen(q) {{
                const rows = g.ligas_ranking.filter(l => !q || l.liga.toLowerCase().includes(q));
                document.querySelector("#tablaLigasGen tbody").innerHTML = rows.map((l, i) => `
                    <tr>
                        <td>${{i + 1}}</td><td><strong>${{esc(l.liga)}}</strong></td>
                        <td class="num"><strong>${{l.oro}}</strong></td><td class="num">${{l.plata}}</td><td class="num">${{l.bronce}}</td>
                        <td class="num"><strong>${{l.podios}}</strong></td>
                        <td class="num">${{l.participaciones}}</td><td class="num">${{l.pilotos_unicos}}</td>
                    </tr>
                `).join("");
            }}
            fillLigasGen("");
            document.getElementById("searchLigaGen").addEventListener("input", e => fillLigasGen(e.target.value.trim().toLowerCase()));
        }}

        // ================= TAB 2: POR MODALIDAD =================
        function renderModalidad() {{
            const el = document.getElementById("tab-modalidad");
            const mods = Object.keys(DATA.modalidades);
            el.innerHTML = `
                <div class="controls-row">
                    <label for="selMod" style="font-weight:700;">Modalidad:</label>
                    <select class="filter-select" id="selMod">
                        ${{mods.map(m => `<option value="${{esc(m)}}">${{esc(m)}}</option>`).join("")}}
                    </select>
                    <span id="modEstadoBadge"></span>
                </div>
                <div id="modDetailBody"></div>
            `;

            function updateMod(modName) {{
                const m = DATA.modalidades[modName];
                document.getElementById("modEstadoBadge").innerHTML = estadoBadge(m.estado);
                document.getElementById("modDetailBody").innerHTML = `
                    <div class="kpi-grid">
                        <div class="kpi-card"><div class="kpi-val">${{m.pilotos_unicos}}</div><div class="kpi-lbl">Pilotos Únicos 2026</div></div>
                        <div class="kpi-card"><div class="kpi-val">${{m.participaciones}}</div><div class="kpi-lbl">Participaciones</div><div class="kpi-sub">${{m.promedio_validas_piloto}} válidas/piloto</div></div>
                        <div class="kpi-card accent"><div class="kpi-val">${{m.validas_count}}</div><div class="kpi-lbl">Válidas Disputadas</div></div>
                        <div class="kpi-card accent"><div class="kpi-val">${{m.efectividad_general_pct}}%</div><div class="kpi-lbl">Tasa de Finalización</div><div class="kpi-sub">Clasificados vs NT/NE/EX</div></div>
                    </div>
                    <div class="two-col">
                        <div class="card-box">
                            <div class="card-box-header">
                                <h3>Categorías (Ordenadas por Pilotos Únicos)</h3>
                                ${{helpBtn("mod_categorias")}}
                            </div>
                            <div class="data-table-wrap">
                                <table class="data-table">
                                    <thead><tr><th>Categoría</th><th class="num">Únicos</th><th class="num">Part.</th><th class="num">Grilla Prom.</th><th class="num">% Llegada</th></tr></thead>
                                    <tbody>
                                        ${{m.categorias.map(c => `
                                            <tr>
                                                <td><strong>${{esc(c.categoria)}}</strong></td>
                                                <td class="num"><strong>${{c.pilotos_unicos}}</strong></td><td class="num">${{c.participaciones}}</td>
                                                <td class="num">${{c.grilla_promedio}}</td><td class="num">${{c.efectividad_llegada_pct}}%</td>
                                            </tr>
                                        `).join("")}}
                                    </tbody>
                                </table>
                            </div>
                        </div>
                        <div class="card-box">
                            <div class="card-box-header">
                                <h3>Ligas en ${{esc(modName)}}</h3>
                                ${{helpBtn("mod_ligas")}}
                            </div>
                            ${{renderBarList(m.ligas.slice(0, 14), "nombre", "pilotos", null, false)}}
                            <div class="card-box-header" style="margin-top:26px;">
                                <h3>Marcas y Podios en ${{esc(modName)}}</h3>
                                ${{helpBtn("mod_marcas")}}
                            </div>
                            <div class="data-table-wrap">
                                <table class="data-table">
                                    <thead><tr><th>Marca</th><th class="num">Part.</th><th class="num">Únicos</th><th class="num">Oro (1°)</th><th class="num">Podios</th></tr></thead>
                                    <tbody>
                                        ${{m.marcas.slice(0, 10).map(mk => `
                                            <tr>
                                                <td><strong>${{esc(mk.marca)}}</strong></td>
                                                <td class="num">${{mk.participaciones}}</td><td class="num">${{mk.pilotos_unicos}}</td>
                                                <td class="num">${{mk.oros}}</td><td class="num">${{mk.podios}}</td>
                                            </tr>
                                        `).join("")}}
                                    </tbody>
                                </table>
                            </div>
                        </div>
                    </div>
                `;
            }}

            const sel = document.getElementById("selMod");
            sel.addEventListener("change", () => updateMod(sel.value));
            updateMod(mods[0]);
        }}

        // ================= TAB 3: POR CAMPEONATO =================
        function renderCampeonato() {{
            const el = document.getElementById("tab-campeonato");
            el.innerHTML = `
                <div class="controls-row">
                    <label for="selChamp" style="font-weight:700;">Campeonato:</label>
                    <select class="filter-select" id="selChamp" style="min-width:280px;">
                        ${{DATA.championships.map(c => `<option value="${{esc(c.id)}}">${{esc(c.nombre)}} (${{esc(c.estado)}})</option>`).join("")}}
                    </select>
                    <span id="champEstadoBadge"></span>
                    <a id="champLinkGeneral" class="btn-link-small" href="#" style="margin-left:auto;">Abrir tabla acumulada oficial →</a>
                </div>
                <div id="champDetailBody"></div>
            `;

            function updateChamp(cid) {{
                const c = DATA.championships.find(x => x.id === cid);
                document.getElementById("champEstadoBadge").innerHTML = estadoBadge(c.estado);
                document.getElementById("champLinkGeneral").href = "../Resultados generales/" + c.url_general;

                document.getElementById("champDetailBody").innerHTML = `
                    <div class="kpi-grid">
                        <div class="kpi-card"><div class="kpi-val">${{c.pilotos_unicos}}</div><div class="kpi-lbl">Pilotos Únicos</div></div>
                        <div class="kpi-card"><div class="kpi-val">${{c.participaciones}}</div><div class="kpi-lbl">Participaciones</div></div>
                        <div class="kpi-card accent"><div class="kpi-val">${{c.retencion_completa_pct}}%</div><div class="kpi-lbl">Asistencia Perfecta</div><div class="kpi-sub">${{c.validas_count}} de ${{c.validas_count}} válidas</div></div>
                        <div class="kpi-card accent"><div class="kpi-val">${{c.parity_avg_gap_1_3 != null ? c.parity_avg_gap_1_3 + " pts" : "N/D"}}</div><div class="kpi-lbl">Brecha Prom. 1° vs 3°</div><div class="kpi-sub">Indicador de paridad</div></div>
                    </div>

                    <div class="two-col">
                        <div class="card-box">
                            <div class="card-box-header">
                                <h3>Evolución de Asistencia por Válida</h3>
                                ${{helpBtn("champ_asistencia")}}
                            </div>
                            <div class="data-table-wrap">
                                <table class="data-table">
                                    <thead><tr><th>Válida</th><th>Sede</th><th class="num">Part.</th><th class="num">Únicos</th><th class="num">% Visitantes</th></tr></thead>
                                    <tbody>
                                        ${{c.valida_curves.map(v => `
                                            <tr>
                                                <td><strong>${{esc(v.label)}}</strong></td><td>${{esc(v.ciudad)}}</td>
                                                <td class="num">${{v.participaciones}}</td><td class="num">${{v.pilotos_unicos}}</td>
                                                <td class="num">${{v.visitantes_pct}}%</td>
                                            </tr>
                                        `).join("")}}
                                    </tbody>
                                </table>
                            </div>
                        </div>
                        <div class="card-box">
                            <div class="card-box-header">
                                <h3>Retención del Campeonato (Válidas Disputadas)</h3>
                                ${{helpBtn("champ_retencion")}}
                            </div>
                            ${{renderBarList(c.retention_dist.map(r => ({{lbl: r.validas_corridas + (r.validas_corridas === 1 ? " válida" : " válidas"), val: r.pilotos}})), "lbl", "val", null, true)}}
                        </div>
                    </div>

                    <div class="sub-section">
                        <div class="section-title-bar">
                            <h2>Cuadro de Honor (${{c.finalizado ? "Campeones Oficiales" : "Líderes Parciales"}})</h2>
                            <div class="section-title-actions">${{helpBtn("champ_honor")}}</div>
                        </div>
                        <div class="data-table-wrap">
                            <table class="data-table">
                                <thead>
                                    <tr><th>Categoría</th><th class="num">Pilotos</th><th>1° Puesto</th><th>2° Puesto</th><th>3° Puesto</th><th class="num">Brecha 1°-3°</th></tr>
                                </thead>
                                <tbody>
                                    ${{c.cuadro_honor.map(ch => `
                                        <tr>
                                            <td><strong>${{esc(ch.categoria)}}</strong></td>
                                            <td class="num">${{ch.pilotos}}</td>
                                            <td><strong>${{esc(ch.p1.nombre)}}</strong> <small>(${{esc(ch.p1.liga)}} · ${{ch.p1.total}} pts · ${{esc(ch.p1.moto)}})</small></td>
                                            <td>${{ch.p2 ? `${{esc(ch.p2.nombre)}} <small>(${{ch.p2.total}} pts)</small>` : "—"}}</td>
                                            <td>${{ch.p3 ? `${{esc(ch.p3.nombre)}} <small>(${{ch.p3.total}} pts)</small>` : "—"}}</td>
                                            <td class="num">${{ch.gap_1_3 != null ? ch.gap_1_3 + " pts" : "—"}}</td>
                                        </tr>
                                    `).join("")}}
                                </tbody>
                            </table>
                        </div>
                    </div>

                    <div class="sub-section two-col">
                        <div class="card-box">
                            <div class="card-box-header">
                                <h3>Medallero por Liga</h3>
                                ${{helpBtn("champ_med_liga")}}
                            </div>
                            <div class="data-table-wrap">
                                <table class="data-table">
                                    <thead><tr><th>Liga</th><th class="num">Oro</th><th class="num">Plata</th><th class="num">Bronce</th><th class="num">Total</th></tr></thead>
                                    <tbody>
                                        ${{c.medallero_ligas.map(m => `
                                            <tr><td><strong>${{esc(m.nombre)}}</strong></td><td class="num">${{m.oro}}</td><td class="num">${{m.plata}}</td><td class="num">${{m.bronce}}</td><td class="num"><strong>${{m.total}}</strong></td></tr>
                                        `).join("")}}
                                    </tbody>
                                </table>
                            </div>
                        </div>
                        <div class="card-box">
                            <div class="card-box-header">
                                <h3>Medallero por Club (Top 10)</h3>
                                ${{helpBtn("champ_med_club")}}
                            </div>
                            <div class="data-table-wrap">
                                <table class="data-table">
                                    <thead><tr><th>Club</th><th class="num">Oro</th><th class="num">Plata</th><th class="num">Bronce</th><th class="num">Total</th></tr></thead>
                                    <tbody>
                                        ${{c.medallero_clubes.slice(0, 10).map(m => `
                                            <tr><td><strong>${{esc(m.nombre)}}</strong></td><td class="num">${{m.oro}}</td><td class="num">${{m.plata}}</td><td class="num">${{m.bronce}}</td><td class="num"><strong>${{m.total}}</strong></td></tr>
                                        `).join("")}}
                                    </tbody>
                                </table>
                            </div>
                        </div>
                    </div>
                `;
            }}

            const sel = document.getElementById("selChamp");
            sel.addEventListener("change", () => updateChamp(sel.value));
            updateChamp(DATA.championships[0].id);
        }}

        // ================= TAB 4: MODALIDAD POR SEMESTRE =================
        function renderModSemestre() {{
            const el = document.getElementById("tab-modalidad-semestre");
            const mods = Object.keys(DATA.modalidad_semestre);
            el.innerHTML = `
                <div class="controls-row">
                    <label for="selModSem" style="font-weight:700;">Modalidad semestral:</label>
                    <select class="filter-select" id="selModSem">
                        ${{mods.map(m => `<option value="${{esc(m)}}">${{esc(m)}}</option>`).join("")}}
                    </select>
                </div>
                <div id="modSemBody"></div>
            `;

            function updateModSem(modName) {{
                const d = DATA.modalidad_semestre[modName];
                document.getElementById("modSemBody").innerHTML = `
                    <div class="kpi-grid">
                        <div class="kpi-card"><div class="kpi-val">${{d.pilotos_1s}}</div><div class="kpi-lbl">Pilotos 1er Semestre</div><div class="kpi-sub">${{d.validas_1s}} válidas · ${{estadoBadge(d.estado_1s)}}</div></div>
                        <div class="kpi-card"><div class="kpi-val">${{d.pilotos_2s}}</div><div class="kpi-lbl">Pilotos 2do Semestre</div><div class="kpi-sub">${{d.validas_2s}} válidas · ${{estadoBadge(d.estado_2s)}}</div></div>
                        <div class="kpi-card accent"><div class="kpi-val">${{d.tasa_continuidad_pct}}%</div><div class="kpi-lbl">Continuidad 1S → 2S</div><div class="kpi-sub">${{d.continuidad_repiten}} pilotos repitieron</div></div>
                        <div class="kpi-card accent"><div class="kpi-val">${{d.nuevos_2s}}</div><div class="kpi-lbl">Nuevos en 2do Semestre</div><div class="kpi-sub">${{d.solo_1s}} no volvieron del 1S</div></div>
                    </div>

                    <div class="two-col">
                        <div class="card-box">
                            <div class="card-box-header">
                                <h3>Comparación por Categoría (1S vs 2S)</h3>
                                ${{helpBtn("mod_sem_cats")}}
                            </div>
                            <div class="data-table-wrap">
                                <table class="data-table">
                                    <thead><tr><th>Categoría</th><th class="num">1S</th><th class="num">2S</th><th class="num">Variación</th></tr></thead>
                                    <tbody>
                                        ${{d.categorias.map(c => `
                                            <tr><td><strong>${{esc(c.nombre)}}</strong></td><td class="num">${{c.s1}}</td><td class="num">${{c.s2}}</td><td class="num">${{deltaHtml(c.s1, c.s2)}}</td></tr>
                                        `).join("")}}
                                    </tbody>
                                </table>
                            </div>
                        </div>
                        <div class="card-box">
                            <div class="card-box-header">
                                <h3>Comparación por Liga (1S vs 2S)</h3>
                                ${{helpBtn("mod_sem_ligas")}}
                            </div>
                            <div class="data-table-wrap">
                                <table class="data-table">
                                    <thead><tr><th>Liga</th><th class="num">1S</th><th class="num">2S</th><th class="num">Variación</th></tr></thead>
                                    <tbody>
                                        ${{d.ligas.map(l => `
                                            <tr><td><strong>${{esc(l.nombre)}}</strong></td><td class="num">${{l.s1}}</td><td class="num">${{l.s2}}</td><td class="num">${{deltaHtml(l.s1, l.s2)}}</td></tr>
                                        `).join("")}}
                                    </tbody>
                                </table>
                            </div>
                        </div>
                    </div>
                `;
            }}

            const sel = document.getElementById("selModSem");
            sel.addEventListener("change", () => updateModSem(sel.value));
            updateModSem(mods[0]);
        }}

        // ================= TAB 5: SEMESTRE EN GENERAL =================
        function renderSemestreGeneral() {{
            const sg = DATA.semestre_general;
            document.getElementById("tab-semestre-general").innerHTML = `
                <div class="notice-box">
                    <strong>Criterio Semestral:</strong> La comparativa directa <em>1er Semestre vs. 2do Semestre</em> consolida las 3 modalidades divididas por semestre (<strong>Motocross, Velocidad y Velotierra</strong>). Los campeonatos anuales continuos (<strong>Enduro y GP Colombia</strong>) se muestran en un bloque independiente al final.
                </div>

                <div class="kpi-grid">
                    <div class="kpi-card"><div class="kpi-val">${{sg.pilotos_1s}}</div><div class="kpi-lbl">Pilotos Únicos 1er Semestre</div><div class="kpi-sub">${{sg.participaciones_1s}} participaciones · ${{sg.validas_1s}} válidas</div></div>
                    <div class="kpi-card"><div class="kpi-val">${{sg.pilotos_2s}}</div><div class="kpi-lbl">Pilotos Únicos 2do Semestre</div><div class="kpi-sub">${{sg.participaciones_2s}} participaciones · ${{sg.validas_2s}} válidas</div></div>
                    <div class="kpi-card accent"><div class="kpi-val">${{sg.tasa_continuidad_pct}}%</div><div class="kpi-lbl">Retención Inter-Semestral</div><div class="kpi-sub">${{sg.repiten_ambos_semestres}} pilotos corrieron en ambos</div></div>
                    <div class="kpi-card accent"><div class="kpi-val">${{deltaHtml(sg.pilotos_1s, sg.pilotos_2s)}}</div><div class="kpi-lbl">Variación 1S → 2S</div><div class="kpi-sub">En licencias únicas</div></div>
                </div>

                <div class="two-col">
                    <div class="card-box">
                        <div class="card-box-header">
                            <h3>Estacionalidad por Modalidad Semestral</h3>
                            ${{helpBtn("sem_gen_mod")}}
                        </div>
                        <div class="data-table-wrap">
                            <table class="data-table">
                                <thead><tr><th>Modalidad</th><th class="num">Pilotos 1S</th><th class="num">Pilotos 2S</th><th class="num">Δ Pilotos</th><th class="num">Part. 1S</th><th class="num">Part. 2S</th></tr></thead>
                                <tbody>
                                    ${{sg.por_modalidad.map(m => `
                                        <tr>
                                            <td><strong>${{esc(m.modalidad)}}</strong></td>
                                            <td class="num">${{m.s1_pilotos}}</td><td class="num">${{m.s2_pilotos}}</td>
                                            <td class="num">${{deltaHtml(m.s1_pilotos, m.s2_pilotos)}}</td>
                                            <td class="num">${{m.s1_parts}}</td><td class="num">${{m.s2_parts}}</td>
                                        </tr>
                                    `).join("")}}
                                </tbody>
                            </table>
                        </div>
                    </div>
                    <div class="card-box">
                        <div class="card-box-header">
                            <h3>Top Ligas por Semestre (1S vs 2S)</h3>
                            ${{helpBtn("sem_gen_ligas")}}
                        </div>
                        <div class="data-table-wrap">
                            <table class="data-table">
                                <thead><tr><th>Liga</th><th class="num">1S</th><th class="num">2S</th><th class="num">Variación</th></tr></thead>
                                <tbody>
                                    ${{sg.por_liga.map(l => `
                                        <tr><td><strong>${{esc(l.liga)}}</strong></td><td class="num">${{l.s1}}</td><td class="num">${{l.s2}}</td><td class="num">${{deltaHtml(l.s1, l.s2)}}</td></tr>
                                    `).join("")}}
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>

                <div class="sub-section">
                    <div class="section-title-bar">
                        <h2>Campeonatos Anuales (No divididos en semestres)</h2>
                    </div>
                    <div class="champ-status-grid">
                        ${{sg.campeonatos_anuales.map(ca => `
                            <div class="champ-status-card">
                                <div class="champ-status-top">
                                    <span class="champ-status-title">${{esc(ca.nombre)}}</span>
                                    ${{estadoBadge(ca.estado)}}
                                </div>
                                <div class="champ-status-meta">
                                    <strong>${{ca.validas_count}}</strong> válidas · <strong>${{ca.pilotos_unicos}}</strong> pilotos únicos · <strong>${{ca.participaciones}}</strong> participaciones
                                </div>
                            </div>
                        `).join("")}}
                    </div>
                </div>
            `;
        }}

        // ================= TAB 6: INTELIGENCIA COMERCIAL =================
        function renderComercial() {{
            const cm = DATA.comercial;
            document.getElementById("tab-comercial").innerHTML = `
                <div class="two-col">
                    <div class="card-box">
                        <div class="card-box-header">
                            <h3>Cuota de Mercado y Efectividad por Marca (OEM)</h3>
                            ${{helpBtn("com_marcas")}}
                        </div>
                        <div class="data-table-wrap">
                            <table class="data-table">
                                <thead><tr><th>#</th><th>Marca</th><th class="num">Part.</th><th class="num">% Grilla</th><th class="num">Únicos</th><th class="num">Oro</th><th class="num">Podios</th></tr></thead>
                                <tbody>
                                    ${{cm.marcas.map((mk, i) => `
                                        <tr>
                                            <td>${{i + 1}}</td><td><strong>${{esc(mk.marca)}}</strong></td>
                                            <td class="num">${{mk.participaciones}}</td><td class="num">${{mk.cuota_pct}}%</td>
                                            <td class="num">${{mk.pilotos_unicos}}</td><td class="num"><strong>${{mk.oro}}</strong></td><td class="num">${{mk.podios}}</td>
                                        </tr>
                                    `).join("")}}
                                </tbody>
                            </table>
                        </div>
                    </div>
                    <div class="card-box">
                        <div class="card-box-header">
                            <h3>Conversión de Licencias: Nacionales vs. Evento (-E)</h3>
                            ${{helpBtn("com_licencias")}}
                        </div>
                        <div class="data-table-wrap" style="margin-bottom:24px;">
                            <table class="data-table">
                                <thead><tr><th>Modalidad</th><th class="num">Únicos</th><th class="num">Nacionales</th><th class="num">Evento (-E)</th><th class="num">% Evento</th></tr></thead>
                                <tbody>
                                    ${{cm.licencias_modalidad.map(lm => `
                                        <tr>
                                            <td><strong>${{esc(lm.modalidad)}}</strong></td>
                                            <td class="num">${{lm.pilotos_unicos}}</td><td class="num">${{lm.nacionales_unicos}}</td>
                                            <td class="num">${{lm.evento_unicos}}</td><td class="num"><strong>${{lm.evento_pct}}%</strong></td>
                                        </tr>
                                    `).join("")}}
                                </tbody>
                            </table>
                        </div>

                        <div class="card-box-header">
                            <h3>Top 10 Marcas en Grilla (Participaciones)</h3>
                        </div>
                        ${{renderBarList(cm.marcas.slice(0, 10), "marca", "participaciones", null, true)}}
                    </div>
                </div>

                <div class="sub-section two-col">
                    <div class="card-box">
                        <div class="card-box-header">
                            <h3>Poder de Convocatoria por Sede (Ciudades Anfitrionas)</h3>
                            ${{helpBtn("com_sedes")}}
                        </div>
                        <div class="data-table-wrap">
                            <table class="data-table">
                                <thead><tr><th>Ciudad Sede</th><th>Depto.</th><th class="num">Eventos</th><th class="num">Part.</th><th class="num">Únicos</th><th class="num">% Visitantes</th><th class="num">Lic. (-E)</th></tr></thead>
                                <tbody>
                                    ${{cm.sedes.map(s => `
                                        <tr>
                                            <td><strong>${{esc(s.ciudad)}}</strong></td><td>${{esc(s.depto)}}</td>
                                            <td class="num">${{s.validas_albergadas}}</td><td class="num">${{s.participaciones}}</td>
                                            <td class="num">${{s.pilotos_unicos}}</td><td class="num"><strong>${{s.visitantes_pct}}%</strong></td>
                                            <td class="num">${{s.licencias_evento}}</td>
                                        </tr>
                                    `).join("")}}
                                </tbody>
                            </table>
                        </div>
                    </div>
                    <div class="card-box">
                        <div class="card-box-header">
                            <h3>Ranking Nacional de Clubes Deportivos (Top 25)</h3>
                            ${{helpBtn("com_clubes")}}
                        </div>
                        <div class="data-table-wrap">
                            <table class="data-table">
                                <thead><tr><th>#</th><th>Club</th><th>Liga(s)</th><th class="num">Únicos</th><th class="num">Part.</th><th class="num">Oro</th><th class="num">Podios</th></tr></thead>
                                <tbody>
                                    ${{cm.clubes.slice(0, 25).map((cl, i) => `
                                        <tr>
                                            <td>${{i + 1}}</td><td><strong>${{esc(cl.club)}}</strong></td><td><small>${{esc(cl.ligas)}}</small></td>
                                            <td class="num">${{cl.pilotos_unicos}}</td><td class="num">${{cl.participaciones}}</td>
                                            <td class="num">${{cl.oro}}</td><td class="num">${{cl.podios}}</td>
                                        </tr>
                                    `).join("")}}
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>
            `;
        }}

        renderGeneral();
        renderModalidad();
        renderCampeonato();
        renderModSemestre();
        renderSemestreGeneral();
        renderComercial();
    </script>
</body>
</html>"""


def generate():
    data = aggregate_data()
    html_out = render_html(data)
    with open(OUTPUT_HTML, "w", encoding="utf-8") as f:
        f.write(html_out)
    print(
        f"Informe Anual 2026 generado: {OUTPUT_HTML} | "
        f"Pilotos únicos: {data['general']['pilotos_unicos']} | "
        f"Participaciones: {data['general']['participaciones']} | "
        f"Campeonatos finalizados: {data['year_status']['finalizados']}/{data['year_status']['total']}"
    )


if __name__ == "__main__":
    generate()
