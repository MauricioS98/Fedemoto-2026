# -*- coding: utf-8 -*-
"""
Generador del Informe Ejecutivo en PDF para la Marca BAJAJ — GP Colombia 2026.
Cubre las 3 válidas oficiales (GP Vitrix, GP BMW, GP IRC) y la Clasificación General Final
de las 5 categorías solicitadas:
  1. Pulsar NS 200 FI (Copa Monomarca Bajaj)
  2. 220cc 4T
  3. Street Race 250
  4. CRS Novatos
  5. CRS Expertos

Salida: Informes/GP Colombia/Informe_Ejecutivo_Bajaj_GP_Colombia_2026.pdf
Autor institucional: Mauricio Sánchez Aguilar · Jefe de Cronometraje — Comisión de Juzgamiento FEDEMOTO
Correo: cronometraje@fedemoto.org
"""

import csv
import io
import os
import re
import sys
from collections import Counter, defaultdict
from datetime import datetime

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image as PILImage

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT, TA_RIGHT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    BaseDocTemplate,
    Frame,
    Image,
    KeepTogether,
    PageBreak,
    PageTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
INFORMES_DIR = os.path.normpath(os.path.join(SCRIPT_DIR, ".."))
ROOT_DIR = os.path.normpath(os.path.join(INFORMES_DIR, ".."))
GEN_DIR = os.path.join(ROOT_DIR, "Resultados generales")
GP_VALIDAS_DIR = os.path.join(ROOT_DIR, "Resultados_validas", "GP Colombia")

for p in (INFORMES_DIR, GEN_DIR, GP_VALIDAS_DIR):
    if p not in sys.path:
        sys.path.insert(0, p)

import generar_informe_anual_2026 as gia  # noqa: E402
import generar_resultados_generales as grg  # noqa: E402
import generar_valida_i_gp_vitrix as gp1  # noqa: E402
import generar_valida_ii_gp_bmw as gp2  # noqa: E402
import generar_valida_iii_gp_irc as gp3  # noqa: E402

OUTPUT_PDF = os.path.join(SCRIPT_DIR, "Informe_Ejecutivo_Bajaj_GP_Colombia_2026.pdf")
LOGO_PATH = os.path.join(ROOT_DIR, "fedemoto-logo.png")

TARGET_CATS = [
    "Pulsar NS 200 FI",
    "220cc 4T",
    "Street Race 250",
    "CRS Novatos",
    "CRS Expertos",
]

# Paleta institucional FEDEMOTO + acento Bajaj
C_NAVY = colors.HexColor("#123E92")
C_NAVY_DARK = colors.HexColor("#0B2861")
C_BAJAJ_BLUE = colors.HexColor("#0056B3")
C_BAJAJ_LIGHT = colors.HexColor("#E8F1FD")
C_GOLD = colors.HexColor("#F7C31D")
C_GOLD_SOFT = colors.HexColor("#FFFBEB")
C_GOLD_BORDER = colors.HexColor("#F59E0B")
C_SLATE_900 = colors.HexColor("#0F172A")
C_SLATE_700 = colors.HexColor("#334155")
C_SLATE_500 = colors.HexColor("#64748B")
C_SLATE_200 = colors.HexColor("#E2E8F0")
C_SLATE_100 = colors.HexColor("#F1F5F9")
C_SLATE_50 = colors.HexColor("#F8FAFC")
C_GREEN_BG = colors.HexColor("#DCFCE7")
C_GREEN_TXT = colors.HexColor("#166534")
C_WHITE = colors.white


def register_fonts():
    win_fonts = r"C:\Windows\Fonts"
    candidates = [
        ("SegoeUI", "segoeui.ttf", "segoeuib.ttf", "segoeuii.ttf"),
        ("Calibri", "calibri.ttf", "calibrib.ttf", "calibrii.ttf"),
        ("Arial", "arial.ttf", "arialbd.ttf", "ariali.ttf"),
    ]
    for fam, reg, bold, ital in candidates:
        rp = os.path.join(win_fonts, reg)
        bp = os.path.join(win_fonts, bold)
        ip = os.path.join(win_fonts, ital)
        if os.path.isfile(rp) and os.path.isfile(bp):
            pdfmetrics.registerFont(TTFont(fam, rp))
            pdfmetrics.registerFont(TTFont(f"{fam}-Bold", bp))
            if os.path.isfile(ip):
                pdfmetrics.registerFont(TTFont(f"{fam}-Italic", ip))
            else:
                pdfmetrics.registerFont(TTFont(f"{fam}-Italic", rp))
            return fam, f"{fam}-Bold", f"{fam}-Italic"
    return "Helvetica", "Helvetica-Bold", "Helvetica-Oblique"


FONT_REG, FONT_BOLD, FONT_ITAL = register_fonts()


def clean_person_name(raw):
    s = " ".join(str(raw or "").strip().split())
    if not s:
        return ""
    out = []
    for w in s.split():
        if len(w) <= 2 and w.endswith("."):
            out.append(w.upper())
        else:
            out.append(w[0].upper() + w[1:].lower())
    return " ".join(out)


def fmt_pts(val):
    if val is None:
        return "—"
    f = float(val)
    return str(int(f)) if abs(f - int(f)) < 1e-6 else f"{f:.1f}"


def fmt_pct(val):
    return f"{val:.1f}%".replace(".", ",")


def time_to_sec(t):
    s = str(t or "").strip()
    if not s:
        return None
    if re.match(r"^\d+:\d{2}(\.\d+)?$", s):
        p = s.split(":")
        return int(p[0]) * 60 + float(p[1])
    if re.match(r"^\d{1,2}\.\d+$", s):
        return float(s)
    return None


