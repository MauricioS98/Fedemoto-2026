#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para sincronizar los Reglamentos Particulares (RP) en menu.html.
Busca todos los archivos PDF en 'Reglamentos particulares/' y asegura que cada uno
tenga su respectivo enlace en menu.html.
"""

import os
import re
import sys

# Configurar salida utf-8 en Windows para evitar errores de consola
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

# Mapeo de carpetas de disco a etiquetas en el menú
MODALIDADES_CONFIG = {
    "Enduro": {
        "menu_label": "Enduro",
        "has_semesters": False,
        "indent": "                                ",  # 32 espacios
    },
    "GP Colombia": {
        "menu_label": "GP Colombia",
        "has_semesters": False,
        "indent": "                                ",  # 32 espacios
    },
    "Motocross": {
        "menu_label": "Motocross",
        "has_semesters": True,
        "indent": "                                        ",  # 40 espacios
    },
    "Velotierra": {
        "menu_label": "Velotierra",
        "has_semesters": True,
        "indent": "                                        ",  # 40 espacios
    },
    "Velocidad": {
        "menu_label": "Velocidad en Kartodromo",
        "has_semesters": True,
        "indent": "                                        ",  # 40 espacios
    },
}

ROMAN_ORDER = ["I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X", "XI", "XII"]

def extract_roman_index(filename):
    """Devuelve un índice para ordenar por el número de válida romano."""
    for idx, r in enumerate(ROMAN_ORDER):
        # Coincidir con 'RP I ', 'VAL I ', ' I ', etc.
        pattern = r'(?:\bRP\s+|\bVAL\s+|\b)' + r + r'(?:\s+VAL|\s+SEM|\b)'
        if re.search(pattern, filename, re.IGNORECASE):
            return idx
    return 999

def sync_rp(workspace_dir=None, dry_run=False):
    if workspace_dir is None:
        if os.path.exists("menu.html"):
            workspace_dir = os.path.abspath(".")
        else:
            workspace_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))

    menu_path = os.path.join(workspace_dir, "menu.html")
    rp_base_dir = os.path.join(workspace_dir, "Reglamentos particulares")

    if not os.path.exists(menu_path):
        print(f"ERROR: No se encontró {menu_path}")
        return False
    if not os.path.exists(rp_base_dir):
        print(f"ERROR: No se encontró {rp_base_dir}")
        return False

    with open(menu_path, "r", encoding="utf-8") as f:
        menu_lines = f.readlines()

    menu_full_text = "".join(menu_lines)

    # 1. Encontrar todos los PDFs en 'Reglamentos particulares/'
    found_pdfs = []
    for root, _, files in os.walk(rp_base_dir):
        for file in files:
            if file.lower().endswith(".pdf"):
                full_path = os.path.join(root, file)
                rel_path = os.path.relpath(full_path, workspace_dir).replace("\\", "/")
                found_pdfs.append((rel_path, root, file))

    # 2. Filtrar los que faltan en menu.html
    missing_pdfs = []
    for rel_path, root, filename in found_pdfs:
        if rel_path not in menu_full_text:
            missing_pdfs.append((rel_path, root, filename))

    if not missing_pdfs:
        print("[OK] Todos los Reglamentos Particulares ya están sincronizados en menu.html.")
        return True

    print(f"Se encontraron {len(missing_pdfs)} reglamento(s) faltante(s) en menu.html:")
    for rel_path, _, fname in missing_pdfs:
        print(f"  - {fname}")

    # 3. Procesar e insertar cada archivo faltante
    added_count = 0
    for rel_path, root, filename in missing_pdfs:
        rel_from_rp = os.path.relpath(root, rp_base_dir).replace("\\", "/")
        parts = [p for p in rel_from_rp.split("/") if p and p != "."]
        if not parts:
            print(f"[AVISO] Archivo en raíz de RP ignorado: {filename}")
            continue

        folder_mod = parts[0]
        folder_sem = parts[1] if len(parts) > 1 else None

        config = MODALIDADES_CONFIG.get(folder_mod)
        if not config:
            print(f"[AVISO] Modalidad desconocida '{folder_mod}' para {filename}")
            continue

        menu_mod_label = config["menu_label"]
        has_semesters = config["has_semesters"]
        indent = config["indent"]
        link_text = os.path.splitext(filename)[0]
        new_line = f'{indent}<li><a href="{rel_path}" target="_blank">{link_text}</a></li>\n'

        # Localizar el bloque en menu_lines
        in_rp = False
        in_mod = False
        in_sem = False
        insertion_idx = -1
        last_li_idx = -1

        for idx, line in enumerate(menu_lines):
            # Detectar inicio de Reglamentos particulares
            if "Reglamentos particulares" in line and "<a" in line:
                in_rp = True
                continue

            if not in_rp:
                continue

            # Si salimos de Reglamentos particulares
            if in_rp and not in_mod and "</nav>" in line:
                break

            # Detectar modalidad
            if in_rp and f">{menu_mod_label}<" in line:
                in_mod = True
                continue

            if in_mod:
                if has_semesters and folder_sem:
                    # Detectar semestre
                    if f">{folder_sem}<" in line:
                        in_sem = True
                        continue

                    if in_sem:
                        if "<li" in line and "<a" in line and "href=" in line:
                            last_li_idx = idx
                        elif "</ul>" in line:
                            # Fin de la lista del semestre
                            insertion_idx = last_li_idx + 1 if last_li_idx != -1 else idx
                            break
                else:
                    # Sin semestres (Enduro, GP Colombia)
                    if "<li" in line and "<a" in line and "href=" in line:
                        last_li_idx = idx
                    elif "</ul>" in line and last_li_idx != -1:
                        insertion_idx = last_li_idx + 1
                        break
                    elif "</ul>" in line and "<li class=\"dropdown\">" not in line:
                        insertion_idx = idx
                        break

        if insertion_idx != -1:
            menu_lines.insert(insertion_idx, new_line)
            added_count += 1
            sem_info = f" > {folder_sem}" if folder_sem else ""
            print(f"  [+] Insertado en [{menu_mod_label}{sem_info}]: {filename}")
        else:
            print(f"  [!] No se pudo ubicar la sección para: {menu_mod_label} / {folder_sem}")

    if added_count > 0 and not dry_run:
        with open(menu_path, "w", encoding="utf-8") as f:
            f.writelines(menu_lines)
        print(f"[ÉXITO] Se agregaron {added_count} reglamento(s) a menu.html correctamente.")
    elif dry_run:
        print(f"[DRY-RUN] Se habrían insertado {added_count} elementos sin modificar el archivo.")

    return True

if __name__ == "__main__":
    dry_run = "--dry-run" in sys.argv
    sync_rp(dry_run=dry_run)
