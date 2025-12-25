# -*- coding: utf-8 -*-
"""
Script para generar informes HTML a partir de datos JSON
Asegura el manejo correcto de caracteres UTF-8 (acentos, ñ, etc.)
"""

import json
import os
import sys
import re
import glob

# Configurar encoding UTF-8 para stdout en Windows
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# Uso: python generar_informe.py <ruta_json> <ruta_output_html> <nombre_valida>
# Ejemplo: python generar_informe.py "Valida de ejemplo/datos_valida_ejemplo.json" "Valida de ejemplo/informe_valida_ejemplo.html" "Valida de ejemplo"

if len(sys.argv) < 4:
    print("Uso: python generar_informe.py <ruta_json> <ruta_output_html> <nombre_valida>")
    print('Ejemplo: python generar_informe.py "Valida de ejemplo/datos_valida_ejemplo.json" "Valida de ejemplo/informe_valida_ejemplo.html" "Valida de ejemplo"')
    sys.exit(1)

json_path = sys.argv[1]
output_path = sys.argv[2]
# Decodificar nombre_valida correctamente para UTF-8
nombre_valida = sys.argv[3]
try:
    # Intentar decodificar desde la codificación del sistema
    nombre_valida = nombre_valida.encode('latin-1').decode('utf-8')
except:
    try:
        # Si falla, intentar directamente
        nombre_valida = nombre_valida.encode('cp1252').decode('utf-8')
    except:
        # Si todo falla, usar tal cual
        pass

# Calcular la profundidad del archivo de salida para las rutas relativas
# output_path puede ser relativo a Informes/ o incluir "Informes/" en el path
# Normalizar el path para trabajar con rutas relativas desde Informes/
script_dir = os.path.dirname(os.path.abspath(__file__))

# Si output_path incluye "Informes/", removerlo para trabajar relativo a Informes/
output_path_norm = output_path.replace('\\', '/')
if 'Informes/' in output_path_norm:
    # Extraer la parte después de "Informes/"
    parts = output_path_norm.split('Informes/')
    if len(parts) > 1:
        output_path_rel = parts[-1]
    else:
        output_path_rel = output_path_norm
else:
    output_path_rel = output_path_norm

output_dir = os.path.dirname(output_path_rel)
# Contar cuántos niveles hay desde Informes/ hasta el archivo
# Si output_path_rel es "Modalidad de ejemplo/informe.html", output_dir es "Modalidad de ejemplo"
# Necesitamos subir depth niveles desde el archivo hasta Informes/, y luego 1 más hasta la raíz
if output_dir:
    # Contar partes del directorio (normalizar separadores)
    output_dir_norm = output_dir.replace('\\', '/')
    depth = len([p for p in output_dir_norm.split('/') if p]) if output_dir_norm else 0
else:
    depth = 0

# Calcular niveles hasta la raíz:
# - Si depth = 0: archivo está en Informes/, necesitamos subir 1 nivel (../)
# - Si depth = 1: archivo está en Informes/Modalidad/, necesitamos subir 2 niveles (../../)
depth_to_root = depth + 1

# Generar las rutas relativas
ruta_inicio = '../' * depth_to_root + 'index.html'
ruta_logo = '../' * depth_to_root + 'fedemoto-logo.png'
# Para informe_2025_fedemoto.html, está en Informes/, así que desde Informes/Modalidad/ es ../informe_2025_fedemoto.html
# Desde Informes/ es informe_2025_fedemoto.html (mismo nivel)
if depth == 0:
    ruta_informe_2025 = 'informe_2025_fedemoto.html'
else:
    ruta_informe_2025 = '../' * (depth_to_root - 1) + 'informe_2025_fedemoto.html'

# Leer los datos del JSON con encoding UTF-8
try:
    with open(json_path, 'r', encoding='utf-8') as f:
        datos = json.load(f)
except UnicodeDecodeError:
    # Si falla, intentar con diferentes encodings
    with open(json_path, 'r', encoding='latin-1') as f:
        datos = json.load(f)
except Exception as e:
    print(f"Error al leer el archivo JSON: {e}")
    sys.exit(1)

# Convertir datos a formato JavaScript
datos_js = json.dumps(datos, ensure_ascii=False, indent=2)