def collect_bajaj_dataset():
    """Recopila todas las métricas verificadas de las 5 categorías en las 3 válidas de GP Colombia 2026."""
    annual = gia.aggregate_data()
    gp_mod_data = annual["modalidades"]["GP Colombia"]
    global_meta = gia.build_global_rider_metadata()

    gp_champ_cfg = [c for c in grg.CHAMPIONSHIPS if c["id"] == "gp_colombia_2026"][0]
    gen_table = grg.build_general_table(gp_champ_cfg)

    validas_spec = [
        ("I", "I Válida — GP Vitrix", "Gran Premio Vitrix", "Trazado Largo (2.725 m)", gp1, gp_champ_cfg["validas"][0]["files_dir"]),
        ("II", "II Válida — GP BMW", "Gran Premio BMW", "Trazado Corto-Medio", gp2, gp_champ_cfg["validas"][1]["files_dir"]),
        ("III", "III Válida Final — GP IRC", "Gran Premio IRC (Final)", "Trazado Largo (2.725 m)", gp3, gp_champ_cfg["validas"][2]["files_dir"]),
    ]

    cat_rider_meta = defaultdict(lambda: defaultdict(lambda: {"motos": [], "liga": "", "club": "", "nombre": ""}))
    global_gp_rider_meta = defaultdict(lambda: {"liga": "", "club": "", "moto": "", "nombre": ""})

    def norm_rider_for_cat(cat, num, nom):
        nom_s = " ".join(str(nom or "").strip().split())
        if cat == "Pulsar NS 200 FI":
            nk = grg.normalize_rider_name(nom_s)
            if nk in grg.PULSAR_VITRIX_NAME_ALIASES:
                nom_s = grg.PULSAR_VITRIX_NAME_ALIASES[nk]
        nk = grg.normalize_rider_name(nom_s)
        return nk or f"num_{num}", nom_s

    raw_cat_map = {
        "pulsar": "Pulsar NS 200 FI",
        "220": "220cc 4T",
        "street": "Street Race 250",
        "crs expertos": "CRS Expertos",
        "crs novatos": "CRS Novatos",
    }

    raw_session_moto = {}
    for v_code, _vl, _vs, _circ, _mod, fdir in validas_spec:
        for fn in sorted(os.listdir(fdir)):
            if not fn.lower().endswith(".csv"):
                continue
            fl = gia.strip_accents(fn).lower()
            with open(os.path.join(fdir, fn), "r", encoding="utf-8-sig", errors="ignore") as f:
                lines = f.read().splitlines()
            if not lines:
                continue
            delim = ";" if lines[0].count(";") > lines[0].count(",") else ","
            rows = list(csv.reader(lines, delimiter=delim))
            if not rows:
                continue
            idx = grg.find_indexes(rows[0])
            matched_cat = None
            for kw, cname in raw_cat_map.items():
                if kw in fl:
                    matched_cat = cname
                    break
            for r in rows[1:]:
                num = str(r[idx["numero"]]).strip() if idx["numero"] is not None and idx["numero"] < len(r) else ""
                nom = str(r[idx["nombre"]]).strip() if idx["nombre"] is not None and idx["nombre"] < len(r) else ""
                if not num and not nom:
                    continue
                liga = gia.clean_liga(r[idx["liga"]]) if idx["liga"] is not None and idx["liga"] < len(r) else ""
                club = gia.clean_club(r[idx["club"]]) if idx["club"] is not None and idx["club"] < len(r) else ""
                moto = gia.clean_marca(r[idx["moto"]]) if idx["moto"] is not None and idx["moto"] < len(r) else ""
                nk_g = grg.normalize_rider_name(nom)
                if nk_g:
                    gm = global_gp_rider_meta[nk_g]
                    if len(nom) > len(gm["nombre"]):
                        gm["nombre"] = nom
                    if liga and not gm["liga"]:
                        gm["liga"] = liga
                    if club and not gm["club"]:
                        gm["club"] = club
                    if moto and not gm["moto"]:
                        gm["moto"] = moto
                if matched_cat:
                    rk, clean_nom = norm_rider_for_cat(matched_cat, num, nom)
                    cm = cat_rider_meta[matched_cat][rk]
                    if len(clean_nom) > len(cm["nombre"]):
                        cm["nombre"] = clean_nom
                    if liga and not cm["liga"]:
                        cm["liga"] = liga
                    if club and not cm["club"]:
                        cm["club"] = club
                    if moto:
                        cm["motos"].append((v_code, moto))
                        raw_session_moto[(v_code, matched_cat, rk)] = moto
                        raw_session_moto[(v_code, matched_cat, f"num_{num}")] = moto

    def resolve_rider_fields(v_code, cat, num, nom, row_liga="", row_club="", row_moto=""):
        rk, clean_nom = norm_rider_for_cat(cat, num, nom)
        cm = cat_rider_meta[cat].get(rk, {})
        gm = global_gp_rider_meta.get(rk, {})
        gl = global_meta.get(rk, {})

        best_nom = clean_person_name(cm.get("nombre") or gm.get("nombre") or gl.get("nombre") or clean_nom)
        best_liga = gia.clean_liga(row_liga) or cm.get("liga") or gm.get("liga") or gl.get("liga") or ""
        best_club = gia.clean_club(row_club) or cm.get("club") or gm.get("club") or gl.get("club") or ""

        if cat == "Pulsar NS 200 FI":
            best_moto = "Bajaj"
        else:
            m = raw_session_moto.get((v_code, cat, rk)) or raw_session_moto.get((v_code, cat, f"num_{num}"))
            if not m and row_moto:
                m = gia.clean_marca(row_moto)
            if not m and cm.get("motos"):
                m = Counter(x[1] for x in cm["motos"]).most_common(1)[0][0]
            if not m:
                m = gm.get("moto") or gl.get("moto") or "Sin Registro"
            best_moto = m

        return rk, best_nom, best_liga, best_club, best_moto

    categories_out = {tc: {"nombre": tc, "validas": [], "general_standings": []} for tc in TARGET_CATS}
    all_parts = []

    for v_code, v_label, v_short, circ_label, mod, _fdir in validas_spec:
        cats_data = mod.load_categorias_data()
        for tc in TARGET_CATS:
            items = cats_data.get(tc, [])
            qual_session = None
            race_session = None
            for tipo, _sk, headers, rows, _com in items:
                tl = gia.strip_accents(tipo).lower()
                if "carrera" in tl:
                    race_session = (tipo, headers, rows)
                elif "clasif" in tl or "practica" in tl:
                    if qual_session is None or "final" in tl:
                        qual_session = (tipo, headers, rows)

            seen_riders = {}
            pole_info = None
            best_qual_lap = None

            if qual_session:
                _, qh, qr = qual_session
                qidx = grg.find_indexes(qh)
                q_tm_idx = next((i for i, h in enumerate(qh) if "mejor" in h.lower()), -1)
                for r in qr:
                    if qidx["numero"] is None or len(r) <= qidx["numero"]:
                        continue
                    num = str(r[qidx["numero"]]).strip()
                    nom = str(r[qidx["nombre"]]).strip() if qidx["nombre"] is not None and qidx["nombre"] < len(r) else ""
                    if not num:
                        continue
                    rl = r[qidx["liga"]] if qidx["liga"] is not None and qidx["liga"] < len(r) else ""
                    rc = r[qidx["club"]] if qidx["club"] is not None and qidx["club"] < len(r) else ""
                    rm = r[qidx["moto"]] if qidx["moto"] is not None and qidx["moto"] < len(r) else ""
                    rk, bnom, bliga, bclub, bmoto = resolve_rider_fields(v_code, tc, num, nom, rl, rc, rm)
                    pos_s = str(r[qidx["pos"]]).strip() if qidx["pos"] is not None and qidx["pos"] < len(r) else ""
                    tm_s = str(r[q_tm_idx]).strip() if 0 <= q_tm_idx < len(r) else ""
                    seen_riders[rk] = {
                        "rk": rk,
                        "numero": num,
                        "nombre": bnom,
                        "liga": bliga,
                        "club": bclub,
                        "moto": bmoto,
                        "es_evento": num.upper().endswith("-E"),
                        "in_qual": True,
                        "in_race": False,
                        "finished_race": False,
                        "race_pos": None,
                    }
                    if pos_s == "1":
                        pole_info = {"numero": num, "nombre": bnom, "moto": bmoto, "liga": bliga, "tiempo": tm_s}
                    sec = time_to_sec(tm_s)
                    if sec and (best_qual_lap is None or sec < best_qual_lap["sec"]):
                        best_qual_lap = {"numero": num, "nombre": bnom, "moto": bmoto, "tiempo": tm_s, "sec": sec}

            race_podium = []
            best_race_lap = None
            race_starts = race_finished = race_dnf = 0
            bajaj_starts = bajaj_finished = 0
            gap_1_2 = gap_1_3 = laps_completed = ""

            # Reference valid pace from Pole or Winner to discard transponder/shortcut outliers
            ref_pace_sec = None
            if best_qual_lap:
                ref_pace_sec = best_qual_lap["sec"]

            if race_session:
                _, rh, rr = race_session
                ridx = grg.find_indexes(rh)
                r_tm_idx = next((i for i, h in enumerate(rh) if "mejor" in h.lower()), -1)
                r_dif_idx = next((i for i, h in enumerate(rh) if "dif" in h.lower() and "1" in h.lower()), -1)
                r_vuel_idx = next((i for i, h in enumerate(rh) if "vuelta" in h.lower()), -1)

                # Determine winner's best lap as pace baseline if no qualifying
                for r0 in rr:
                    if ridx["pos"] is not None and ridx["pos"] < len(r0) and str(r0[ridx["pos"]]).strip() == "1":
                        w_sec = time_to_sec(r0[r_tm_idx]) if 0 <= r_tm_idx < len(r0) else None
                        if w_sec and (ref_pace_sec is None or w_sec < ref_pace_sec):
                            ref_pace_sec = w_sec
                        break

                for r in rr:
                    if ridx["numero"] is None or len(r) <= ridx["numero"]:
                        continue
                    num = str(r[ridx["numero"]]).strip()
                    nom = str(r[ridx["nombre"]]).strip() if ridx["nombre"] is not None and ridx["nombre"] < len(r) else ""
                    if not num:
                        continue
                    rl = r[ridx["liga"]] if ridx["liga"] is not None and ridx["liga"] < len(r) else ""
                    rc = r[ridx["club"]] if ridx["club"] is not None and ridx["club"] < len(r) else ""
                    rm = r[ridx["moto"]] if ridx["moto"] is not None and ridx["moto"] < len(r) else ""
                    rk, bnom, bliga, bclub, bmoto = resolve_rider_fields(v_code, tc, num, nom, rl, rc, rm)

                    pos_s = str(r[ridx["pos"]]).strip().upper() if ridx["pos"] is not None and ridx["pos"] < len(r) else ""
                    pts_val = grg.parse_points(r[ridx["puntos"]]) if ridx["puntos"] is not None and ridx["puntos"] < len(r) else 0.0
                    tm_s = str(r[r_tm_idx]).strip() if 0 <= r_tm_idx < len(r) else ""
                    dif_s = str(r[r_dif_idx]).strip() if 0 <= r_dif_idx < len(r) else ""
                    vuel_s = str(r[r_vuel_idx]).strip() if 0 <= r_vuel_idx < len(r) else ""

                    is_fin = bool(re.match(r"^\d+$", pos_s))
                    pos_int = int(pos_s) if is_fin else None

                    race_starts += 1
                    if is_fin:
                        race_finished += 1
                    else:
                        race_dnf += 1
                    if bmoto == "Bajaj":
                        bajaj_starts += 1
                        if is_fin:
                            bajaj_finished += 1

                    entry = seen_riders.setdefault(rk, {
                        "rk": rk,
                        "numero": num,
                        "nombre": bnom,
                        "liga": bliga,
                        "club": bclub,
                        "moto": bmoto,
                        "es_evento": num.upper().endswith("-E"),
                        "in_qual": False,
                        "in_race": True,
                        "finished_race": is_fin,
                        "race_pos": pos_int,
                    })
                    entry["in_race"] = True
                    entry["finished_race"] = is_fin
                    entry["race_pos"] = pos_int
                    if bliga and not entry["liga"]:
                        entry["liga"] = bliga
                    if bclub and not entry["club"]:
                        entry["club"] = bclub
                    if bmoto and entry["moto"] in ("", "Sin Registro"):
                        entry["moto"] = bmoto

                    if pos_int in (1, 2, 3):
                        if pos_int == 1 and vuel_s:
                            laps_completed = vuel_s
                        if pos_int == 2:
                            gap_1_2 = dif_s
                        elif pos_int == 3:
                            gap_1_3 = dif_s
                        race_podium.append({
                            "pos": pos_int,
                            "numero": num,
                            "nombre": bnom,
                            "liga": bliga or "—",
                            "club": bclub or "—",
                            "moto": bmoto,
                            "puntos": pts_val,
                            "mejor_tm": tm_s or "—",
                            "dif": f"+{dif_s} s" if (pos_int > 1 and dif_s and "vuelta" not in dif_s.lower()) else (dif_s if pos_int > 1 else "Ganador"),
                            "vueltas": vuel_s or "—",
                        })

                    sec = time_to_sec(tm_s)
                    # Solo considerar vueltas válidas de pilotos clasificados sin anomalía de transpondedor (>3.0s bajo el ritmo de punta)
                    valid_lap = is_fin and sec is not None and (ref_pace_sec is None or sec >= ref_pace_sec - 3.0)
                    if valid_lap and (best_race_lap is None or sec < best_race_lap["sec"]):
                        best_race_lap = {"numero": num, "nombre": bnom, "moto": bmoto, "tiempo": tm_s, "sec": sec}

            race_podium.sort(key=lambda x: x["pos"])
            brand_counts_all = Counter(x["moto"] for x in seen_riders.values())

            for x in seen_riders.values():
                all_parts.append({
                    **x,
                    "valida": v_code,
                    "valida_label": v_label,
                    "categoria": tc,
                })

            categories_out[tc]["validas"].append({
                "valida": v_code,
                "valida_label": v_label,
                "valida_short": v_short,
                "circuito": circ_label,
                "inscritos_totales": len(seen_riders),
                "clasificatoria_pilotos": sum(1 for x in seen_riders.values() if x["in_qual"]),
                "grilla_carrera": race_starts,
                "finalizados": race_finished,
                "dnf": race_dnf,
                "efectividad_pct": round(race_finished / race_starts * 100, 1) if race_starts else 0.0,
                "bajaj_inscritos": brand_counts_all.get("Bajaj", 0),
                "bajaj_cuota_pct": round(brand_counts_all.get("Bajaj", 0) / len(seen_riders) * 100, 1) if seen_riders else 0.0,
                "bajaj_carrera": bajaj_starts,
                "bajaj_finalizados": bajaj_finished,
                "bajaj_efectividad_pct": round(bajaj_finished / bajaj_starts * 100, 1) if bajaj_starts else 0.0,
                "marcas": dict(brand_counts_all.most_common()),
                "pole": pole_info,
                "mejor_vuelta_clasif": best_qual_lap,
                "mejor_vuelta_carrera": best_race_lap,
                "vueltas_carrera": laps_completed,
                "gap_1_2": gap_1_2,
                "gap_1_3": gap_1_3,
                "podio": race_podium,
            })

    for tc in TARGET_CATS:
        rows = gen_table.get(tc, [])
        standings = []
        for idx_pos, r in enumerate(rows, 1):
            rk, bnom, bliga, bclub, bmoto = resolve_rider_fields(
                "GEN", tc, r["numero"], r["nombre"], r.get("liga", ""), r.get("club", ""), r.get("moto", "")
            )
            standings.append({
                "pos": idx_pos,
                "numero": r["numero"],
                "nombre": bnom,
                "liga": bliga or "—",
                "club": bclub or "—",
                "moto": bmoto,
                "v1": r["por_valida"][0],
                "v2": r["por_valida"][1],
                "v3": r["por_valida"][2],
                "bono": r["bonificacion_asistencia"],
                "total": r["total"],
            })
        categories_out[tc]["general_standings"] = standings

    return {
        "gp_macro": {
            "participaciones_totales_gp": gp_mod_data["participaciones"],
            "pilotos_unicos_gp": gp_mod_data["pilotos_unicos"],
            "categorias_totales_gp": len(gp_mod_data["categorias"]),
        },
        "categories": categories_out,
        "participations": all_parts,
    }


