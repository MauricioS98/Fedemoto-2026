# -*- coding: utf-8 -*-
"""
Script para analizar archivos Excel de válidas y generar datos JSON
Asegura el manejo correcto de caracteres UTF-8 (acentos, ñ, etc.)
"""

import pandas as pd
import unicodedata
import json
from collections import defaultdict
import os
from datetime import datetime

def normalizar_liga(nombre):
    """
    Normaliza el nombre de la liga: quita tildes, convierte a mayúsculas,
    y limpia espacios extra.
    """
    if pd.isna(nombre) or nombre == '':
        return None
    
    # Convertir a string y limpiar
    nombre = str(nombre).strip()
    
    # Quitar tildes
    nombre = unicodedata.normalize('NFD', nombre)
    nombre = ''.join(c for c in nombre if unicodedata.category(c) != 'Mn')
    
    # Convertir a mayúsculas para unificar
    nombre = nombre.upper()
    
    return nombre

def extraer_datos_excel(excel_path):
    """
    Extrae todos los datos del Excel de una válida.
    Estructura: columnas de información del piloto + columnas de categorías con "x"
    """
    excel_file = pd.ExcelFile(excel_path)
    
    resultados = {
        'modalidades': {},
        'total_pilotos_unicos': set(),
        'total_participaciones': 0,
        'pilotos_por_categoria': defaultdict(set),
        'deportistas_por_liga_total': defaultdict(set),
        'deportistas_por_liga_categoria': defaultdict(lambda: defaultdict(set)),
        'participaciones_por_edad': defaultdict(int)
    }
    
    print(f"Procesando {len(excel_file.sheet_names)} hojas...")
    
    for sheet_name in excel_file.sheet_names:
        print(f"\nProcesando hoja: {sheet_name}")
        df = pd.read_excel(excel_file, sheet_name=sheet_name)
        
        modalidad_data = {
            'pilotos_unicos': set(),
            'total_participaciones': 0,
            'pilotos_por_categoria': defaultdict(set),
            'deportistas_por_liga': defaultdict(set),
            'deportistas_por_liga_categoria': defaultdict(lambda: defaultdict(set)),
            'participaciones_por_edad': defaultdict(int)
        }
        
        # Fecha de referencia para calcular edades (año actual)
        fecha_referencia = datetime.now()
        
        # Identificar columnas de información del piloto (excluir categorías)
        columnas_info = ['Consecutivo', 'Licencia', 'TX', 'Nombre', 'Apellido', 'Liga', 
                        'Club', 'FN', 'RH', 'MOTO', 'Documento', 'EPS', 'Pago Licencia', 
                        'Poliza', 'Celular', 'Mail', 'Formatos']
        
        # Identificar columnas de categorías (las que no están en columnas_info)
        columnas_categorias = []
        for col in df.columns:
            if col not in columnas_info and str(col) != 'nan':
                # Verificar si esta columna tiene valores "x" (indicando participación)
                if df[col].notna().any():
                    valores_unicos = df[col].dropna().unique()
                    # Si tiene "x" o valores similares, es una categoría
                    if any(str(v).upper().strip() in ['X', 'x', 'X ', ' x'] for v in valores_unicos):
                        columnas_categorias.append(col)
        
        print(f"  Categorías encontradas: {columnas_categorias}")
        
        # Verificar que tenemos la columna Liga
        if 'Liga' not in df.columns:
            print(f"  ADVERTENCIA: No se encontró la columna 'Liga'")
            continue
        
        # Procesar cada fila
        for idx, row in df.iterrows():
            licencia = row.get('Licencia', None)
            liga = row.get('Liga', None)
            
            # Validar que tenemos licencia y liga
            if pd.isna(licencia) or pd.isna(liga):
                continue
            
            licencia = int(licencia) if isinstance(licencia, (int, float)) else licencia
            liga_normalizada = normalizar_liga(liga)
            
            if not liga_normalizada:
                continue
            
            # Calcular edad si hay fecha de nacimiento
            edad_rango = None
            fecha_nacimiento = row.get('FN', None)
            if pd.notna(fecha_nacimiento):
                try:
                    if isinstance(fecha_nacimiento, str):
                        fecha_nac = pd.to_datetime(fecha_nacimiento)
                    else:
                        fecha_nac = fecha_nacimiento
                    
                    edad = fecha_referencia.year - fecha_nac.year
                    if fecha_referencia.month < fecha_nac.month or (fecha_referencia.month == fecha_nac.month and fecha_referencia.day < fecha_nac.day):
                        edad -= 1
                    
                    # Agrupar en rangos de 5 años, empezando desde 1-5 años
                    if edad < 1:
                        edad_rango = "0 años"
                    elif edad <= 5:
                        edad_rango = "1-5 años"
                    elif edad <= 10:
                        edad_rango = "6-10 años"
                    elif edad <= 15:
                        edad_rango = "11-15 años"
                    elif edad <= 20:
                        edad_rango = "16-20 años"
                    elif edad <= 25:
                        edad_rango = "21-25 años"
                    elif edad <= 30:
                        edad_rango = "26-30 años"
                    elif edad <= 35:
                        edad_rango = "31-35 años"
                    elif edad <= 40:
                        edad_rango = "36-40 años"
                    elif edad <= 45:
                        edad_rango = "41-45 años"
                    elif edad <= 50:
                        edad_rango = "46-50 años"
                    elif edad <= 55:
                        edad_rango = "51-55 años"
                    elif edad <= 60:
                        edad_rango = "56-60 años"
                    elif edad <= 65:
                        edad_rango = "61-65 años"
                    else:
                        edad_rango = "66+ años"
                except:
                    pass  # Si no se puede calcular la edad, se omite
            
            # Procesar cada categoría
            for categoria in columnas_categorias:
                valor_categoria = row.get(categoria, None)
                
                # Verificar si el piloto participa en esta categoría (tiene "x")
                if pd.notna(valor_categoria):
                    valor_str = str(valor_categoria).upper().strip()
                    if valor_str in ['X', 'X ', ' X']:
                        # El piloto participa en esta categoría
                        resultados['total_pilotos_unicos'].add(licencia)
                        resultados['total_participaciones'] += 1
                        resultados['pilotos_por_categoria'][categoria].add(licencia)
                        resultados['deportistas_por_liga_total'][liga_normalizada].add(licencia)
                        resultados['deportistas_por_liga_categoria'][categoria][liga_normalizada].add(licencia)
                        
                        # Agregar participación por edad
                        if edad_rango:
                            resultados['participaciones_por_edad'][edad_rango] += 1
                        
                        # Agregar a modalidad específica
                        modalidad_data['pilotos_unicos'].add(licencia)
                        modalidad_data['total_participaciones'] += 1
                        modalidad_data['pilotos_por_categoria'][categoria].add(licencia)
                        modalidad_data['deportistas_por_liga'][liga_normalizada].add(licencia)
                        modalidad_data['deportistas_por_liga_categoria'][categoria][liga_normalizada].add(licencia)
                        
                        # Agregar participación por edad en modalidad
                        if edad_rango:
                            modalidad_data['participaciones_por_edad'][edad_rango] += 1
        
        resultados['modalidades'][sheet_name] = modalidad_data
    
    return resultados

