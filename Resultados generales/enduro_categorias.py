# -*- coding: utf-8 -*-
"""
Unifica nombres de categoría entre archivos exportados (p. ej. 'e1' vs 'enduro 1').
"""
import re
import unicodedata

_BY_NORM = {
    "e1": "Enduro 1",
    "e2": "Enduro 2",
    "e3": "Enduro 3",
    "enduro1": "Enduro 1",
    "enduro2": "Enduro 2",
    "enduro3": "Enduro 3",
    "fem": "Femenino",
    "femenina": "Femenino",
    "femenino": "Femenino",
    "infe1": "Infantil Enduro 1",
    "infe2": "Infantil Enduro 2",
    "infe3": "Infantil Enduro 3",
    "infantilenduro1": "Infantil Enduro 1",
    "infantilenduro2": "Infantil Enduro 2",
    "infantilenduro3": "Infantil Enduro 3",
    "jun": "Junior",
    "junior": "Junior",
    "junnov": "Junior Novatos",
    "juniornovatos": "Junior Novatos",
    "juv": "Juvenil",
    "juvenil": "Juvenil",
    "masa": "Master A",
    "masb": "Master B",
    "mastera": "Master A",
    "masterb": "Master B",
    "inicio": "Inicio",
    "noracer": "No Racer",
    "scratch": "Scratch",
}


def _normalize_key(text):
    s = str(text or "").strip().lower()
    s = "".join(c for c in unicodedata.normalize("NFD", s) if unicodedata.category(c) != "Mn")
    s = re.sub(r"[^a-z0-9]+", "", s)
    return s


def canonical_enduro_categoria(cat):
    """Devuelve el nombre canónico de categoría (como en la I válida) o el mismo texto si no aplica."""
    if not cat or not str(cat).strip():
        return cat
    k = _normalize_key(cat)
    return _BY_NORM.get(k, cat)