def make_chart_image(fig, width_mm, height_mm):
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=260, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    buf.seek(0)
    return Image(buf, width=width_mm * mm, height=height_mm * mm)


def build_chart_brand_and_evolution(dataset):
    parts = dataset["participations"]
    cats = dataset["categories"]

    plt.rcParams["font.sans-serif"] = ["Segoe UI", "Calibri", "Arial", "DejaVu Sans"]
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10.6, 3.65), gridspec_kw={"width_ratios": [1.22, 1.0]})
    fig.patch.set_facecolor("white")

    # Panel 1: Participaciones Bajaj vs Otras Marcas por Categoría (acumulado 3 válidas)
    cat_labels = ["CRS Novatos", "220cc 4T", "Street Race 250", "CRS Expertos", "Pulsar NS 200 FI"]
    bajaj_vals = []
    other_vals = []
    for c in cat_labels:
        cp = [p for p in parts if p["categoria"] == c]
        b = sum(1 for p in cp if p["moto"] == "Bajaj")
        bajaj_vals.append(b)
        other_vals.append(len(cp) - b)

    y = np.arange(len(cat_labels))
    ax1.barh(y, bajaj_vals, height=0.56, color="#123E92", label="Motocicletas Bajaj")
    ax1.barh(y, other_vals, left=bajaj_vals, height=0.56, color="#CBD5E1", label="Otras marcas / S.R.")
    ax1.set_yticks(y)
    ax1.set_yticklabels(cat_labels, fontsize=8.8, fontweight="bold", color="#0F172A")
    ax1.invert_yaxis()
    ax1.set_xlabel("Participaciones acumuladas (3 válidas)", fontsize=8.2, color="#334155")
    ax1.set_title("Dominio de Grilla Bajaj por Categoría", fontsize=10, fontweight="bold", color="#123E92", pad=8)
    ax1.set_xlim(0, max(b + o for b, o in zip(bajaj_vals, other_vals)) * 1.24)
    ax1.grid(axis="x", linestyle="--", alpha=0.35, color="#94A3B8")
    ax1.spines["top"].set_visible(False)
    ax1.spines["right"].set_visible(False)
    ax1.legend(loc="lower right", fontsize=7.6, frameon=True, facecolor="white", edgecolor="#E2E8F0")

    for i, (b, o) in enumerate(zip(bajaj_vals, other_vals)):
        tot = b + o
        pct = b / tot * 100 if tot else 0
        ax1.text(tot + 3, i, f"{b}/{tot} ({pct:.1f}%)", va="center", fontsize=8.0, fontweight="bold", color="#123E92")

    # Panel 2: Evolución por Válida (I, II, III) Bajaj vs Otras Marcas en las 5 categorías
    v_codes = ["I", "II", "III"]
    v_names = ["I Válida\nGP Vitrix", "II Válida\nGP BMW", "III Válida Final\nGP IRC"]
    v_bajaj = []
    v_other = []
    for vc in v_codes:
        vp = [p for p in parts if p["valida"] == vc]
        vb = sum(1 for p in vp if p["moto"] == "Bajaj")
        v_bajaj.append(vb)
        v_other.append(len(vp) - vb)

    x = np.arange(len(v_codes))
    w = 0.48
    ax2.bar(x, v_bajaj, width=w, color="#123E92", label="Bajaj")
    ax2.bar(x, v_other, bottom=v_bajaj, width=w, color="#F7C31D", label="Otras marcas")
    ax2.set_xticks(x)
    ax2.set_xticklabels(v_names, fontsize=8.3, fontweight="bold", color="#0F172A")
    ax2.set_ylabel("Participaciones", fontsize=8.2, color="#334155")
    ax2.set_title("Evolución por Válida (5 Categorías)", fontsize=10, fontweight="bold", color="#123E92", pad=8)
    ax2.set_ylim(0, max(b + o for b, o in zip(v_bajaj, v_other)) * 1.22)
    ax2.grid(axis="y", linestyle="--", alpha=0.35, color="#94A3B8")
    ax2.spines["top"].set_visible(False)
    ax2.spines["right"].set_visible(False)
    ax2.legend(loc="upper right", fontsize=7.6, frameon=True, facecolor="white", edgecolor="#E2E8F0")

    for i, (b, o) in enumerate(zip(v_bajaj, v_other)):
        tot = b + o
        pct = b / tot * 100 if tot else 0
        ax2.text(i, tot + 5, f"{tot} total\n({pct:.1f}% Bajaj)", ha="center", va="bottom", fontsize=7.6, fontweight="bold", color="#0B2861")

    fig.tight_layout(pad=1.2)
    return make_chart_image(fig, 182, 62)


def build_chart_territorial(dataset):
    parts = dataset["participations"]
    liga_all = defaultdict(set)
    liga_bajaj = defaultdict(set)
    club_all = defaultdict(set)
    club_bajaj = defaultdict(set)

    for p in parts:
        if p["liga"]:
            liga_all[p["liga"]].add(p["rk"])
            if p["moto"] == "Bajaj":
                liga_bajaj[p["liga"]].add(p["rk"])
        if p["club"]:
            club_all[p["club"]].add(p["rk"])
            if p["moto"] == "Bajaj":
                club_bajaj[p["club"]].add(p["rk"])

    top_ligas = sorted(liga_all.items(), key=lambda x: (-len(x[1]), x[0]))[:10]
    top_clubs = sorted(club_all.items(), key=lambda x: (-len(club_bajaj[x[0]]), -len(x[1]), x[0]))[:8]

    plt.rcParams["font.sans-serif"] = ["Segoe UI", "Calibri", "Arial", "DejaVu Sans"]
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10.6, 3.55), gridspec_kw={"width_ratios": [1.0, 1.15]})
    fig.patch.set_facecolor("white")

    l_names = [k for k, _ in top_ligas]
    l_b = [len(liga_bajaj[k]) for k, _ in top_ligas]
    l_o = [len(v) - len(liga_bajaj[k]) for k, v in top_ligas]
    y1 = np.arange(len(l_names))
    ax1.barh(y1, l_b, height=0.58, color="#123E92", label="Pilotos Bajaj")
    ax1.barh(y1, l_o, left=l_b, height=0.58, color="#CBD5E1", label="Otras marcas")
    ax1.set_yticks(y1)
    ax1.set_yticklabels(l_names, fontsize=8.2, fontweight="bold", color="#0F172A")
    ax1.invert_yaxis()
    ax1.set_title("Top 10 Ligas Departamentales (Pilotos Únicos)", fontsize=9.5, fontweight="bold", color="#123E92", pad=7)
    ax1.set_xlim(0, max(b + o for b, o in zip(l_b, l_o)) * 1.24)
    ax1.grid(axis="x", linestyle="--", alpha=0.35, color="#94A3B8")
    ax1.spines["top"].set_visible(False)
    ax1.spines["right"].set_visible(False)
    ax1.legend(loc="lower right", fontsize=7.4, frameon=True, facecolor="white", edgecolor="#E2E8F0")
    for i, (b, o) in enumerate(zip(l_b, l_o)):
        ax1.text(b + o + 0.8, i, f"{b}/{b+o}", va="center", fontsize=7.8, fontweight="bold", color="#123E92")

    c_names = [k[:27] + ("…" if len(k) > 27 else "") for k, _ in top_clubs]
    c_b = [len(club_bajaj[k]) for k, _ in top_clubs]
    c_o = [len(v) - len(club_bajaj[k]) for k, v in top_clubs]
    y2 = np.arange(len(c_names))
    ax2.barh(y2, c_b, height=0.58, color="#0056B3", label="Pilotos Bajaj")
    ax2.barh(y2, c_o, left=c_b, height=0.58, color="#E2E8F0", label="Otras marcas")
    ax2.set_yticks(y2)
    ax2.set_yticklabels(c_names, fontsize=7.9, fontweight="bold", color="#0F172A")
    ax2.invert_yaxis()
    ax2.set_title("Clubes Deportivos con Mayor Flota Bajaj", fontsize=9.5, fontweight="bold", color="#123E92", pad=7)
    ax2.set_xlim(0, max(b + o for b, o in zip(c_b, c_o)) * 1.24)
    ax2.grid(axis="x", linestyle="--", alpha=0.35, color="#94A3B8")
    ax2.spines["top"].set_visible(False)
    ax2.spines["right"].set_visible(False)
    ax2.legend(loc="lower right", fontsize=7.4, frameon=True, facecolor="white", edgecolor="#E2E8F0")
    for i, (b, o) in enumerate(zip(c_b, c_o)):
        ax2.text(b + o + 0.6, i, f"{b} Bajaj ({b+o} tot.)", va="center", fontsize=7.6, fontweight="bold", color="#0056B3")

    fig.tight_layout(pad=1.1)
    return make_chart_image(fig, 182, 52)


def get_styles():
    return {
        "h1_sec": ParagraphStyle(
            "h1_sec",
            fontName=FONT_BOLD,
            fontSize=12.5,
            leading=15,
            textColor=C_NAVY,
            spaceBefore=2 * mm,
            spaceAfter=2 * mm,
        ),
        "h2_sub": ParagraphStyle(
            "h2_sub",
            fontName=FONT_BOLD,
            fontSize=9.8,
            leading=12,
            textColor=C_NAVY_DARK,
            spaceBefore=2.2 * mm,
            spaceAfter=1.2 * mm,
        ),
        "body": ParagraphStyle(
            "body",
            fontName=FONT_REG,
            fontSize=8.5,
            leading=11.8,
            textColor=C_SLATE_700,
            alignment=TA_JUSTIFY,
            spaceAfter=1.8 * mm,
        ),
        "bullet": ParagraphStyle(
            "bullet",
            fontName=FONT_REG,
            fontSize=8.3,
            leading=11.4,
            textColor=C_SLATE_700,
            leftIndent=3.5 * mm,
            spaceAfter=1.2 * mm,
        ),
        "note": ParagraphStyle(
            "note",
            fontName=FONT_ITAL,
            fontSize=7.4,
            leading=9.8,
            textColor=C_SLATE_500,
            spaceBefore=1 * mm,
            spaceAfter=1.5 * mm,
        ),
        "th": ParagraphStyle(
            "th",
            fontName=FONT_BOLD,
            fontSize=7.6,
            leading=9.2,
            textColor=C_WHITE,
            alignment=TA_CENTER,
        ),
        "th_l": ParagraphStyle(
            "th_l",
            fontName=FONT_BOLD,
            fontSize=7.6,
            leading=9.2,
            textColor=C_WHITE,
            alignment=TA_LEFT,
        ),
        "td": ParagraphStyle(
            "td",
            fontName=FONT_REG,
            fontSize=7.5,
            leading=9.3,
            textColor=C_SLATE_900,
            alignment=TA_CENTER,
        ),
        "td_b": ParagraphStyle(
            "td_b",
            fontName=FONT_BOLD,
            fontSize=7.5,
            leading=9.3,
            textColor=C_SLATE_900,
            alignment=TA_CENTER,
        ),
        "td_l": ParagraphStyle(
            "td_l",
            fontName=FONT_REG,
            fontSize=7.5,
            leading=9.3,
            textColor=C_SLATE_900,
            alignment=TA_LEFT,
        ),
        "td_lb": ParagraphStyle(
            "td_lb",
            fontName=FONT_BOLD,
            fontSize=7.5,
            leading=9.3,
            textColor=C_NAVY_DARK,
            alignment=TA_LEFT,
        ),
        "kpi_num": ParagraphStyle(
            "kpi_num",
            fontName=FONT_BOLD,
            fontSize=15.5,
            leading=17.5,
            textColor=C_NAVY,
            alignment=TA_CENTER,
        ),
        "kpi_lbl": ParagraphStyle(
            "kpi_lbl",
            fontName=FONT_BOLD,
            fontSize=7.2,
            leading=9.0,
            textColor=C_SLATE_900,
            alignment=TA_CENTER,
        ),
        "kpi_sub": ParagraphStyle(
            "kpi_sub",
            fontName=FONT_REG,
            fontSize=6.7,
            leading=8.3,
            textColor=C_SLATE_500,
            alignment=TA_CENTER,
        ),
    }