def generar_json(resultados, output_file):
    """
    Genera un archivo JSON con los datos estructurados para la página web.
    """
    datos_json = {
        'total_pilotos_unicos': len(resultados['total_pilotos_unicos']),
        'total_participaciones': resultados['total_participaciones'],
        'pilotos_por_categoria': {
            cat: len(pilotos) 
            for cat, pilotos in sorted(resultados['pilotos_por_categoria'].items())
        },
        'deportistas_por_liga_total': {
            liga: len(deportistas) 
            for liga, deportistas in sorted(resultados['deportistas_por_liga_total'].items())
        },
        'deportistas_por_liga_categoria': {
            cat: {
                liga: len(deportistas)
                for liga, deportistas in sorted(ligas.items())
            }
            for cat, ligas in sorted(resultados['deportistas_por_liga_categoria'].items())
        },
        'participaciones_por_edad': dict(sorted(resultados['participaciones_por_edad'].items())),
        'modalidades': {
            modalidad: {
                'pilotos_unicos': len(data['pilotos_unicos']),
                'total_participaciones': data['total_participaciones'],
                'pilotos_por_categoria': {
                    cat: len(pilotos)
                    for cat, pilotos in sorted(data['pilotos_por_categoria'].items())
                },
                'deportistas_por_liga': {
                    liga: len(deportistas)
                    for liga, deportistas in sorted(data['deportistas_por_liga'].items())
                },
                'deportistas_por_liga_categoria': {
                    cat: {
                        liga: len(deportistas)
                        for liga, deportistas in sorted(ligas.items())
                    }
                    for cat, ligas in sorted(data['deportistas_por_liga_categoria'].items())
                },
                'participaciones_por_edad': dict(sorted(data['participaciones_por_edad'].items()))
            }
            for modalidad, data in resultados['modalidades'].items()
        }
    }
    
    # Escribir JSON con encoding UTF-8 y ensure_ascii=False para preservar caracteres especiales
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(datos_json, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"Error al escribir el archivo JSON: {e}")
        raise
    
    print(f"JSON generado en: {output_file}")
    return datos_json

# Ejecutar análisis
# Uso: python analizar_valida.py <ruta_excel> <ruta_output_json>
# Ejemplo: python analizar_valida.py "Valida de ejemplo/valejempo.xlsx" "Valida de ejemplo/datos_valida_ejemplo.json"
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 3:
        print("Uso: python analizar_valida.py <ruta_excel> <ruta_output_json>")
        print('Ejemplo: python analizar_valida.py "Valida de ejemplo/valejempo.xlsx" "Valida de ejemplo/datos_valida_ejemplo.json"')
        sys.exit(1)
    
    excel_path = sys.argv[1]
    output_json = sys.argv[2]
    
    print("Iniciando análisis del Excel de ejemplo...")
    resultados = extraer_datos_excel(excel_path)
    
    print("\nGenerando JSON...")
    datos_json = generar_json(resultados, output_json)
    
    print("\n¡Análisis completado!")
    print(f"\nResumen:")
    print(f"- Total pilotos únicos: {datos_json['total_pilotos_unicos']}")
    print(f"- Total participaciones: {datos_json['total_participaciones']}")
    print(f"- Modalidades: {len(datos_json['modalidades'])}")
    print(f"\nCategorías encontradas:")
    for cat in sorted(datos_json['pilotos_por_categoria'].keys()):
        print(f"  - {cat}: {datos_json['pilotos_por_categoria'][cat]} pilotos únicos")