# Generar el HTML
html_content = f'''<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Informe - {nombre_valida}</title>
    <link rel="icon" type="image/png" href="{ruta_logo}">
    <!-- Librerías para generar PDF -->
    <script src="https://cdnjs.cloudflare.com/ajax/libs/jspdf/2.5.1/jspdf.umd.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/html2canvas/1.4.1/html2canvas.min.js"></script>
    <!-- SweetAlert2 para modales -->
    <script src="https://cdn.jsdelivr.net/npm/sweetalert2@11"></script>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: #ffffff;
            color: #333;
            line-height: 1.6;
            padding: 20px;
            padding-top: 120px;
            min-height: 100vh;
        }}

        /* Header fijo con menú */
        .fixed-header {{
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            background: #123E92;
            color: white;
            z-index: 10000;
            box-shadow: 0 4px 10px rgba(0,0,0,0.2);
            width: 100%;
        }}

        .header-content {{
            max-width: 1400px;
            margin: 0 auto;
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 15px 30px;
            width: 100%;
        }}

        .logo-container {{
            display: flex;
            align-items: center;
            gap: 15px;
        }}

        .logo-container img {{
            height: 50px;
            width: auto;
        }}

        .logo-container h1 {{
            font-size: 1.8em;
            margin: 0;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
        }}

        .nav-menu {{
            display: flex;
            gap: 0;
            list-style: none;
            margin: 0;
            padding: 0;
        }}

        .nav-menu li {{
            margin: 0;
            padding: 0;
            position: relative;
        }}

        .nav-menu > li > a {{
            display: block;
            padding: 12px 25px;
            color: white;
            text-decoration: none;
            font-weight: 500;
            font-size: 1.1em;
            transition: all 0.3s;
            border-radius: 5px;
            position: relative;
            white-space: nowrap;
            cursor: pointer;
        }}

        .nav-menu > li > a:hover {{
            background: rgba(255,255,255,0.1);
            transform: translateY(-2px);
        }}

        .nav-menu > li > a.active {{
            background: #F7C31D;
            color: #123E92;
        }}

        /* Menú desplegable */
        .dropdown {{
            position: relative;
        }}

        .dropdown > a::after {{
            content: ' ▼';
            font-size: 0.8em;
            margin-left: 5px;
        }}

        /* Puente invisible para mantener el hover activo */
        .dropdown::before {{
            content: '';
            position: absolute;
            top: 100%;
            left: 0;
            right: 0;
            height: 5px;
            background: transparent;
            z-index: 10002;
        }}

        .dropdown-menu {{
            display: none;
            position: absolute;
            top: calc(100% + 5px);
            left: 0;
            background: white;
            min-width: 200px;
            width: 220px;
            box-shadow: 0 8px 16px rgba(0,0,0,0.2);
            border-radius: 8px;
            z-index: 10001;
            list-style: none;
            padding: 0;
            margin: 0;
            overflow: visible;
        }}
        
        /* Submenús dentro de dropdowns (para Motocross, Velotierra, etc.) */
        .dropdown-menu .dropdown {{
            position: relative;
        }}
        
        /* Puente invisible para submenús anidados */
        .dropdown-menu .dropdown::before {{
            content: '';
            position: absolute;
            top: 0;
            left: 100%;
            width: 10px;
            height: 100%;
            background: transparent;
            z-index: 10004;
        }}
        
        .dropdown-menu .dropdown > a {{
            position: relative;
            padding-right: 35px;
        }}
        
        .dropdown-menu .dropdown > a::after {{
            content: ' ▶';
            position: absolute;
            right: 15px;
            top: 50%;
            transform: translateY(-50%);
            font-size: 0.8em;
            margin: 0;
            float: none;
        }}
        
        .dropdown-menu .dropdown .dropdown-menu {{
            display: none !important;
            position: absolute;
            left: 100%;
            top: 0;
            margin-left: 5px;
            z-index: 10003;
            min-width: 180px;
            background: white;
            box-shadow: 0 8px 16px rgba(0,0,0,0.2);
            border-radius: 8px;
            overflow: visible;
        }}
        
        /* En "Resultados generales", mostrar submenús a la izquierda */
        .nav-menu > .dropdown:nth-child(4) .dropdown-menu > .dropdown > .dropdown-menu {{
            left: auto;
            right: 100%;
            margin-left: 0;
            margin-right: 5px;
        }}
        
        .dropdown-menu .dropdown:hover > .dropdown-menu {{
            display: block !important;
        }}

        /* Solo aplicar hover al primer nivel de dropdown (no a submenús anidados) */
        .nav-menu > .dropdown:hover > .dropdown-menu,
        .nav-menu > .dropdown.active > .dropdown-menu {{
            display: block;
            animation: fadeInDown 0.3s ease;
        }}

        @keyframes fadeInDown {{
            from {{
                opacity: 0;
                transform: translateY(-10px);
            }}
            to {{
                opacity: 1;
                transform: translateY(0);
            }}
        }}

        .dropdown-menu li {{
            margin: 0;
            position: relative;
        }}

        .dropdown-menu a {{
            display: block;
            padding: 12px 20px;
            color: #333;
            text-decoration: none;
            font-size: 1em;
            transition: all 0.2s;
            border-bottom: 1px solid #f0f0f0;
        }}

        .dropdown-menu a:last-child {{
            border-bottom: none;
        }}

        .dropdown-menu a:hover {{
            background: #f8f9fa;
            color: #123E92;
        }}
        
        /* Los elementos con submenú mantienen el padding al hacer hover */
        .dropdown-menu .dropdown > a:hover {{
            padding-left: 20px;
        }}

        .dropdown-menu a.active {{
            background: #F7C31D;
            color: #123E92;
            font-weight: 600;
        }}

        .dropdown.active > a {{
            background: rgba(255,255,255,0.15);
        }}

        .container {{
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            overflow: hidden;
        }}

        .container > header {{
            background: #123E92;
            color: white;
            padding: 40px;
            text-align: center;
        }}

        .container > header h1 {{
            font-size: 2.5em;
            margin-bottom: 10px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
        }}

        .container > header p {{
            font-size: 1.2em;
            opacity: 0.9;
        }}

        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            padding: 30px;
            background: #f8f9fa;
        }}

        .stat-card {{
            background: white;
            padding: 25px;
            border-radius: 15px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
            text-align: center;
            transition: transform 0.3s, box-shadow 0.3s;
        }}

        .stat-card:hover {{
            transform: translateY(-5px);
            box-shadow: 0 10px 25px rgba(0,0,0,0.2);
        }}

        .stat-card .number {{
            font-size: 3em;
            font-weight: bold;
            color: #123E92;
            margin-bottom: 10px;
        }}

        .stat-card .label {{
            font-size: 1.1em;
            color: #666;
            text-transform: uppercase;
            letter-spacing: 1px;
        }}

        .section {{
            padding: 40px;
            border-bottom: 1px solid #e0e0e0;
        }}

        .section:last-child {{
            border-bottom: none;
        }}

        .section h2 {{
            font-size: 2em;
            color: #123E92;
            margin-bottom: 25px;
            padding-bottom: 15px;
            border-bottom: 3px solid #F7C31D;
        }}

        .chart-container {{
            background: white;
            padding: 20px;
            border-radius: 10px;
            margin-top: 20px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            overflow-x: auto;
        }}

        .bar-chart {{
            display: flex;
            flex-direction: column;
            gap: 10px;
            min-width: 100%;
        }}

        .bar-item {{
            display: flex;
            align-items: center;
            gap: 15px;
            min-width: 100%;
        }}

        .bar-label {{
            min-width: 120px;
            max-width: 120px;
            font-weight: 500;
            color: #333;
            font-size: 0.9em;
            flex-shrink: 0;
        }}

        .bar-wrapper {{
            flex: 1;
            height: 30px;
            background: #e0e0e0;
            border-radius: 15px;
            overflow: hidden;
            position: relative;
            display: flex;
            align-items: flex-end;
        }}

        .bar-fill {{
            height: 100%;
            background: #123E92;
            border-radius: 15px;
            transition: width 1s ease-out;
            display: flex;
            align-items: center;
            justify-content: flex-end;
            padding-right: 10px;
            color: white;
            font-weight: bold;
            font-size: 0.9em;
        }}

        /* Gráfica de columnas verticales */
        .column-chart {{
            display: flex;
            flex-direction: row;
            align-items: flex-end;
            justify-content: space-around;
            gap: 15px;
            min-height: 300px;
            padding: 20px 0;
        }}

        .column-item {{
            display: flex;
            flex-direction: column;
            align-items: center;
            flex: 1;
            min-width: 60px;
            max-width: 120px;
        }}

        .column-wrapper {{
            width: 100%;
            height: 250px;
            background: #e0e0e0;
            border-radius: 5px 5px 0 0;
            position: relative;
            display: flex;
            align-items: flex-end;
            justify-content: center;
        }}

        .column-fill {{
            width: 100%;
            background: #123E92;
            border-radius: 5px 5px 0 0;
            transition: height 1s ease-out;
            display: flex;
            align-items: flex-start;
            justify-content: center;
            padding-top: 5px;
            color: white;
            font-weight: bold;
            font-size: 0.9em;
            min-height: 20px;
            position: relative;
        }}

        .column-label {{
            margin-top: 10px;
            font-weight: 500;
            color: #333;
            font-size: 0.85em;
            text-align: center;
            word-wrap: break-word;
            max-width: 100%;
        }}

        .filters-container {{
            display: grid;
            grid-template-columns: 2fr 1fr 1fr;
            gap: 15px;
            margin-bottom: 20px;
        }}

        .search-box {{
            width: 100%;
            padding: 15px;
            font-size: 1em;
            border: 2px solid #e0e0e0;
            border-radius: 10px;
            transition: border-color 0.3s;
            box-sizing: border-box;
        }}

        .search-box:focus {{
            outline: none;
            border-color: #F7C31D;
        }}

        .filter-select {{
            padding: 15px;
            font-size: 1em;
            border: 2px solid #e0e0e0;
            border-radius: 10px;
            background: white;
            cursor: pointer;
            transition: border-color 0.3s;
            width: 100%;
            box-sizing: border-box;
        }}

        .filter-select:focus {{
            outline: none;
            border-color: #F7C31D;
        }}

        footer {{
            background: #f8f9fa;
            padding: 30px 40px;
            text-align: center;
            border-top: 1px solid #e0e0e0;
            color: #666;
            font-size: 0.9em;
            line-height: 1.8;
        }}

        @media (max-width: 768px) {{
            body {{
                padding: 10px;
                padding-top: 150px;
            }}

            .header-content {{
                flex-direction: column;
                padding: 15px 20px;
            }}

            .logo-container {{
                margin-bottom: 15px;
            }}

            .nav-menu {{
                flex-direction: column;
                width: 100%;
                gap: 5px;
            }}

            .dropdown-menu {{
                position: static;
                display: none;
                box-shadow: none;
                border-radius: 0;
                background: rgba(255,255,255,0.1);
            }}

            .nav-menu > .dropdown:hover > .dropdown-menu,
            .nav-menu > .dropdown.active > .dropdown-menu {{
                display: block;
            }}

            .dropdown-menu a {{
                color: white;
                padding: 10px 20px;
            }}

            .stats-grid {{
                grid-template-columns: 1fr;
            }}

            .section {{
                padding: 25px 15px;
            }}
        }}
    </style>
</head>
<body>
    <!-- Header fijo con menú -->
    <header class="fixed-header">
        <div class="header-content">
            <div class="logo-container">
                <img src="{ruta_logo.replace(chr(92), '/')}" alt="Logo FEDEMOTO">
                <h1>Fedemoto</h1>
            </div>
            <nav>
                <ul class="nav-menu">
                    <li><a href="{ruta_inicio}">Inicio</a></li>
                    <li class="dropdown">
                        <a href="#">Informes</a>
                        <ul class="dropdown-menu">
                            <li><a href="{ruta_informe_2025}">Informe Anual 2025</a></li>
                            <li><a href="#">Enduro</a></li>
                            <li><a href="#">GP Colombia</a></li>
                            <li class="dropdown">
                                <a href="#">Modalidad de ejemplo</a>
                                <ul class="dropdown-menu">
                                    <li><a href="Modalidad de ejemplo/informe_valida_ejemplo.html">Válida de ejemplo</a></li>
                                    <li><a href="Modalidad de ejemplo/informe_valida_ejemplo2.html">Válida de ejemplo 2</a></li>
                                </ul>
                            </li>
                            <li class="dropdown">
                                <a href="#">Motocross</a>
                                <ul class="dropdown-menu">
                                    <li><a href="#">Primer semestre</a></li>
                                    <li><a href="#">Segundo semestre</a></li>
                                </ul>
                            </li>
                            <li><a href="#">Velocidad</a></li>
                            <li class="dropdown">
                                <a href="#">Velotierra</a>
                                <ul class="dropdown-menu">
                                    <li><a href="#">Primer semestre</a></li>
                                    <li><a href="#">Segundo semestre</a></li>
                                </ul>
                            </li>
                        </ul>
                    </li>
                    <li class="dropdown">
                        <a href="#">Resultados de válidas</a>
                        <ul class="dropdown-menu">
                            <li><a href="#">Enduro</a></li>
                            <li><a href="#">GP Colombia</a></li>
                            <li><a href="#">Valida de ejemplo</a></li>
                            <li class="dropdown">
                                <a href="#">Motocross</a>
                                <ul class="dropdown-menu">
                                    <li><a href="#">Primer semestre</a></li>
                                    <li><a href="#">Segundo semestre</a></li>
                                </ul>
                            </li>
                            <li><a href="#">Velocidad</a></li>
                            <li class="dropdown">
                                <a href="#">Velotierra</a>
                                <ul class="dropdown-menu">
                                    <li><a href="#">Primer semestre</a></li>
                                    <li><a href="#">Segundo semestre</a></li>
                                </ul>
                            </li>
                        </ul>
                    </li>
                    <li class="dropdown">
                        <a href="#">Resultados generales</a>
                        <ul class="dropdown-menu">
                            <li><a href="#">Enduro</a></li>
                            <li><a href="#">GP Colombia</a></li>
                            <li><a href="#">Valida de ejemplo</a></li>
                            <li class="dropdown">
                                <a href="#">Motocross</a>
                                <ul class="dropdown-menu">
                                    <li><a href="#">Primer semestre</a></li>
                                    <li><a href="#">Segundo semestre</a></li>
                                </ul>
                            </li>
                            <li><a href="#">Velocidad</a></li>
                            <li class="dropdown">
                                <a href="#">Velotierra</a>
                                <ul class="dropdown-menu">
                                    <li><a href="#">Primer semestre</a></li>
                                    <li><a href="#">Segundo semestre</a></li>
                                </ul>
                            </li>
                        </ul>
                    </li>
                </ul>
            </nav>
        </div>
    </header>

    <div class="container">
        <header>
            <h1>
                <img src="{ruta_logo.replace(chr(92), '/')}" alt="FEDEMOTO Logo" style="height: 60px; vertical-align: middle; margin-right: 15px;">
                Informe - {nombre_valida}
            </h1>
            <p>Análisis completo de participantes y categorías</p>
        </header>

        <div id="content">
            <!-- Estadísticas principales -->
            <div class="stats-grid" id="statsGrid">
                <!-- Se llenará con JavaScript -->
            </div>

            <!-- Sección 1: Pilotos por categoría -->
            <div class="section">
                <h2>🏆 Pilotos por categoría</h2>
                <div class="chart-container">
                    <div class="bar-chart" id="categoriaChart">
                        <!-- Se llenará con JavaScript -->
                    </div>
                </div>
            </div>

            <!-- Sección 2: Deportistas por ligas totales -->
            <div class="section">
                <h2>🌎 Deportistas por ligas totales</h2>
                <div class="filters-container">
                    <input type="text" class="search-box" id="searchLiga" placeholder="🔍 Buscar liga...">
                    <select class="filter-select" id="filterSortLiga">
                        <option value="cantidad-desc">Ordenar por cantidad (mayor a menor)</option>
                        <option value="cantidad-asc">Ordenar por cantidad (menor a mayor)</option>
                        <option value="nombre-asc">Ordenar por nombre (A-Z)</option>
                        <option value="nombre-desc">Ordenar por nombre (Z-A)</option>
                    </select>
                </div>
                <div class="chart-container">
                    <div class="bar-chart" id="ligasChart">
                        <!-- Se llenará con JavaScript -->
                    </div>
                </div>
            </div>

            <!-- Sección 3: Deportistas por ligas por categoría -->
            <div class="section">
                <h2>📈 Deportistas por ligas por categoría</h2>
                <div class="filters-container" style="grid-template-columns: 1fr; max-width: 400px; margin-bottom: 30px;">
                    <select class="filter-select" id="filtroCategoriaLiga">
                        <option value="todas">Todas</option>
                    </select>
                </div>
                <div id="todasCategoriasLigaCharts">
                    <!-- Se llenará con todas las gráficas de categorías -->
                </div>
            </div>

            <!-- Sección 4: Participación por edad -->
            <div class="section">
                <h2>🎂 Participación por edad</h2>
                <div class="chart-container">
                    <div class="column-chart" id="edadChart">
                        <!-- Se llenará con JavaScript -->
                    </div>
                </div>
            </div>
        </div>

        <footer>
            <p><span class="developer">Developed by Mauricio Sánchez Aguilar - Fedemoto</span></p>
            <p>Este proyecto es de uso interno de FEDEMOTO.</p>
            <div style="text-align: center; margin-top: 30px; padding-top: 20px; border-top: 2px solid #e0e0e0;">
                <button id="descargarPDF" style="background: #123E92; color: white; border: none; padding: 15px 40px; font-size: 1.1em; border-radius: 8px; cursor: pointer; font-weight: 600; transition: all 0.3s; box-shadow: 0 4px 10px rgba(0,0,0,0.2);" onmouseover="this.style.background='#0d2d6b'; this.style.transform='translateY(-2px)'; this.style.boxShadow='0 6px 15px rgba(0,0,0,0.3)';" onmouseout="this.style.background='#123E92'; this.style.transform='translateY(0)'; this.style.boxShadow='0 4px 10px rgba(0,0,0,0.2)';">
                    📥 Descargar PDF
                </button>
                <p style="margin-top: 10px; color: #666; font-size: 0.9em;">Descarga este informe completo con todas las gráficas en formato PDF</p>
            </div>
        </footer>
    </div>

    <script>
        // Datos incrustados directamente para evitar problemas de CORS
        const datos = {datos_js};

        // Función para corregir ortografía de departamentos
        function corregirOrtografiaDepartamento(nombre) {{
            const correcciones = {{
                'NARINO': 'Nariño',
                'QUINDIO': 'Quindío',
                'BOGOTA': 'Bogotá',
                'VALLE': 'Valle del Cauca',
                'ANTIOQUIA': 'Antioquia',
                'ARAUCA': 'Arauca',
                'CALDAS': 'Caldas',
                'CASANARE': 'Casanare',
                'CAUCA': 'Cauca',
                'CESAR': 'Cesar',
                'CUNDINAMARCA': 'Cundinamarca',
                'HUILA': 'Huila',
                'META': 'Meta',
                'PUTUMAYO': 'Putumayo',
                'RISARALDA': 'Risaralda',
                'SANTANDER': 'Santander',
                'TOLIMA': 'Tolima'
            }};
            return correcciones[nombre] || nombre;
        }}

        document.addEventListener('DOMContentLoaded', function() {{
            renderizarEstadisticas();
            renderizarCategorias();
            renderizarLigas();
            renderizarCategoriaLiga();
            renderizarEdad();
        }});

        function renderizarEstadisticas() {{
            const statsGrid = document.getElementById('statsGrid');
            const totalCategorias = Object.keys(datos.pilotos_por_categoria).length;
            const totalLigas = Object.keys(datos.deportistas_por_liga_total).length;

            statsGrid.innerHTML = `
                <div class="stat-card">
                    <div class="number">${{datos.total_pilotos_unicos}}</div>
                    <div class="label">Licencias Únicas</div>
                </div>
                <div class="stat-card">
                    <div class="number">${{datos.total_participaciones}}</div>
                    <div class="label">Total Participaciones</div>
                </div>
                <div class="stat-card">
                    <div class="number">${{totalCategorias}}</div>
                    <div class="label">Categorías</div>
                </div>
                <div class="stat-card">
                    <div class="number">${{totalLigas}}</div>
                    <div class="label">Ligas</div>
                </div>
            `;
        }}

        function renderizarCategorias() {{
            const chart = document.getElementById('categoriaChart');
            const categorias = Object.entries(datos.pilotos_por_categoria)
                .sort((a, b) => b[1] - a[1]);

            const maxValue = Math.max(...categorias.map(([, v]) => v), 1);

            chart.innerHTML = categorias.map(([categoria, cantidad]) => {{
                const porcentaje = (cantidad / maxValue) * 100;
                return `
                    <div class="bar-item">
                        <div class="bar-label">${{categoria}}</div>
                        <div class="bar-wrapper">
                            <div class="bar-fill" style="width: ${{porcentaje}}%">
                                ${{cantidad}}
                            </div>
                        </div>
                    </div>
                `;
            }}).join('');
        }}

        function renderizarLigas() {{
            const chart = document.getElementById('ligasChart');
            let ligas = Object.entries(datos.deportistas_por_liga_total);
            let sortBy = 'cantidad-desc';

            function aplicarFiltros() {{
                const search = document.getElementById('searchLiga').value.toLowerCase();
                sortBy = document.getElementById('filterSortLiga').value;

                let ligasFiltradas = ligas.filter(([liga]) => {{
                    const ligaCorregida = corregirOrtografiaDepartamento(liga);
                    return ligaCorregida.toLowerCase().includes(search) || liga.toLowerCase().includes(search);
                }});

                ligasFiltradas.sort((a, b) => {{
                    switch(sortBy) {{
                        case 'cantidad-desc':
                            return b[1] - a[1];
                        case 'cantidad-asc':
                            return a[1] - b[1];
                        case 'nombre-asc':
                            return a[0].localeCompare(b[0]);
                        case 'nombre-desc':
                            return b[0].localeCompare(a[0]);
                        default:
                            return b[1] - a[1];
                    }}
                }});

                const maxValue = Math.max(...ligasFiltradas.map(([, v]) => v), 1);

                chart.innerHTML = ligasFiltradas.map(([liga, cantidad]) => {{
                    const porcentaje = (cantidad / maxValue) * 100;
                    const ligaCorregida = corregirOrtografiaDepartamento(liga);
                    return `
                        <div class="bar-item">
                            <div class="bar-label">${{ligaCorregida}}</div>
                            <div class="bar-wrapper">
                                <div class="bar-fill" style="width: ${{porcentaje}}%">
                                    ${{cantidad}}
                                </div>
                            </div>
                        </div>
                    `;
                }}).join('');
            }}

            document.getElementById('searchLiga').addEventListener('input', aplicarFiltros);
            document.getElementById('filterSortLiga').addEventListener('change', aplicarFiltros);
            aplicarFiltros();
        }}

        function renderizarCategoriaLiga() {{
            const container = document.getElementById('todasCategoriasLigaCharts');
            const filtroSelect = document.getElementById('filtroCategoriaLiga');
            const categorias = Object.keys(datos.deportistas_por_liga_categoria).sort();

            // Llenar el selector con todas las categorías
            filtroSelect.innerHTML = '<option value="todas">Todas</option>' +
                categorias.map(cat => 
                    `<option value="${{cat}}">${{cat}}</option>`
                ).join('');

            function mostrarGraficas(categoriaFiltro) {{
                const categoriasAMostrar = categoriaFiltro === 'todas' 
                    ? categorias 
                    : [categoriaFiltro];

                container.innerHTML = categoriasAMostrar.map(categoria => {{
                    const ligas = Object.entries(datos.deportistas_por_liga_categoria[categoria] || {{}})
                        .sort((a, b) => b[1] - a[1]);

                    if (ligas.length === 0) {{
                        return '';
                    }}

                    const maxValue = Math.max(...ligas.map(([, v]) => v), 1);
                    const maxHeight = 200; // Altura máxima de las columnas

                    const chartHTML = ligas.map(([liga, cantidad]) => {{
                        const altura = (cantidad / maxValue) * maxHeight;
                        const ligaCorregida = corregirOrtografiaDepartamento(liga);
                        return `
                            <div class="column-item">
                                <div class="column-wrapper">
                                    <div class="column-fill" style="height: ${{altura}}px">
                                        ${{cantidad}}
                                    </div>
                                </div>
                                <div class="column-label">${{ligaCorregida}}</div>
                            </div>
                        `;
                    }}).join('');

                    return `
                        <div style="margin-bottom: 40px;">
                            <h3 style="color: #123E92; margin-bottom: 20px; font-size: 1.3em; padding-bottom: 10px; border-bottom: 2px solid #F7C31D;">${{categoria}}</h3>
                            <div class="chart-container">
                                <div class="column-chart">
                                    ${{chartHTML}}
                                </div>
                            </div>
                        </div>
                    `;
                }}).join('');
            }}

            // Mostrar todas por defecto
            mostrarGraficas('todas');

            // Event listener para el filtro
            filtroSelect.addEventListener('change', function() {{
                mostrarGraficas(this.value);
            }});
        }}

        function renderizarEdad() {{
            const chart = document.getElementById('edadChart');
            const edades = Object.entries(datos.participaciones_por_edad || {{}});
            
            if (edades.length === 0) {{
                chart.innerHTML = '<p style="text-align: center; padding: 40px; color: #666;">No hay datos de edad disponibles</p>';
                return;
            }}

            // Ordenar por orden de edad (rango de 5 años, empezando desde 1-5)
            const ordenEdades = [
                "0 años", "1-5 años", "6-10 años", "11-15 años", "16-20 años", 
                "21-25 años", "26-30 años", "31-35 años", "36-40 años",
                "41-45 años", "46-50 años", "51-55 años", "56-60 años",
                "61-65 años", "66+ años"
            ];
            
            edades.sort((a, b) => {{
                const idxA = ordenEdades.indexOf(a[0]);
                const idxB = ordenEdades.indexOf(b[0]);
                if (idxA === -1 && idxB === -1) return a[0].localeCompare(b[0]);
                if (idxA === -1) return 1;
                if (idxB === -1) return -1;
                return idxA - idxB;
            }});

            const maxValue = Math.max(...edades.map(([, v]) => v), 1);
            const maxHeight = 250;

            chart.innerHTML = edades.map(([rango, cantidad]) => {{
                const altura = (cantidad / maxValue) * maxHeight;
                return `
                    <div class="column-item">
                        <div class="column-wrapper">
                            <div class="column-fill" style="height: ${{altura}}px">
                                ${{cantidad}}
                            </div>
                        </div>
                        <div class="column-label">${{rango}}</div>
                    </div>
                `;
            }}).join('');
        }}

        // Marcar el enlace activo basándose en la URL actual
        document.addEventListener('DOMContentLoaded', function() {{
            const currentPath = window.location.pathname;
            const currentHref = window.location.href;
            const menuLinks = document.querySelectorAll('.nav-menu a, .dropdown-menu a');
            
            menuLinks.forEach(link => {{
                const linkHref = link.getAttribute('href');
                if (linkHref && linkHref !== '#') {{
                    // Obtener el nombre del archivo actual
                    const currentFileName = currentHref.split('/').pop() || currentHref.split('\\\\').pop();
                    const linkFileName = linkHref.split('/').pop() || linkHref.split('\\\\').pop();
                    
                    // Comparar nombres de archivo
                    if (linkFileName && currentFileName && linkFileName === currentFileName) {{
                        link.classList.add('active');
                        const dropdown = link.closest('.dropdown');
                        if (dropdown) {{
                            dropdown.classList.add('active');
                        }}
                    }} else if (linkHref.includes(currentFileName) || currentHref.includes(linkFileName)) {{
                        link.classList.add('active');
                        const dropdown = link.closest('.dropdown');
                        if (dropdown) {{
                            dropdown.classList.add('active');
                        }}
                    }}
                }}
            }});
        }});

        // Manejar clics en menús desplegables para móviles
        document.addEventListener('DOMContentLoaded', function() {{
            const dropdowns = document.querySelectorAll('.dropdown > a');

            dropdowns.forEach(dropdown => {{
                dropdown.addEventListener('click', function(e) {{
                    if (window.innerWidth <= 768) {{
                        e.preventDefault();
                        const parent = this.parentElement;
                        const isActive = parent.classList.contains('active');

                        document.querySelectorAll('.dropdown').forEach(d => {{
                            if (d !== parent) {{
                                d.classList.remove('active');
                            }}
                        }});

                        if (isActive) {{
                            parent.classList.remove('active');
                        }} else {{
                            parent.classList.add('active');
                        }}
                    }}
                }});
            }});

            // Cerrar dropdowns al hacer clic fuera
            document.addEventListener('click', function(e) {{
                if (!e.target.closest('.dropdown')) {{
                    document.querySelectorAll('.dropdown').forEach(d => {{
                        d.classList.remove('active');
                    }});
                }}
            }});
        }});

        // Función para descargar el informe como PDF
        document.getElementById('descargarPDF').addEventListener('click', function() {{
            const button = this;
            const buttonContainer = button.parentElement;
            const originalText = button.innerHTML;
            
            // Mostrar modal de carga con SweetAlert
            Swal.fire({{
                title: 'Generando PDF',
                html: 'Por favor espere mientras se genera el documento...',
                allowOutsideClick: false,
                allowEscapeKey: false,
                showConfirmButton: false,
                didOpen: () => {{
                    Swal.showLoading();
                }}
            }});

            // Deshabilitar el botón pero mantenerlo visible
            button.disabled = true;
            button.style.opacity = '0.7';
            button.style.cursor = 'not-allowed';
            button.innerHTML = '⏳ Generando PDF...';

            // Ocultar el contenedor del botón temporalmente para que no aparezca en el PDF
            const originalDisplay = buttonContainer.style.display;
            buttonContainer.style.display = 'none';

            // Capturar el contenido del contenedor principal
            const element = document.querySelector('.container');
            
            html2canvas(element, {{
                scale: 2,
                useCORS: true,
                logging: false,
                backgroundColor: '#ffffff',
                windowWidth: element.scrollWidth,
                windowHeight: element.scrollHeight
            }}).then(canvas => {{
                const imgData = canvas.toDataURL('image/png');
                const {{ jsPDF }} = window.jspdf;
                const pdf = new jsPDF('p', 'mm', 'a4');
                
                const imgWidth = 210; // Ancho A4 en mm
                const pageHeight = 297; // Alto A4 en mm
                const imgHeight = (canvas.height * imgWidth) / canvas.width;
                let heightLeft = imgHeight;
                let position = 0;

                // Agregar primera página
                pdf.addImage(imgData, 'PNG', 0, position, imgWidth, imgHeight);
                heightLeft -= pageHeight;

                // Agregar páginas adicionales si el contenido es más largo que una página
                while (heightLeft >= 0) {{
                    position = heightLeft - imgHeight;
                    pdf.addPage();
                    pdf.addImage(imgData, 'PNG', 0, position, imgWidth, imgHeight);
                    heightLeft -= pageHeight;
                }}

                // Descargar el PDF
                const nombreArchivo = '{nombre_valida.replace("/", "_").replace(" ", "_")}_informe.pdf';
                pdf.save(nombreArchivo);

                // Cerrar el modal y mostrar éxito
                Swal.fire({{
                    icon: 'success',
                    title: 'PDF generado',
                    text: 'El informe se ha descargado correctamente',
                    confirmButtonColor: '#123E92',
                    timer: 2000,
                    timerProgressBar: true
                }});

                // Restaurar el contenedor del botón (siempre centrado)
                buttonContainer.style.display = originalDisplay || 'block';
                button.innerHTML = originalText;
                button.disabled = false;
                button.style.opacity = '1';
                button.style.cursor = 'pointer';
            }}).catch(error => {{
                console.error('Error al generar PDF:', error);
                Swal.fire({{
                    icon: 'error',
                    title: 'Error',
                    text: 'No se pudo generar el PDF. Por favor, intente nuevamente.',
                    confirmButtonColor: '#123E92'
                }});
                buttonContainer.style.display = originalDisplay || 'block';
                button.innerHTML = originalText;
                button.disabled = false;
                button.style.opacity = '1';
                button.style.cursor = 'pointer';
            }});
        }});
    </script>
</body>
</html>
'''