def section_banner(title_text, subtitle_text=""):
    st_t = ParagraphStyle("sb_t", fontName=FONT_BOLD, fontSize=11.2, leading=13.5, textColor=C_WHITE)
    st_s = ParagraphStyle("sb_s", fontName=FONT_REG, fontSize=8.0, leading=10.0, textColor=colors.HexColor("#DBEAFE"), alignment=TA_RIGHT)
    if subtitle_text:
        row = [[Paragraph(title_text, st_t), Paragraph(subtitle_text, st_s)]]
        tbl = Table(row, colWidths=[116 * mm, 66 * mm])
    else:
        row = [[Paragraph(title_text, st_t)]]
        tbl = Table(row, colWidths=[182 * mm])
    tbl.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), C_NAVY),
        ("LINEBELOW", (0, 0), (-1, -1), 2.2, C_GOLD),
        ("LEFTPADDING", (0, 0), (-1, -1), 3.5 * mm),
        ("RIGHTPADDING", (0, 0), (-1, -1), 3.5 * mm),
        ("TOPPADDING", (0, 0), (-1, -1), 2.2 * mm),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2.2 * mm),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]))
    return tbl


def make_kpi_grid(cards, cols=4, total_width_mm=182):
    st = get_styles()
    col_w = (total_width_mm / cols) * mm
    rows = []
    for i in range(0, len(cards), cols):
        chunk = cards[i:i + cols]
        row_cells = []
        for num_txt, lbl_txt, sub_txt in chunk:
            cell_content = [
                Paragraph(num_txt, st["kpi_num"]),
                Spacer(1, 0.6 * mm),
                Paragraph(lbl_txt, st["kpi_lbl"]),
                Spacer(1, 0.4 * mm),
                Paragraph(sub_txt, st["kpi_sub"]),
            ]
            row_cells.append(cell_content)
        rows.append(row_cells)

    tbl = Table(rows, colWidths=[col_w] * cols)
    tbl.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), C_SLATE_50),
        ("GRID", (0, 0), (-1, -1), 0.8, C_SLATE_200),
        ("LINEABOVE", (0, 0), (-1, 0), 2.0, C_NAVY),
        ("TOPPADDING", (0, 0), (-1, -1), 2.3 * mm),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2.3 * mm),
        ("LEFTPADDING", (0, 0), (-1, -1), 1.8 * mm),
        ("RIGHTPADDING", (0, 0), (-1, -1), 1.8 * mm),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]))
    return tbl


def standard_table_style(num_rows, highlight_bajaj_rows=None, gold_top_rows=None, compact=False):
    pad_v = 1.05 * mm if compact else 1.30 * mm
    cmds = [
        ("BACKGROUND", (0, 0), (-1, 0), C_NAVY),
        ("TEXTCOLOR", (0, 0), (-1, 0), C_WHITE),
        ("LINEBELOW", (0, 0), (-1, 0), 1.5, C_GOLD),
        ("GRID", (0, 0), (-1, -1), 0.45, C_SLATE_200),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, 0), 1.75 * mm),
        ("BOTTOMPADDING", (0, 0), (-1, 0), 1.75 * mm),
        ("TOPPADDING", (0, 1), (-1, -1), pad_v),
        ("BOTTOMPADDING", (0, 1), (-1, -1), pad_v),
        ("LEFTPADDING", (0, 0), (-1, -1), 1.5 * mm),
        ("RIGHTPADDING", (0, 0), (-1, -1), 1.5 * mm),
    ]
    for r in range(1, num_rows):
        if r % 2 == 0:
            cmds.append(("BACKGROUND", (0, r), (-1, r), C_SLATE_50))
    if highlight_bajaj_rows:
        for r in highlight_bajaj_rows:
            cmds.append(("BACKGROUND", (0, r), (-1, r), C_BAJAJ_LIGHT))
    if gold_top_rows:
        for r in gold_top_rows:
            cmds.append(("BACKGROUND", (0, r), (-1, r), C_GOLD_SOFT))
    return TableStyle(cmds)


def draw_header_footer(canvas, doc):
    canvas.saveState()
    w, h = A4
    page_num = canvas.getPageNumber()

    if page_num > 1:
        # Running institutional header on interior pages
        canvas.setFillColor(C_NAVY)
        canvas.rect(0, h - 15 * mm, w, 15 * mm, stroke=0, fill=1)
        canvas.setFillColor(C_GOLD)
        canvas.rect(0, h - 15.8 * mm, w, 0.8 * mm, stroke=0, fill=1)

        if os.path.isfile(LOGO_PATH):
            with PILImage.open(LOGO_PATH) as im:
                aspect = im.size[0] / float(im.size[1])
            lh = 9.6 * mm
            lw = lh * aspect
            canvas.setFillColor(C_WHITE)
            canvas.roundRect(13.5 * mm, h - 13.1 * mm, lw + 2.0 * mm, lh + 1.6 * mm, 1.5 * mm, stroke=0, fill=1)
            canvas.drawImage(LOGO_PATH, 14.5 * mm, h - 12.3 * mm, width=lw, height=lh, mask="auto", preserveAspectRatio=True)

        canvas.setFillColor(C_WHITE)
        canvas.setFont(FONT_BOLD, 8.6)
        canvas.drawString(28 * mm, h - 7.2 * mm, "FEDERACIÓN COLOMBIANA DE MOTOCICLISMO — COMISIÓN DE JUZGAMIENTO")
        canvas.setFont(FONT_REG, 7.4)
        canvas.setFillColor(colors.HexColor("#DBEAFE"))
        canvas.drawString(28 * mm, h - 11.5 * mm, "Informe Ejecutivo de Participación y Rendimiento Deportivo · Marca BAJAJ — GP Colombia 2026")

        canvas.setFillColor(C_GOLD)
        canvas.setFont(FONT_BOLD, 8.0)
        canvas.drawRightString(w - 14 * mm, h - 9.5 * mm, "GP COLOMBIA 2026")

    # Running footer on every page
    canvas.setStrokeColor(C_SLATE_200)
    canvas.setLineWidth(0.6)
    canvas.line(14 * mm, 12.5 * mm, w - 14 * mm, 12.5 * mm)

    canvas.setFillColor(C_SLATE_500)
    canvas.setFont(FONT_REG, 7.1)
    canvas.drawString(
        14 * mm,
        8.2 * mm,
        "FEDEMOTO · Mauricio Sánchez Aguilar — Jefe de Cronometraje (Comisión de Juzgamiento) · cronometraje@fedemoto.org",
    )
    canvas.setFont(FONT_BOLD, 7.4)
    canvas.setFillColor(C_NAVY)
    canvas.drawRightString(w - 14 * mm, 8.2 * mm, f"Página {page_num}")
    canvas.restoreState()


def build_pdf():
    dataset = collect_bajaj_dataset()
    parts = dataset["participations"]
    cats = dataset["categories"]
    macro = dataset["gp_macro"]
    st = get_styles()

    # Global aggregates across the 5 categories
    tot_parts = len(parts)
    bajaj_parts = sum(1 for p in parts if p["moto"] == "Bajaj")
    known_parts = sum(1 for p in parts if p["moto"] not in ("", "Sin Registro"))
    open_parts = [p for p in parts if p["categoria"] != "Pulsar NS 200 FI"]
    open_bajaj = sum(1 for p in open_parts if p["moto"] == "Bajaj")

    u_riders = set(p["rk"] for p in parts)
    u_bajaj_riders = set(p["rk"] for p in parts if p["moto"] == "Bajaj")
    event_riders = set(p["rk"] for p in parts if p["es_evento"])
    event_bajaj_riders = set(p["rk"] for p in parts if p["es_evento"] and p["moto"] == "Bajaj")

    # Multi-category Bajaj riders
    rider_bajaj_cats = defaultdict(set)
    rider_names = {}
    rider_ligas = {}
    for p in parts:
        rider_names[p["rk"]] = p["nombre"]
        if p["liga"]:
            rider_ligas[p["rk"]] = p["liga"]
        if p["moto"] == "Bajaj":
            rider_bajaj_cats[p["rk"]].add(p["categoria"])
    multicat_bajaj = [rk for rk, cs in rider_bajaj_cats.items() if len(cs) >= 2]

    # Sporting counts
    bajaj_wins = bajaj_podiums = total_races = 0
    bajaj_poles = total_poles = 0
    bajaj_fl = total_fl = 0
    tot_race_starts = tot_race_fin = 0
    tot_bajaj_starts = tot_bajaj_fin = 0

    for tc in TARGET_CATS:
        for vd in cats[tc]["validas"]:
            total_races += 1
            tot_race_starts += vd["grilla_carrera"]
            tot_race_fin += vd["finalizados"]
            tot_bajaj_starts += vd["bajaj_carrera"]
            tot_bajaj_fin += vd["bajaj_finalizados"]
            pm = [x["moto"] for x in vd["podio"]]
            if pm and pm[0] == "Bajaj":
                bajaj_wins += 1
            bajaj_podiums += sum(1 for m in pm if m == "Bajaj")
            if vd["pole"]:
                total_poles += 1
                if vd["pole"]["moto"] == "Bajaj":
                    bajaj_poles += 1
            if vd["mejor_vuelta_carrera"]:
                total_fl += 1
                if vd["mejor_vuelta_carrera"]["moto"] == "Bajaj":
                    bajaj_fl += 1

    story = []

    # =========================================================================
    # PÁGINA 1: PORTADA EJECUTIVA + KPIS + TABLA SÍNTESIS + HALLAZGOS CLAVE
    # =========================================================================
    logo_cell = ""
    if os.path.isfile(LOGO_PATH):
        with PILImage.open(LOGO_PATH) as im:
            aspect = im.size[0] / float(im.size[1])
        lh = 18.5 * mm
        logo_img = Image(LOGO_PATH, width=lh * aspect, height=lh)
        logo_badge = Table([[logo_img]], colWidths=[21.5 * mm], rowHeights=[21.5 * mm])
        logo_badge.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), C_WHITE),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("LEFTPADDING", (0, 0), (-1, -1), 1 * mm),
            ("RIGHTPADDING", (0, 0), (-1, -1), 1 * mm),
            ("TOPPADDING", (0, 0), (-1, -1), 1 * mm),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 1 * mm),
        ]))
        logo_cell = logo_badge

    st_cov_sup = ParagraphStyle("csup", fontName=FONT_BOLD, fontSize=8.3, leading=10.5, textColor=C_GOLD)
    st_cov_tit = ParagraphStyle("ctit", fontName=FONT_BOLD, fontSize=15.5, leading=18.5, textColor=C_WHITE)
    st_cov_sub = ParagraphStyle("csub", fontName=FONT_REG, fontSize=8.8, leading=11.5, textColor=colors.HexColor("#E2E8F0"))

    hero_right = [
        Paragraph("FEDERACIÓN COLOMBIANA DE MOTOCICLISMO · COMISIÓN DE JUZGAMIENTO", st_cov_sup),
        Spacer(1, 1 * mm),
        Paragraph("INFORME EJECUTIVO PARA LA MARCA BAJAJ — GP COLOMBIA 2026", st_cov_tit),
        Spacer(1, 1.2 * mm),
        Paragraph(
            "Análisis integral de participaciones, cuota de parque automotor, desempeño competitivo, fiabilidad y alcance territorial en las categorías <b>Pulsar NS 200 FI, 220cc 4T, Street Race 250, CRS Novatos y CRS Expertos</b> (I, II y III Válida Final — Autódromo de Tocancipá).",
            st_cov_sub,
        ),
    ]
    hero_tbl = Table([[logo_cell, hero_right]], colWidths=[26 * mm, 156 * mm])
    hero_tbl.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), C_NAVY_DARK),
        ("LINEBELOW", (0, 0), (-1, -1), 3.0, C_GOLD),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("ALIGN", (0, 0), (0, 0), "CENTER"),
        ("LEFTPADDING", (0, 0), (-1, -1), 3.5 * mm),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4.0 * mm),
        ("TOPPADDING", (0, 0), (-1, -1), 4.2 * mm),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4.2 * mm),
    ]))
    story.append(hero_tbl)
    story.append(Spacer(1, 3.2 * mm))

    # Metadata bar
    meta_st = ParagraphStyle("mst", fontName=FONT_REG, fontSize=7.6, leading=9.5, textColor=C_SLATE_700)
    meta_tbl = Table([[
        Paragraph("<b>Destinatario:</b> Marca BAJAJ Colombia", meta_st),
        Paragraph("<b>Escenario:</b> Autódromo de Tocancipá (3 Válidas)", meta_st),
        Paragraph("<b>Estado Campeonato:</b> Finalizado Oficial 2026", meta_st),
    ]], colWidths=[58 * mm, 64 * mm, 60 * mm])
    meta_tbl.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), C_SLATE_100),
        ("BOX", (0, 0), (-1, -1), 0.6, C_SLATE_200),
        ("TOPPADDING", (0, 0), (-1, -1), 1.6 * mm),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 1.6 * mm),
        ("LEFTPADDING", (0, 0), (-1, -1), 2.5 * mm),
    ]))
    story.append(meta_tbl)
    story.append(Spacer(1, 3.2 * mm))

    # 8 Hero KPI Cards
    ligas_5cat = set(p["liga"] for p in parts if p["liga"])
    ligas_bajaj = set(p["liga"] for p in parts if p["liga"] and p["moto"] == "Bajaj")
    clubs_5cat = set(p["club"] for p in parts if p["club"])

    bajaj_silvers = sum(1 for tc in TARGET_CATS for v in cats[tc]["validas"] for x in v["podio"] if x["pos"] == 2 and x["moto"] == "Bajaj")
    bajaj_bronzes = sum(1 for tc in TARGET_CATS for v in cats[tc]["validas"] for x in v["podio"] if x["pos"] == 3 and x["moto"] == "Bajaj")

    kpi_cards = [
        (f"{bajaj_parts} / {tot_parts}", "PARTICIPACIONES BAJAJ", f"{fmt_pct(bajaj_parts / tot_parts * 100)} del bloque ({fmt_pct(bajaj_parts / known_parts * 100)} marcas reg.)"),
        (f"{len(u_bajaj_riders)} / {len(u_riders)}", "PILOTOS ÚNICOS BAJAJ", f"{fmt_pct(len(u_bajaj_riders) / len(u_riders) * 100)} de los pilotos de las 5 categorías"),
        (fmt_pct(tot_parts / macro["participaciones_totales_gp"] * 100), "PESO EN GP COLOMBIA", f"{tot_parts} de {macro['participaciones_totales_gp']} participaciones totales GP"),
        ("3 de 5", "TÍTULOS NACIONALES 2026", "Pulsar NS 200 FI · 220cc 4T · CRS Novatos"),
        (f"{bajaj_podiums} / {total_races * 3}", f"PODIOS DE VÁLIDA ({fmt_pct(bajaj_podiums / (total_races * 3) * 100)})", f"{bajaj_wins} victorias ({int(round(bajaj_wins / total_races * 100))}%), {bajaj_silvers} platas y {bajaj_bronzes} bronces"),
        (f"{bajaj_poles} / {total_poles}", f"POLE POSITIONS ({fmt_pct(bajaj_poles / total_poles * 100)})", "Clasificatorias oficiales lideradas por Bajaj"),
        (f"{bajaj_fl} / {total_fl}", f"VUELTAS RÁPIDAS ({fmt_pct(bajaj_fl / total_fl * 100)})", "Récords válidos de vuelta en carrera sobre Bajaj"),
        (f"{len(ligas_bajaj)} Ligas", "ALCANCE TERRITORIAL", f"Presente en {len(ligas_bajaj)}/{len(ligas_5cat)} deptos. y {len(clubs_5cat)} clubes"),
    ]
    story.append(make_kpi_grid(kpi_cards, cols=4))
    story.append(Spacer(1, 3.8 * mm))

    # Tabla resumen ejecutivo de las 5 categorías
    story.append(Paragraph("1. Resumen Consolidado de las 5 Categorías Objetivo (Temporada Completa GP Colombia 2026)", st["h2_sub"]))

    sum_rows = [[
        Paragraph("Categoría", st["th_l"]),
        Paragraph("Part.<br/>Totales", st["th"]),
        Paragraph("Pilotos<br/>Únicos", st["th"]),
        Paragraph("Part.<br/>Bajaj", st["th"]),
        Paragraph("Cuota<br/>Bajaj", st["th"]),
        Paragraph("Victorias<br/>Bajaj", st["th"]),
        Paragraph("Podios<br/>Bajaj", st["th"]),
        Paragraph("Efectiv.<br/>Bajaj", st["th"]),
        Paragraph("Campeón Nacional 2026 (Marca)", st["th_l"]),
    ]]
    for tc in TARGET_CATS:
        cp = [p for p in parts if p["categoria"] == tc]
        cu = set(p["rk"] for p in cp)
        cb = sum(1 for p in cp if p["moto"] == "Bajaj")
        vds = cats[tc]["validas"]
        wins_c = sum(1 for v in vds if v["podio"] and v["podio"][0]["moto"] == "Bajaj")
        pods_c = sum(sum(1 for x in v["podio"] if x["moto"] == "Bajaj") for v in vds)
        bs = sum(v["bajaj_carrera"] for v in vds)
        bf = sum(v["bajaj_finalizados"] for v in vds)
        beff = (bf / bs * 100) if bs else 0.0
        champ_row = cats[tc]["general_standings"][0]
        champ_str = f"#{champ_row['numero']} {champ_row['nombre']} ({champ_row['moto']})"
        sum_rows.append([
            Paragraph(tc, st["td_lb"]),
            Paragraph(str(len(cp)), st["td_b"]),
            Paragraph(str(len(cu)), st["td"]),
            Paragraph(str(cb), st["td_b"]),
            Paragraph(fmt_pct(cb / len(cp) * 100), st["td_b"]),
            Paragraph(f"{wins_c} / 3", st["td"]),
            Paragraph(f"{pods_c} / 9", st["td_b"]),
            Paragraph(fmt_pct(beff), st["td"]),
            Paragraph(champ_str, st["td_l"]),
        ])

    # Fila Total
    tot_beff = (tot_bajaj_fin / tot_bajaj_starts * 100) if tot_bajaj_starts else 0.0
    sum_rows.append([
        Paragraph("TOTAL CONSOLIDADO (5 CATEGORÍAS)", st["td_lb"]),
        Paragraph(str(tot_parts), st["td_b"]),
        Paragraph(str(len(u_riders)), st["td_b"]),
        Paragraph(str(bajaj_parts), st["td_b"]),
        Paragraph(fmt_pct(bajaj_parts / tot_parts * 100), st["td_b"]),
        Paragraph(f"{bajaj_wins} / 15", st["td_b"]),
        Paragraph(f"{bajaj_podiums} / 45", st["td_b"]),
        Paragraph(fmt_pct(tot_beff), st["td_b"]),
        Paragraph("3 Campeonatos Nacionales Bajaj (60%)", st["td_lb"]),
    ])

    sum_tbl = Table(
        sum_rows,
        colWidths=[31 * mm, 13 * mm, 13 * mm, 13 * mm, 15 * mm, 15 * mm, 14 * mm, 15 * mm, 53 * mm],
    )
    sum_style = standard_table_style(len(sum_rows), gold_top_rows=[len(sum_rows) - 1])
    sum_style.add("LINEABOVE", (0, len(sum_rows) - 1), (-1, len(sum_rows) - 1), 1.2, C_NAVY)
    sum_tbl.setStyle(sum_style)
    story.append(sum_tbl)
    story.append(Spacer(1, 3.2 * mm))

    # Hallazgos ejecutivos para Bajaj
    story.append(Paragraph("2. Conclusiones Estratégicas de Valor para la Marca BAJAJ", st["h2_sub"]))
    insights = [
        f"<b>1. Liderazgo hegemónico en categorías abiertas multimarca:</b> Excluyendo la copa monomarca <i>Pulsar NS 200 FI</i> (100% Bajaj), en las 4 categorías multimarca abiertas (<i>CRS Novatos, CRS Expertos, Street Race 250 y 220cc 4T</i>) Bajaj registró <b>{open_bajaj} de {len(open_parts)} participaciones ({fmt_pct(open_bajaj / len(open_parts) * 100)})</b>, superando de forma conjunta a otras 12 marcas presentes en grilla.",
        f"<b>2. Columna vertebral del Campeonato Nacional GP Colombia:</b> Estas 5 categorías aportan el <b>26,6% de todas las participaciones</b> del GP Colombia (579 de {macro['participaciones_totales_gp']}) y congregan al <b>32,4% de todos los pilotos únicos</b> del certamen (186 de {macro['pilotos_unicos_gp']}). En total, <b>1 de cada 4 pilotos inscritos en todo GP Colombia compite en una moto Bajaj</b> dentro de este bloque.",
        "<b>3. Paridad mecánica y espectáculo deportivo en pista:</b> La Copa <i>Pulsar NS 200 FI</i> definió su título nacional por apenas <b>1 punto</b> (45 vs. 44 vs. 43 pts) y registró llegadas a meta separadas por <b>0,009 s</b> (Válida II), <b>0,094 s</b> (Válida I) y <b>0,114 s</b> (Válida III). En <i>CRS Novatos</i> (Válida III), el triunfo de Bajaj se decidió en foto-finish por <b>0,001 segundos (una milésima)</b>.",
        "<b>4. Semillero nacional, inclusión femenina y escalera deportiva:</b> En <i>CRS Novatos</i>, la piloto <b>Daniela Triana Gil (#290)</b> se coronó Campeona Nacional absoluta sobre Bajaj ante 64 rivales, encabezando una <b>barrida histórica de los 7 primeros puestos de la general para Bajaj</b>. Además, <b>34 pilotos</b> utilizaron plataformas Bajaj para competir simultáneamente en 2 o más categorías del bloque.",
    ]
    for ins in insights:
        story.append(Paragraph(f"• {ins}", st["bullet"]))

    story.append(PageBreak())

    # =========================================================================
    # PÁGINA 2: INTELIGENCIA DE MARCA (SHARE OEM), EVOLUCIÓN Y FIABILIDAD
    # =========================================================================
    story.append(section_banner(
        "INTELIGENCIA COMPETITIVA DE MARCA Y RENDIMIENTO EN PISTA",
        "Cuota OEM, evolución por válida y escalera deportiva",
    ))
    story.append(Spacer(1, 2.5 * mm))
    story.append(build_chart_brand_and_evolution(dataset))
    story.append(Spacer(1, 2.2 * mm))

    story.append(Paragraph("Comparativa Oficial de Marcas (OEM) en las 5 Categorías Analizadas", st["h2_sub"]))

    # Compute OEM table across the 5 categories
    brand_parts = Counter(p["moto"] for p in parts)
    brand_uids = defaultdict(set)
    for p in parts:
        brand_uids[p["moto"]].add(p["rk"])

    brand_wins = Counter()
    brand_pods = Counter()
    for tc in TARGET_CATS:
        for vd in cats[tc]["validas"]:
            for pr in vd["podio"]:
                brand_pods[pr["moto"]] += 1
                if pr["pos"] == 1:
                    brand_wins[pr["moto"]] += 1

    brand_top10 = Counter()
    brand_titles = Counter()
    for tc in TARGET_CATS:
        gs = cats[tc]["general_standings"]
        if gs:
            brand_titles[gs[0]["moto"]] += 1
        for r in gs[:10]:
            brand_top10[r["moto"]] += 1

    oem_rows = [[
        Paragraph("Marca", st["th_l"]),
        Paragraph("Participaciones", st["th"]),
        Paragraph("Cuota Global", st["th"]),
        Paragraph("Pilotos Únicos", st["th"]),
        Paragraph("Victorias Válida", st["th"]),
        Paragraph("Podios Válida", st["th"]),
        Paragraph("Cupos Top 10 Gen.", st["th"]),
        Paragraph("Títulos 2026", st["th"]),
    ]]

    ordered_brands = [b for b, _ in brand_parts.most_common() if b != "Sin Registro"]
    if brand_parts.get("Sin Registro"):
        ordered_brands.append("Sin Registro")

    for b in ordered_brands[:10]:
        cnt = brand_parts[b]
        oem_rows.append([
            Paragraph(b, st["td_lb"] if b == "Bajaj" else st["td_l"]),
            Paragraph(str(cnt), st["td_b"] if b == "Bajaj" else st["td"]),
            Paragraph(fmt_pct(cnt / tot_parts * 100), st["td_b"] if b == "Bajaj" else st["td"]),
            Paragraph(str(len(brand_uids[b])), st["td"]),
            Paragraph(str(brand_wins[b]), st["td_b"] if brand_wins[b] else st["td"]),
            Paragraph(str(brand_pods[b]), st["td_b"] if brand_pods[b] else st["td"]),
            Paragraph(f"{brand_top10[b]} / 50", st["td_b"] if b == "Bajaj" else st["td"]),
            Paragraph(str(brand_titles[b]), st["td_b"] if brand_titles[b] else st["td"]),
        ])

    rest_brands = ordered_brands[10:]
    if rest_brands:
        rcnt = sum(brand_parts[b] for b in rest_brands)
        ruids = set().union(*(brand_uids[b] for b in rest_brands))
        oem_rows.append([
            Paragraph(f"Otras ({len(rest_brands)} marcas: {', '.join(rest_brands)})", st["td_l"]),
            Paragraph(str(rcnt), st["td"]),
            Paragraph(fmt_pct(rcnt / tot_parts * 100), st["td"]),
            Paragraph(str(len(ruids)), st["td"]),
            Paragraph(str(sum(brand_wins[b] for b in rest_brands)), st["td"]),
            Paragraph(str(sum(brand_pods[b] for b in rest_brands)), st["td"]),
            Paragraph(f"{sum(brand_top10[b] for b in rest_brands)} / 50", st["td"]),
            Paragraph(str(sum(brand_titles[b] for b in rest_brands)), st["td"]),
        ])

    oem_tbl = Table(oem_rows, colWidths=[41 * mm, 24 * mm, 20 * mm, 20 * mm, 21 * mm, 19 * mm, 21 * mm, 16 * mm])
    oem_tbl.setStyle(standard_table_style(len(oem_rows), highlight_bajaj_rows=[1]))
    story.append(oem_tbl)
    story.append(Spacer(1, 3.0 * mm))

    # Desglose por Válida + Escalera Deportiva Bajaj
    story.append(Paragraph("Comportamiento por Válida y Escalera de Progresión de Pilotos Bajaj", st["h2_sub"]))
    val_summary_rows = [[
        Paragraph("Válida Oficial GP Colombia 2026", st["th_l"]),
        Paragraph("Trazado Tocancipá", st["th"]),
        Paragraph("Inscritos (5 Cat.)", st["th"]),
        Paragraph("Motos Bajaj", st["th"]),
        Paragraph("Cuota Bajaj", st["th"]),
        Paragraph("Largadas Bajaj", st["th"]),
        Paragraph("Finalizados Bajaj", st["th"]),
        Paragraph("Podios Bajaj", st["th"]),
    ]]
    for vc, vname, circ in [
        ("I", "I Válida — Gran Premio Vitrix", "Largo (2.725 m)"),
        ("II", "II Válida — Gran Premio BMW", "Corto-Medio"),
        ("III", "III Válida Final — Gran Premio IRC", "Largo (2.725 m)"),
    ]:
        vp = [p for p in parts if p["valida"] == vc]
        vb = sum(1 for p in vp if p["moto"] == "Bajaj")
        bs = sum(cats[tc]["validas"][idx]["bajaj_carrera"] for tc in TARGET_CATS for idx, vv in enumerate(cats[tc]["validas"]) if vv["valida"] == vc)
        bf = sum(cats[tc]["validas"][idx]["bajaj_finalizados"] for tc in TARGET_CATS for idx, vv in enumerate(cats[tc]["validas"]) if vv["valida"] == vc)
        bpod = sum(sum(1 for x in vv["podio"] if x["moto"] == "Bajaj") for tc in TARGET_CATS for vv in cats[tc]["validas"] if vv["valida"] == vc)
        val_summary_rows.append([
            Paragraph(vname, st["td_lb"]),
            Paragraph(circ, st["td"]),
            Paragraph(str(len(vp)), st["td_b"]),
            Paragraph(str(vb), st["td_b"]),
            Paragraph(fmt_pct(vb / len(vp) * 100), st["td_b"]),
            Paragraph(str(bs), st["td"]),
            Paragraph(f"{bf} ({fmt_pct(bf / bs * 100 if bs else 0)})", st["td"]),
            Paragraph(f"{bpod} / 15", st["td_b"]),
        ])

    val_tbl = Table(val_summary_rows, colWidths=[48 * mm, 26 * mm, 20 * mm, 18 * mm, 18 * mm, 17 * mm, 20 * mm, 15 * mm])
    val_tbl.setStyle(standard_table_style(len(val_summary_rows)))
    story.append(val_tbl)
    story.append(Spacer(1, 2.5 * mm))

    # Highlight box: Escalera deportiva y captación de nuevos talentos
    three_cat_riders = [
        f"{rider_names[rk]} ({rider_ligas.get(rk, '—')})"
        for rk, cs in sorted(rider_bajaj_cats.items(), key=lambda x: (-len(x[1]), rider_names[x[0]]))
        if len(cs) >= 3
    ]
    ladder_text = (
        f"<b>Fidelidad de Plataforma y Captación de Nuevos Pilotos:</b> De los <b>143 pilotos únicos de Bajaj</b> en estas categorías, "
        f"<b>{len(multicat_bajaj)} pilotos ({fmt_pct(len(multicat_bajaj)/len(u_bajaj_riders)*100)})</b> compitieron en 2 o más categorías del bloque "
        f"(combinando <i>CRS, 220cc 4T y Street Race 250</i>), incluyendo <b>{len(three_cat_riders)} pilotos en 3 categorías con Bajaj</b> "
        f"({', '.join(three_cat_riders[:6])}). Adicionalmente, de los <b>{len(event_riders)} pilotos con Licencia por Evento (-E)</b> "
        f"(nuevos talentos que debutan en pista), <b>{len(event_bajaj_riders)} ({fmt_pct(len(event_bajaj_riders)/len(event_riders)*100 if event_riders else 0)}) eligieron una motocicleta Bajaj</b> como su moto de iniciación deportiva."
    )
    box_tbl = Table([[Paragraph(ladder_text, st["body"])]], colWidths=[182 * mm])
    box_tbl.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), C_GOLD_SOFT),
        ("BOX", (0, 0), (-1, -1), 0.8, C_GOLD_BORDER),
        ("LEFTPADDING", (0, 0), (-1, -1), 3.2 * mm),
        ("RIGHTPADDING", (0, 0), (-1, -1), 3.2 * mm),
        ("TOPPADDING", (0, 0), (-1, -1), 2.2 * mm),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 1.5 * mm),
    ]))
    story.append(box_tbl)

    story.append(PageBreak())

    # =========================================================================
    # PÁGINA 3: ALCANCE TERRITORIAL (LIGAS DEPARTAMENTALES Y CLUBES DEPORTIVOS)
    # =========================================================================
    story.append(section_banner(
        "ALCANCE TERRITORIAL: LIGAS DEPARTAMENTALES Y ECOSISTEMA DE CLUBES",
        "Impacto regional y escuelas aliadas con presencia Bajaj",
    ))
    story.append(Spacer(1, 2.5 * mm))
    story.append(build_chart_territorial(dataset))
    story.append(Spacer(1, 2.0 * mm))

    # Ligas Table (15 departments)
    liga_u = defaultdict(set)
    liga_bu = defaultdict(set)
    liga_p = Counter()
    liga_bp = Counter()
    liga_pods_bajaj = Counter()

    for p in parts:
        if p["liga"]:
            liga_u[p["liga"]].add(p["rk"])
            liga_p[p["liga"]] += 1
            if p["moto"] == "Bajaj":
                liga_bu[p["liga"]].add(p["rk"])
                liga_bp[p["liga"]] += 1

    for tc in TARGET_CATS:
        for vd in cats[tc]["validas"]:
            for pr in vd["podio"]:
                if pr["moto"] == "Bajaj" and pr["liga"] and pr["liga"] != "—":
                    liga_pods_bajaj[pr["liga"]] += 1

    story.append(Paragraph("Participación Oficial por Liga Departamental en las 5 Categorías", st["h2_sub"]))
    liga_rows = [[
        Paragraph("Liga Departamental", st["th_l"]),
        Paragraph("Pilotos Únicos", st["th"]),
        Paragraph("Pilotos Bajaj", st["th"]),
        Paragraph("% Adopción Bajaj", st["th"]),
        Paragraph("Part. Totales", st["th"]),
        Paragraph("Part. Bajaj", st["th"]),
        Paragraph("Podios Bajaj (Válidas)", st["th"]),
    ]]
    for l_name, us in sorted(liga_u.items(), key=lambda x: (-len(liga_bu[x[0]]), -len(x[1]), x[0])):
        bu_cnt = len(liga_bu[l_name])
        u_cnt = len(us)
        liga_rows.append([
            Paragraph(l_name, st["td_lb"] if bu_cnt >= 10 else st["td_l"]),
            Paragraph(str(u_cnt), st["td"]),
            Paragraph(str(bu_cnt), st["td_b"] if bu_cnt else st["td"]),
            Paragraph(fmt_pct(bu_cnt / u_cnt * 100), st["td_b"] if bu_cnt / u_cnt >= 0.75 else st["td"]),
            Paragraph(str(liga_p[l_name]), st["td"]),
            Paragraph(str(liga_bp[l_name]), st["td_b"] if liga_bp[l_name] else st["td"]),
            Paragraph(str(liga_pods_bajaj[l_name]) if liga_pods_bajaj[l_name] else "—", st["td_b"] if liga_pods_bajaj[l_name] else st["td"]),
        ])

    liga_tbl = Table(liga_rows, colWidths=[42 * mm, 22 * mm, 22 * mm, 25 * mm, 22 * mm, 22 * mm, 27 * mm])
    liga_tbl.setStyle(standard_table_style(len(liga_rows), highlight_bajaj_rows=[1, 2, 3], compact=True))
    story.append(liga_tbl)
    story.append(Spacer(1, 2.0 * mm))

    # Top 9 Clubs Table
    club_u = defaultdict(set)
    club_bu = defaultdict(set)
    club_bp = Counter()
    club_ligas_map = defaultdict(set)
    for p in parts:
        if p["club"]:
            club_u[p["club"]].add(p["rk"])
            if p["liga"]:
                club_ligas_map[p["club"]].add(p["liga"])
            if p["moto"] == "Bajaj":
                club_bu[p["club"]].add(p["rk"])
                club_bp[p["club"]] += 1

    story.append(Paragraph("Principales Clubes y Escuelas Deportivas con Mayor Actividad Bajaj", st["h2_sub"]))
    club_rows = [[
        Paragraph("Club Deportivo / Escuela", st["th_l"]),
        Paragraph("Liga Principal", st["th_l"]),
        Paragraph("Pilotos Club", st["th"]),
        Paragraph("Pilotos Bajaj", st["th"]),
        Paragraph("% Flota Bajaj", st["th"]),
        Paragraph("Participaciones Bajaj", st["th"]),
    ]]
    top_clubs_sorted = sorted(club_u.items(), key=lambda x: (-len(club_bu[x[0]]), -club_bp[x[0]], x[0]))[:9]
    for cname, cus in top_clubs_sorted:
        bu = len(club_bu[cname])
        cu = len(cus)
        cligas = ", ".join(sorted(club_ligas_map[cname])[:2]) or "—"
        club_rows.append([
            Paragraph(cname, st["td_lb"] if bu >= 10 else st["td_l"]),
            Paragraph(cligas, st["td_l"]),
            Paragraph(str(cu), st["td"]),
            Paragraph(str(bu), st["td_b"]),
            Paragraph(fmt_pct(bu / cu * 100), st["td_b"]),
            Paragraph(str(club_bp[cname]), st["td_b"]),
        ])

    club_tbl = Table(club_rows, colWidths=[58 * mm, 36 * mm, 20 * mm, 21 * mm, 22 * mm, 25 * mm])
    club_tbl.setStyle(standard_table_style(len(club_rows), compact=True))
    story.append(club_tbl)
    story.append(Paragraph(
        "Nota: Los pilotos de la Copa Monomarca Pulsar NS 200 FI compiten bajo formato promocional de copa de marca sin registro obligatorio de club/liga en planilla.",
        st["note"],
    ))

    # =========================================================================
    # PÁGINAS 4 A 8: FICHAS DETALLADAS POR CADA UNA DE LAS 5 CATEGORÍAS
    # =========================================================================
    cat_descriptions = {
        "Pulsar NS 200 FI": (
            "COPA PULSAR NS 200 FI — MONOMARCA OFICIAL BAJAJ",
            "Copa promocional 100% Bajaj: paridad mecánica total y formación competitiva",
            "La copa monomarca Pulsar NS 200 FI mantuvo una grilla constante de 10 pilotos en las 3 válidas (30 participaciones y 13 pilotos únicos en el año), alcanzando un 90,0% de efectividad mecánica en carrera y protagonizando las definiciones más cerradas del campeonato: 0,094 s en Válida I, 0,009 s en Válida II y 0,114 s en la Válida Final, con el Top 3 del campeonato separado por apenas 2 puntos (45, 44 y 43 pts).",
        ),
        "220cc 4T": (
            "CATEGORÍA 220cc 4T — CAMPEÓN Y SUBCAMPEÓN NACIONAL BAJAJ",
            "Categoría abierta multimarca con 69,8% de dominio de parque automotor Bajaj",
            "Con 149 participaciones y 94 pilotos únicos (pico de 74 inscritos en la I Válida), 220cc 4T es una de las categorías estructurales del GP Colombia. Las motocicletas Bajaj sumaron 104 participaciones (69,8%), ganaron las Válidas I y II, obtuvieron 2 Pole Positions y conquistaron el 1° y 2° lugar del Campeonato Nacional con Andrés Felipe González (#314) y Christian David Chavarro (#417), ubicando 6 motos Bajaj en el Top 9 anual.",
        ),
        "Street Race 250": (
            "CATEGORÍA STREET RACE 250 — LIDERAZGO EN PARQUE AUTOMOTOR (75,0%)",
            "3 de cada 4 pilotos en grilla eligen plataforma Bajaj frente a 10 marcas rivales",
            "En la exigente cilindrada de cuarto de litro abierta a preparaciones multimarca (Unite Motor, Aprilia, Kawasaki, Honda, Yamaha, KTM), Bajaj fue por amplio margen la marca preferida por los pilotos colombianos con 96 de 128 participaciones (75,0% de la grilla). Logró podios oficiales en la I Válida (#367 Johon Farfán) y II Válida (#370 Cristian Cruz, a solo 0,142 s del triunfo), posicionando a 6 pilotos Bajaj dentro del Top 10 del Campeonato Nacional (puestos 5° al 10°).",
        ),
        "CRS Novatos": (
            "CATEGORÍA CRS NOVATOS — BARRIDA HISTÓRICA TOP 7 NACIONAL BAJAJ",
            "86,6% de cuota de marca, Campeona Nacional en Bajaj y definición al milésimo (0,001 s)",
            "Fue la categoría de mayor convocatoria del bloque con 179 participaciones y 98 pilotos únicos (82 inscritos en Válida I). Bajaj dominó con 155 participaciones (86,6%, subiendo al 91,2% en la Gran Final), barrió el podio 1°-2°-3° tanto en la II como en la III Válida (definida por 0,001 s a favor de Daniela Triana Gil #290) y firmó un hito inédito: los primeros 7 puestos de la Clasificación General Final 2026 fueron ocupados íntegramente por motocicletas Bajaj.",
        ),
        "CRS Expertos": (
            "CATEGORÍA CRS EXPERTOS — ÉLITE DE CRITERIUM CON 79,6% DE FLOTA BAJAJ",
            "Barrida 1°-2°-3° en Válida I, 2 victorias de válida y Bronce Nacional 2026",
            "En la máxima división del Criterium (93 participaciones y 53 pilotos únicos), Bajaj representó el 79,6% del parque automotor (74 participaciones) y alcanzó un 83,3% de efectividad mecánica. Bajaj protagonizó una barrida 1°-2°-3°-4° en la I Válida, repitió victoria y doble podio en la II Válida (definida por apenas 0,029 s) y cerró con podio en la Gran Final, asegurando el 3°, 4° y 5° puesto del Campeonato Nacional.",
        ),
    }

    for idx_cat, tc in enumerate(TARGET_CATS):
        story.append(PageBreak())
        banner_title, banner_sub, intro_p = cat_descriptions[tc]
        story.append(section_banner(banner_title, banner_sub))
        story.append(Spacer(1, 2.0 * mm))

        cp = [p for p in parts if p["categoria"] == tc]
        cu = set(p["rk"] for p in cp)
        cb = sum(1 for p in cp if p["moto"] == "Bajaj")
        vds = cats[tc]["validas"]
        gs = cats[tc]["general_standings"]

        wins_c = sum(1 for v in vds if v["podio"] and v["podio"][0]["moto"] == "Bajaj")
        pods_c = sum(sum(1 for x in v["podio"] if x["moto"] == "Bajaj") for v in vds)
        bs = sum(v["bajaj_carrera"] for v in vds)
        bf = sum(v["bajaj_finalizados"] for v in vds)
        b_top10 = sum(1 for r in gs[:10] if r["moto"] == "Bajaj")

        cat_kpis = [
            (f"{cb} / {len(cp)}", "PARTICIPACIONES BAJAJ", f"Cuota {fmt_pct(cb / len(cp) * 100)} ({len(cu)} pilotos únicos)"),
            (f"{pods_c} / 9", "PODIOS DE VÁLIDA BAJAJ", f"{wins_c} victorias de carrera sobre 3 válidas"),
            (fmt_pct(bf / bs * 100 if bs else 0), "FIABILIDAD EN CARRERA", f"{bf} finalizados de {bs} largadas Bajaj"),
            (f"{b_top10} / {min(10, len(gs))}", "BAJAJ EN TOP 10 GENERAL", f"{len(gs)} pilotos clasificados en el año"),
        ]
        story.append(make_kpi_grid(cat_kpis, cols=4))
        story.append(Spacer(1, 1.8 * mm))
        story.append(Paragraph(intro_p, st["body"]))

        # Tabla 1 de la categoría: Desempeño por Válida + Récords de Vuelta
        story.append(Paragraph("Desempeño por Válida, Pole Positions y Récords de Vuelta", st["h2_sub"]))
        v_rows = [[
            Paragraph("Válida (Trazado)", st["th_l"]),
            Paragraph("Inscr.<br/>Tot.", st["th"]),
            Paragraph("Motos<br/>Bajaj", st["th"]),
            Paragraph("Grilla /<br/>Finaliz.", st["th"]),
            Paragraph("Pole Position (Tiempo)", st["th_l"]),
            Paragraph("Vuelta Rápida Carrera", st["th_l"]),
            Paragraph("Margen<br/>1° a 2°", st["th"]),
        ]]
        for vd in vds:
            pole_txt = (
                f"#{vd['pole']['numero']} {vd['pole']['nombre']} ({vd['pole']['moto']}) · {vd['pole']['tiempo']}"
                if vd["pole"] else "Grilla directa / Sin Q"
            )
            fl = vd["mejor_vuelta_carrera"]
            fl_txt = f"#{fl['numero']} {fl['nombre']} ({fl['moto']}) · {fl['tiempo']}" if fl else "—"
            gap_txt = f"{vd['gap_1_2']} s" if vd["gap_1_2"] and "vuelta" not in vd["gap_1_2"].lower() else (vd["gap_1_2"] or "—")
            v_rows.append([
                Paragraph(f"<b>{vd['valida']}</b> · {vd['valida_short']}", st["td_l"]),
                Paragraph(str(vd["inscritos_totales"]), st["td"]),
                Paragraph(f"{vd['bajaj_inscritos']} ({fmt_pct(vd['bajaj_cuota_pct'])})", st["td_b"]),
                Paragraph(f"{vd['grilla_carrera']} / {vd['finalizados']}", st["td"]),
                Paragraph(pole_txt, st["td_l"]),
                Paragraph(fl_txt, st["td_l"]),
                Paragraph(gap_txt, st["td_b"]),
            ])

        vtbl = Table(v_rows, colWidths=[33 * mm, 12 * mm, 21 * mm, 15 * mm, 43 * mm, 43 * mm, 15 * mm])
        vtbl.setStyle(standard_table_style(len(v_rows), compact=True))
        story.append(vtbl)
        story.append(Spacer(1, 1.5 * mm))

        # Tabla 2 de la categoría: Podios Oficiales de las 3 Válidas (9 filas compactas)
        story.append(Paragraph("Podios Oficiales de Carrera — Válidas I, II y III", st["h2_sub"]))
        pod_rows = [[
            Paragraph("Válida", st["th"]),
            Paragraph("Pos.", st["th"]),
            Paragraph("N°", st["th"]),
            Paragraph("Piloto", st["th_l"]),
            Paragraph("Liga", st["th_l"]),
            Paragraph("Marca", st["th"]),
            Paragraph("Mejor Vuelta", st["th"]),
            Paragraph("Dif. 1°", st["th"]),
        ]]
        bajaj_pod_indices = []
        r_cursor = 1
        for vd in vds:
            for pr in vd["podio"]:
                if pr["moto"] == "Bajaj":
                    bajaj_pod_indices.append(r_cursor)
                pod_rows.append([
                    Paragraph(f"Válida {vd['valida']}", st["td_b"] if pr["pos"] == 1 else st["td"]),
                    Paragraph(f"{pr['pos']}°", st["td_b"]),
                    Paragraph(str(pr["numero"]), st["td"]),
                    Paragraph(pr["nombre"], st["td_lb"] if pr["moto"] == "Bajaj" else st["td_l"]),
                    Paragraph(pr["liga"], st["td_l"]),
                    Paragraph(pr["moto"], st["td_b"] if pr["moto"] == "Bajaj" else st["td"]),
                    Paragraph(pr["mejor_tm"], st["td"]),
                    Paragraph(pr["dif"], st["td"]),
                ])
                r_cursor += 1

        ptbl = Table(pod_rows, colWidths=[16 * mm, 11 * mm, 12 * mm, 56 * mm, 29 * mm, 20 * mm, 20 * mm, 18 * mm])
        ptbl.setStyle(standard_table_style(len(pod_rows), highlight_bajaj_rows=bajaj_pod_indices, compact=True))
        story.append(ptbl)
        story.append(Spacer(1, 1.5 * mm))

        # Tabla 3 de la categoría: Clasificación General Final 2026
        max_gen_rows = 13 if tc == "Pulsar NS 200 FI" else (8 if idx_cat == len(TARGET_CATS) - 1 else 10)
        gen_subset = gs[:max_gen_rows]
        gen_title = (
            f"Clasificación General Final 2026 — Totalidad de Clasificados ({len(gs)} Pilotos)"
            if len(gen_subset) == len(gs)
            else f"Clasificación General Final 2026 — Top {len(gen_subset)} Oficial (de {len(gs)} pilotos clasificados)"
        )
        story.append(Paragraph(gen_title, st["h2_sub"]))

        g_rows = [[
            Paragraph("Pos.", st["th"]),
            Paragraph("N°", st["th"]),
            Paragraph("Piloto", st["th_l"]),
            Paragraph("Liga", st["th_l"]),
            Paragraph("Club Deportivo", st["th_l"]),
            Paragraph("Marca", st["th"]),
            Paragraph("I", st["th"]),
            Paragraph("II", st["th"]),
            Paragraph("III", st["th"]),
            Paragraph("Bono", st["th"]),
            Paragraph("Total", st["th"]),
        ]]
        bajaj_gen_rows = []
        gold_gen_rows = []
        for r_i, gr in enumerate(gen_subset, 1):
            if gr["pos"] == 1:
                gold_gen_rows.append(r_i)
            elif gr["moto"] == "Bajaj":
                bajaj_gen_rows.append(r_i)
            g_rows.append([
                Paragraph(f"{gr['pos']}°", st["td_b"]),
                Paragraph(str(gr["numero"]), st["td"]),
                Paragraph(gr["nombre"], st["td_lb"] if gr["moto"] == "Bajaj" else st["td_l"]),
                Paragraph(gr["liga"], st["td_l"]),
                Paragraph(gr["club"][:25] + ("…" if len(gr["club"]) > 25 else ""), st["td_l"]),
                Paragraph(gr["moto"], st["td_b"] if gr["moto"] == "Bajaj" else st["td"]),
                Paragraph(fmt_pts(gr["v1"]), st["td"]),
                Paragraph(fmt_pts(gr["v2"]), st["td"]),
                Paragraph(fmt_pts(gr["v3"]), st["td"]),
                Paragraph(f"+{fmt_pts(gr['bono'])}" if gr["bono"] else "—", st["td"]),
                Paragraph(fmt_pts(gr["total"]), st["td_b"]),
            ])

        gtbl = Table(
            g_rows,
            colWidths=[10 * mm, 11 * mm, 41 * mm, 22 * mm, 35 * mm, 16 * mm, 8 * mm, 8 * mm, 8 * mm, 11 * mm, 12 * mm],
        )
        gtbl.setStyle(standard_table_style(len(g_rows), highlight_bajaj_rows=bajaj_gen_rows, gold_top_rows=gold_gen_rows, compact=True))
        story.append(gtbl)

        # Bloque de certificación y firma en la última página
        if idx_cat == len(TARGET_CATS) - 1:
            story.append(Spacer(1, 2.2 * mm))
            sig_p = ParagraphStyle("sigp", fontName=FONT_REG, fontSize=7.5, leading=9.8, textColor=C_SLATE_700, alignment=TA_CENTER)
            sig_b = ParagraphStyle("sigb", fontName=FONT_BOLD, fontSize=8.4, leading=10.8, textColor=C_NAVY_DARK, alignment=TA_CENTER)
            sig_tbl = Table([[
                [
                    Paragraph("CERTIFICACIÓN TÉCNICA Y ESTADÍSTICA OFICIAL", sig_b),
                    Spacer(1, 0.8 * mm),
                    Paragraph(
                        "Datos consolidados a partir de las planillas oficiales de cronometraje electrónico y resultados homologados de las Válidas I (GP Vitrix), II (GP BMW) y III Válida Final (GP IRC) del Campeonato Nacional GP Colombia 2026.",
                        sig_p,
                    ),
                    Spacer(1, 1.4 * mm),
                    Paragraph("<b>Mauricio Sánchez Aguilar</b> · Jefe de Cronometraje — Comisión de Juzgamiento FEDEMOTO", sig_b),
                    Paragraph("Federación Colombiana de Motociclismo · Correo oficial: <b>cronometraje@fedemoto.org</b>", sig_p),
                ]
            ]], colWidths=[182 * mm])
            sig_tbl.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, -1), C_SLATE_50),
                ("BOX", (0, 0), (-1, -1), 0.9, C_NAVY),
                ("LINEABOVE", (0, 0), (-1, 0), 2.0, C_GOLD),
                ("TOPPADDING", (0, 0), (-1, -1), 1.8 * mm),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 1.8 * mm),
                ("LEFTPADDING", (0, 0), (-1, -1), 4 * mm),
                ("RIGHTPADDING", (0, 0), (-1, -1), 4 * mm),
            ]))
            story.append(KeepTogether([sig_tbl]))

    os.makedirs(os.path.dirname(OUTPUT_PDF), exist_ok=True)
    doc = BaseDocTemplate(
        OUTPUT_PDF,
        pagesize=A4,
        leftMargin=14 * mm,
        rightMargin=14 * mm,
        topMargin=18 * mm,
        bottomMargin=15 * mm,
        title="Informe Ejecutivo Marca BAJAJ — GP Colombia 2026 | FEDEMOTO",
        author="Mauricio Sánchez Aguilar - Jefe de Cronometraje FEDEMOTO",
        subject="Participaciones y Rendimiento Deportivo Bajaj en GP Colombia 2026",
    )

    frame_cover = Frame(14 * mm, 15 * mm, A4[0] - 28 * mm, A4[1] - 25 * mm, id="cover_frame", topPadding=0, bottomPadding=0, leftPadding=0, rightPadding=0)
    frame_later = Frame(14 * mm, 15 * mm, A4[0] - 28 * mm, A4[1] - 34 * mm, id="later_frame", topPadding=0, bottomPadding=0, leftPadding=0, rightPadding=0)

    def on_first(canvas, d):
        draw_header_footer(canvas, d)
        d.handle_nextPageTemplate("LaterPages")

    doc.addPageTemplates([
        PageTemplate(id="FirstPage", frames=[frame_cover], onPage=on_first),
        PageTemplate(id="LaterPages", frames=[frame_later], onPage=draw_header_footer),
    ])

    doc.build(story)
    print(f"PDF generado exitosamente: {OUTPUT_PDF}")


if __name__ == "__main__":
    build_pdf()