# Guardar el HTML
# Escribir el HTML con encoding UTF-8
try:
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
except Exception as e:
    print(f"Error al escribir el archivo HTML: {e}")
    sys.exit(1)

print(f"HTML generado en: {output_path}")

# Función para agregar el enlace al nuevo informe en todos los menús HTML
def agregar_enlace_a_menus(output_html_path, nombre_valida):
    """
    Busca todos los archivos HTML y agrega el enlace al nuevo informe en el menú correspondiente.
    """
    # Obtener el nombre del archivo HTML generado
    nombre_archivo_html = os.path.basename(output_html_path)
    
    # Obtener la ruta relativa desde la raíz del proyecto
    # output_html_path es relativo a Informes/, necesitamos la ruta completa
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    
    # Buscar todos los archivos HTML en el proyecto
    html_files = []
    for root, dirs, files in os.walk(project_root):
        # Excluir node_modules y otros directorios no relevantes
        dirs[:] = [d for d in dirs if d not in ['.git', 'node_modules', '__pycache__']]
        for file in files:
            if file.endswith('.html'):
                html_files.append(os.path.join(root, file))
    
    # Determinar la ruta relativa del nuevo informe desde cada HTML
    # output_html_path es relativo a Informes/, construir la ruta completa
    output_dir = os.path.dirname(output_html_path)
    output_file_full = os.path.join(script_dir, output_html_path) if output_html_path else script_dir
    
    for html_file in html_files:
        try:
            # Leer el archivo HTML
            with open(html_file, 'r', encoding='utf-8') as f:
                contenido = f.read()
            
            # Calcular la ruta relativa desde este HTML al nuevo informe
            html_dir = os.path.dirname(html_file)
            try:
                # Calcular ruta relativa desde el HTML hasta el archivo del informe
                ruta_relativa = os.path.relpath(output_file_full, html_dir).replace('\\', '/')
                
                # Corregir si hay "Informes/Informes" duplicado
                if 'Informes/Informes' in ruta_relativa:
                    ruta_relativa = ruta_relativa.replace('Informes/Informes', 'Informes')
                
                # Si la ruta relativa es muy larga o incorrecta, construir desde output_html_path
                # output_html_path es relativo a Informes/, así que desde la raíz sería "Informes/" + output_html_path
                if html_file == os.path.join(project_root, 'index.html'):
                    # Desde index.html (raíz), la ruta es "Informes/" + output_html_path
                    ruta_relativa = f"Informes/{output_html_path}".replace('\\', '/')
                elif 'Informes' in os.path.relpath(html_file, project_root):
                    # Si el HTML está dentro de Informes/, calcular relativa normalmente
                    pass  # Ya calculada arriba
                else:
                    # Si está en otro lugar, usar la ruta desde la raíz
                    ruta_relativa = f"Informes/{output_html_path}".replace('\\', '/')
            except Exception as e:
                # Si no se puede calcular, construir desde output_html_path
                if html_file == os.path.join(project_root, 'index.html'):
                    ruta_relativa = f"Informes/{output_html_path}".replace('\\', '/')
                else:
                    ruta_relativa = output_html_path.replace('\\', '/')
            
            # Buscar el menú "Modalidad de ejemplo" dentro del dropdown "Informes"
            # Patrón: buscar <li class="dropdown"><a href="#">Modalidad de ejemplo</a><ul class="dropdown-menu">
            patron_modalidad = r'(<li class="dropdown">\s*<a href="#">Modalidad de ejemplo</a>\s*<ul class="dropdown-menu">)'
            
            # Verificar si el enlace ya existe
            if nombre_archivo_html in contenido:
                continue  # Ya existe, no agregar de nuevo
            
            # Buscar el patrón completo del dropdown "Modalidad de ejemplo" con su contenido
            # Necesitamos encontrar desde <li class="dropdown"> hasta el </ul></li> de cierre
            patron_completo = r'(<li class="dropdown">\s*<a href="#">Modalidad de ejemplo</a>\s*<ul class="dropdown-menu">)(.*?)(</ul>\s*</li>)'
            
            def agregar_enlace(match):
                inicio = match.group(1)
                contenido_menu = match.group(2)
                cierre = match.group(3)
                
                # Verificar si el enlace ya existe en el contenido
                if nombre_archivo_html in contenido_menu:
                    return match.group(0)  # Ya existe, no modificar
                
                # Agregar el nuevo enlace al final del contenido del menú, antes del cierre
                nuevo_item = f'                                    <li><a href="{ruta_relativa}">{nombre_valida}</a></li>'
                return inicio + contenido_menu + '\n' + nuevo_item + '\n                                ' + cierre
            
            # Intentar agregar el enlace
            nuevo_contenido = re.sub(
                patron_completo,
                agregar_enlace,
                contenido,
                flags=re.IGNORECASE | re.DOTALL
            )
            
            # Si se hizo algún cambio, escribir el archivo
            if nuevo_contenido != contenido:
                with open(html_file, 'w', encoding='utf-8') as f:
                    f.write(nuevo_contenido)
                print(f"  [OK] Enlace agregado en: {os.path.relpath(html_file, project_root)}")
        
        except Exception as e:
            print(f"  [ADVERTENCIA] No se pudo actualizar {os.path.relpath(html_file, project_root)}: {e}")

# Agregar el enlace al nuevo informe en todos los menús HTML
print("\nActualizando menús en todos los archivos HTML...")
agregar_enlace_a_menus(output_path, nombre_valida)

# Eliminar el archivo JSON después de generar el HTML
try:
    os.remove(json_path)
    print(f"\nArchivo JSON eliminado: {json_path}")
except Exception as e:
    print(f"Advertencia: No se pudo eliminar el archivo JSON {json_path}: {e}")

