"""
Script de generación del Informe Oficial de Funciones y Gestión FEDEMOTO 2026.
Incluye análisis comparativo: Modelo Tradicional 2025 vs. Ecosistema Tecnológico 2026.
Responsable: Mauricio Sánchez Aguilar - Jefe de Cronometraje FEDEMOTO.
"""

import os
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, HRFlowable, Image
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas

# Colores Institucionales FEDEMOTO
PRIMARY = colors.HexColor("#123E92")      # Azul Institucional
PRIMARY_DARK = colors.HexColor("#0A235C") # Azul Marino Profundo
PRIMARY_LIGHT = colors.HexColor("#EBF2FF")# Fondo suave azul
ACCENT = colors.HexColor("#F7C31D")       # Amarillo / Dorado FEDEMOTO
ACCENT_DARK = colors.HexColor("#D97706")  # Ámbar oscuro
TEXT_DARK = colors.HexColor("#1E293B")    # Texto principal pizarra
TEXT_MUTED = colors.HexColor("#64748B")   # Texto secundario gris
BORDER_COLOR = colors.HexColor("#CBD5E1") # Bordes suaves
SURFACE_BG = colors.HexColor("#F8FAFC")   # Fondo tarjetas
SUCCESS = colors.HexColor("#15803D")      # Verde éxito
WARNING_RED = colors.HexColor("#B91C1C")  # Rojo advertencia


class NumberedCanvas(canvas.Canvas):
    """Canvas para numeración dinámica de páginas 'Página X de Y' y membrete elegante."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_elements(num_pages)
            super().showPage()
        super().save()

    def draw_page_elements(self, page_count):
        self.saveState()
        
        # Membrete superior (páginas 2 en adelante)
        if self._pageNumber > 1:
            self.setFillColor(PRIMARY)
            self.rect(36, 11 * inch - 32, 8.5 * inch - 72, 3, fill=True, stroke=False)
            
            self.setFont("Helvetica-Bold", 8)
            self.setFillColor(PRIMARY_DARK)
            self.drawString(36, 11 * inch - 26, "FEDERACIÓN COLOMBIANA DE MOTOCICLISMO — FEDEMOTO")
            
            self.setFont("Helvetica", 8)
            self.setFillColor(TEXT_MUTED)
            self.drawRightString(8.5 * inch - 36, 11 * inch - 26, "Informe Oficial de Gestión y Funciones 2026")

        # Pie de página en todas las páginas
        self.setStrokeColor(BORDER_COLOR)
        self.setLineWidth(0.75)
        self.line(36, 38, 8.5 * inch - 36, 38)

        self.setFont("Helvetica-Bold", 7.5)
        self.setFillColor(PRIMARY)
        self.drawString(36, 26, "MAURICIO SÁNCHEZ AGUILAR")
        self.setFont("Helvetica", 7.5)
        self.setFillColor(TEXT_MUTED)
        self.drawString(185, 26, "|   Jefe de Cronometraje FEDEMOTO   |   Uso Oficial e Institucional")

        page_str = f"Página {self._pageNumber} de {page_count}"
        self.drawRightString(8.5 * inch - 36, 26, page_str)
        
        self.restoreState()


def create_report(output_pdf="Informe_Gestion_Funciones_2026_Mauricio_Sanchez.pdf"):
    doc = SimpleDocTemplate(
        output_pdf,
        pagesize=letter,
        leftMargin=36,
        rightMargin=36,
        topMargin=42,
        bottomMargin=46
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "CoverTitle",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=20,
        leading=24,
        textColor=PRIMARY_DARK,
        spaceAfter=6
    )

    subtitle_style = ParagraphStyle(
        "CoverSubtitle",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=10.5,
        leading=14.5,
        textColor=TEXT_MUTED,
        spaceAfter=12
    )

    h1_style = ParagraphStyle(
        "Heading1_Custom",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=12.5,
        leading=16,
        textColor=PRIMARY,
        spaceBefore=11,
        spaceAfter=5,
        keepWithNext=True
    )

    body_style = ParagraphStyle(
        "Body_Custom",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=8.5,
        leading=11.8,
        textColor=TEXT_DARK,
        spaceAfter=4
    )

    body_bold = ParagraphStyle(
        "Body_Bold",
        parent=body_style,
        fontName="Helvetica-Bold"
    )

    body_white = ParagraphStyle(
        "Body_White",
        parent=body_style,
        textColor=colors.white
    )

    body_white_bold = ParagraphStyle(
        "Body_White_Bold",
        parent=body_bold,
        textColor=colors.white
    )

    callout_style = ParagraphStyle(
        "Callout_Text",
        parent=styles["Normal"],
        fontName="Helvetica-Oblique",
        fontSize=8.4,
        leading=11.8,
        textColor=PRIMARY_DARK
    )

    kpi_num_style = ParagraphStyle(
        "KpiNum",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=17,
        leading=19,
        textColor=PRIMARY,
        alignment=1
    )

    kpi_lbl_style = ParagraphStyle(
        "KpiLbl",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=6.8,
        leading=8.5,
        textColor=TEXT_MUTED,
        alignment=1
    )

    story = []

    # ========================== PORTADA / ENCABEZADO ==========================
    logo_path = os.path.abspath("fedemoto-logo.png")
    # Mantener relación de aspecto cuadrada 1:1 original (60x60 pt) para que no se vea espichado
    logo_img = Image(logo_path, width=0.88 * inch, height=0.88 * inch) if os.path.exists(logo_path) else Paragraph("<b>FEDEMOTO</b>", h1_style)

    header_table_data = [
        [
            logo_img,
            [
                Paragraph("<b>FEDERACIÓN COLOMBIANA DE MOTOCICLISMO — FEDEMOTO</b>", ParagraphStyle("FedemotoHeader", parent=body_style, fontName="Helvetica-Bold", fontSize=9, textColor=PRIMARY, leading=12)),
                Paragraph("COMISIÓN DE JUZGAMIENTO", ParagraphStyle("SubHeader", parent=body_style, fontName="Helvetica-Bold", fontSize=7.8, textColor=ACCENT_DARK, leading=10)),
                Paragraph("INFORME OFICIAL DE GESTIÓN, RESPONSABILIDADES Y DESARROLLO TÉCNICO · VIGENCIA 2026", ParagraphStyle("SubHeader2", parent=body_style, fontName="Helvetica", fontSize=7.5, textColor=TEXT_MUTED, leading=10)),
            ]
        ]
    ]
    t_header = Table(header_table_data, colWidths=[1.1 * inch, 6.4 * inch])
    t_header.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ALIGN', (0, 0), (0, 0), 'LEFT'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('TOPPADDING', (0, 0), (-1, -1), 0),
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
    ]))
    story.append(t_header)

    story.append(HRFlowable(width="100%", thickness=2, color=PRIMARY, spaceBefore=4, spaceAfter=8))

    story.append(Paragraph("Informe Integral de Gestión y Funciones 2026", title_style))
    story.append(Paragraph(
        "<b>Responsable:</b> Mauricio Sánchez Aguilar &nbsp;|&nbsp; <b>Cargo:</b> Jefe de Cronometraje FEDEMOTO<br/>"
        "<b>Ámbito:</b> Dirección Técnica de Tiempos, Soporte Nacional a Ligas, Auditoría de Pólizas, Operaciones y Transformación Digital",
        subtitle_style
    ))

    # Tarjetas de Impacto Macro 2026
    kpi_cards = [
        [
            Paragraph("1.048", kpi_num_style),
            Paragraph("4.073", kpi_num_style),
            Paragraph("25", kpi_num_style),
            Paragraph("8", kpi_num_style),
            Paragraph("16 / 91", kpi_num_style),
            Paragraph("23", kpi_num_style)
        ],
        [
            Paragraph("PILOTOS ÚNICOS GESTIONADOS", kpi_lbl_style),
            Paragraph("SALIDAS A GRILLA AUDITADAS", kpi_lbl_style),
            Paragraph("VÁLIDAS NACIONALES ATENDIDAS", kpi_lbl_style),
            Paragraph("CAMPEONATOS OFICIALES", kpi_lbl_style),
            Paragraph("LIGAS / CLUBES ATENDIDOS", kpi_lbl_style),
            Paragraph("MARCAS FABRICANTES EN PISTA", kpi_lbl_style)
        ]
    ]
    t_kpis = Table(kpi_cards, colWidths=[1.25 * inch] * 6)
    t_kpis.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), PRIMARY_LIGHT),
        ('BOX', (0, 0), (-1, -1), 1, BORDER_COLOR),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, BORDER_COLOR),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    story.append(t_kpis)
    story.append(Spacer(1, 8))

    # ========================== SECCIÓN 1: RESUMEN EJECUTIVO ==========================
    story.append(Paragraph("1. Resumen Ejecutivo y Alcance del Rol", h1_style))
    story.append(Paragraph(
        "El presente informe consolida formalmente las funciones operativas, desarrollos tecnológicos y procesos de soporte técnico ejecutados por <b>Mauricio Sánchez Aguilar</b> como <b>Jefe de Cronometraje de la Federación Colombiana de Motociclismo (FEDEMOTO)</b> en la temporada oficial 2026. "
        "La gestión del área abarca una cadena de valor integral y crítica para la Federación: aseguramiento y control de pólizas médicas de accidentes, parametrización de eventos en software oficial (Mylaps Orbits 5), atención continua casi 24/7 a las ligas departamentales, soporte remoto en tiempo real a cronometristas en pista, y el desarrollo de un ecosistema web propio que transformó radicalmente la captura, procesamiento, publicación y análisis de resultados del motociclismo nacional.",
        body_style
    ))
    story.append(Spacer(1, 4))

    # ========================== SECCIÓN 2: COMPARATIVO 2025 VS 2026 ==========================
    story.append(Paragraph("2. Transformación Histórica: Modelo Tradicional 2025 vs. Ecosistema Digital 2026", h1_style))
    story.append(Paragraph(
        "Uno de los mayores aportes a FEDEMOTO ha sido el salto cualitativo en la gestión de la información. Hasta la temporada 2025, el manejo de resultados dependía de carpetas desconectadas en Google Drive (<i>'G:\\Mi unidad\\Resultados\\2025'</i>), archivos aislados en Excel/PDF por válida y un reporte general en hojas de cálculo susceptible a errores manuales, <b>sin presencia en página web institucional</b>. En 2026, mediante desarrollo propio de ingeniería de software, se construyó una plataforma web federativa moderna, interactiva y automatizada:",
        body_style
    ))

    t_comp_data = [
        [
            Paragraph("<b>Eje de Gestión</b>", body_white_bold),
            Paragraph("<b>Modelo Anterior (Temporada 2025)</b>", body_white_bold),
            Paragraph("<b>Ecosistema Desarrollado (Temporada 2026)</b>", body_white_bold),
            Paragraph("<b>Impacto Federativo</b>", body_white_bold)
        ],
        [
            Paragraph("<b>Publicación y Acceso al Público</b>", body_style),
            Paragraph("<b>Sin página web.</b> La información reposaba en carpetas internas de Drive. La difusión dependía del envío de PDFs sueltos por correo o WhatsApp.", body_style),
            Paragraph("<b>Portal Web Institucional Oficial.</b> Plataforma web estructurada con menú interactivo por modalidad, semestre y válida con responsive móvil.", body_style),
            Paragraph("Acceso público instantáneo, transparencia e institucionalidad.", body_style)
        ],
        [
            Paragraph("<b>Tiempos Vuelta a Vuelta (Laptimes)</b>", body_style),
            Paragraph("Archivos PDF individuales aislados (<i>'Laptimes.pdf'</i>) difíciles de consultar y desvinculados de la clasificación final.", body_style),
            Paragraph("<b>Visor interactivo integrado en web</b> con botón 'Ver vuelta a vuelta' por serie y manga de competencia.", body_style),
            Paragraph("Experiencia moderna para pilotos, preparadores y prensa.", body_style)
        ],
        [
            Paragraph("<b>Clasificaciones Acumuladas</b>", body_style),
            Paragraph("Hojas de cálculo en Excel (<i>'REPORTE GENERAL 2025.xlsx'</i>) con fórmulas manuales y digitación susceptible a inconsistencias.", body_style),
            Paragraph("<b>Motor algorítmico automatizado:</b> acumulación exacta, criterios de desempate y bono reglamentario de 8 pts sin error humano.", body_style),
            Paragraph("Cero discrepancias en podiums y campeones oficiales.", body_style)
        ],
        [
            Paragraph("<b>Calidad y Metadatos (Moto, Liga, Club)</b>", body_style),
            Paragraph("Múltiples celdas en blanco o nombres no homologados entre mangas clasificatorias y finales.", body_style),
            Paragraph("<b>Algoritmo de cruce automático:</b> normalización entre sesiones que garantiza datos completos de moto, liga y club.", body_style),
            Paragraph("Registros depurados y listos para aval de comisarios.", body_style)
        ],
        [
            Paragraph("<b>Exportación Oficial de Resultados</b>", body_style),
            Paragraph("Impresión o exportación genérica desde Orbits sin adaptación al formato corporativo federativo.", body_style),
            Paragraph("<b>Módulo de exportación a PDF vectorial estilo Excel</b> con escudo FEDEMOTO integrado directamente en la web.", body_style),
            Paragraph("Planillas listas para firma formal de comisarios y archivo.", body_style)
        ],
        [
            Paragraph("<b>Analítica y Estadísticas</b>", body_style),
            Paragraph("Inexistente o limitada a tablas estáticas de participación sin cruces deportivos ni comerciales.", body_style),
            Paragraph("<b>Informe Estadístico Anual y por Válida:</b> análisis de estacionalidad (1S vs 2S), polivalencia, marcas (OEM) y sedes.", body_style),
            Paragraph("Herramienta comercial ante patrocinadores y alcaldías.", body_style)
        ],
        [
            Paragraph("<b>Reglamentos Particulares (RP)</b>", body_style),
            Paragraph("PDFs archivados en carpetas locales sin sincronización con los resultados ni difusión centralizada.", body_style),
            Paragraph("<b>Sincronizador automático:</b> indexación y enlace directo de los PDFs de RP en el menú oficial de navegación.", body_style),
            Paragraph("Acceso normativo inmediato para delegados y jueces.", body_style)
        ]
    ]
    t_comp = Table(t_comp_data, colWidths=[1.4 * inch, 2.2 * inch, 2.4 * inch, 1.5 * inch])
    t_comp.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), PRIMARY),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, 0), 'LEFT'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, SURFACE_BG]),
        ('GRID', (0, 0), (-1, -1), 0.5, BORDER_COLOR),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))
    for r in range(1):
        for c in range(4):
            t_comp_data[r][c].style = body_white_bold
    story.append(t_comp)
    story.append(Spacer(1, 8))

    # ========================== SECCIÓN 3: PREPARACIÓN Y CONFIGURACIÓN ORBITS ==========================
    story.append(Paragraph("3. Planificación, Creación de Eventos y Parametrización en Orbits 5", h1_style))
    story.append(Paragraph(
        "Para cada una de las <b>25 válidas nacionales</b> disputadas en 2026 (Motocross, Velocidad, Velotierra, Enduro y GP Colombia), se ejecuta un protocolo técnico indispensable en software oficial Mylaps Orbits 5:",
        body_style
    ))

    t_orbits_data = [
        [
            Paragraph("<b>Procedimiento Técnico</b>", body_white_bold),
            Paragraph("<b>Descripción del Procedimiento Operativo</b>", body_white_bold),
            Paragraph("<b>Impacto / Garantía</b>", body_white_bold)
        ],
        [
            Paragraph("<b>Configuración en Orbits 5</b>", body_style),
            Paragraph("Apertura del evento en Orbits 5: configuración de fechas, sede, modalidad, tipo de transponder (TX) y parámetros de detección.", body_style),
            Paragraph("Estandarización requerida para iniciar cronometraje.", body_style)
        ],
        [
            Paragraph("<b>Grupos y Carreras</b>", body_style),
            Paragraph("Creación de categorías, mangas de entrenamientos, series clasificatorias y mangas finales conforme al Reglamento Particular (RP).", body_style),
            Paragraph("Prevención de errores de grilla o cruces de categorías.", body_style)
        ],
        [
            Paragraph("<b>Entrega de Backup Oficial</b>", body_style),
            Paragraph("Generación, empaquetado y entrega anticipada del archivo de respaldo (backup) preconfigurado al cronometrista asignado.", body_style),
            Paragraph("Operatividad inmediata en pista sin demoras.", body_style)
        ],
        [
            Paragraph("<b>Headers y Footers Oficiales</b>", body_style),
            Paragraph("Diseño gráfico corporativo de encabezados y pies de página utilizados exclusivamente en las planillas de resultados y vuelta a vuelta.", body_style),
            Paragraph("Identidad institucional y uniformidad federativa.", body_style)
        ]
    ]
    t_orbits = Table(t_orbits_data, colWidths=[2.0 * inch, 4.0 * inch, 1.5 * inch])
    t_orbits.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), PRIMARY),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, 0), 'LEFT'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3.5),
        ('TOPPADDING', (0, 0), (-1, -1), 3.5),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, SURFACE_BG]),
        ('GRID', (0, 0), (-1, -1), 0.5, BORDER_COLOR),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))
    for r in range(1):
        for c in range(3):
            t_orbits_data[r][c].style = body_white_bold
    story.append(t_orbits)
    story.append(Spacer(1, 8))

    # ========================== SECCIÓN 4: LOGÍSTICA DE EQUIPOS ==========================
    story.append(Paragraph("4. Gestión Logística y Envío de Equipos de Cronometraje", h1_style))
    callout_equipos = [
        [
            Paragraph(
                "<b>Nota Aclaratoria sobre la Operación Logística:</b><br/>"
                "Hasta hace aproximadamente tres (3) meses, me encargaba de forma presencial del alistamiento físico de los maletines, decodificadores, cables y sensores de cronometraje para cada válida. Por motivos personales informados oportunamente y de común acuerdo con la Federación, dicha labor presencial de empaque en bodega fue asignada a otra persona; no obstante, <b>ha seguido y permanece bajo mi entera responsabilidad la supervisión, coordinación y seguimiento logístico para garantizar que los equipos lleguen completos, a tiempo y en perfecto estado a cada pista del país</b>. De esta función, la única variación fue la no asistencia física al alistamiento, manteniéndose indemne la responsabilidad sobre el cumplimiento logístico integral.",
                callout_style
            )
        ]
    ]
    t_callout_eq = Table(callout_equipos, colWidths=[7.5 * inch])
    t_callout_eq.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), SURFACE_BG),
        ('BOX', (0, 0), (-1, -1), 1, BORDER_COLOR),
        ('LINELEFT', (0, 0), (-1, -1), 3.5, PRIMARY),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(t_callout_eq)
    story.append(Spacer(1, 8))

    # ========================== SECCIÓN 5: AUDITORÍA DE PÓLIZAS ==========================
    story.append(Paragraph("5. Control, Contraste y Auditoría de Pólizas de Seguro de Accidentes", h1_style))
    story.append(Paragraph(
        "Como salvaguarda médica de los deportistas y blindaje jurídico para FEDEMOTO, opera un sistema continuo de auditoría de pólizas pre-competencia:",
        body_style
    ))

    t_polizas_data = [
        [
            Paragraph("<b>Eje de Control</b>", body_white_bold),
            Paragraph("<b>Detalle de la Operación y Metodología</b>", body_white_bold),
            Paragraph("<b>Resultado Obtenido</b>", body_white_bold)
        ],
        [
            Paragraph("<b>Cruce Masivo Pre-Válida<br/>(Inscritos vs. Pólizas)</b>", body_style),
            Paragraph("Contraste sistemático de las planillas de inscripción de cada evento contra las matrices federativas de pólizas vigentes (archivos maestros de pólizas anuales y sus opciones de cobertura OPC 1, OPC 2, OPC 3).", body_style),
            Paragraph("Detección precisa de pilotos sin póliza activa antes de iniciar prácticas.", body_style)
        ],
        [
            Paragraph("<b>Reporte de Pilotos Faltantes</b>", body_style),
            Paragraph("Generación y remisión inmediata a la administración del informe oficial de <i>Pilotos Faltantes de Póliza</i> por válida, categorizando pilotos pendientes por adquirir seguro.", body_style),
            Paragraph("Blindaje legal para FEDEMOTO y cobro oportuno de seguros de evento.", body_style)
        ],
        [
            Paragraph("<b>Auditoría por Documento</b>", body_style),
            Paragraph("Consultas directas por cédula o tarjeta de identidad para verificar el histórico de pólizas, edad, liga y coberturas de pilotos cuestionados en pista.", body_style),
            Paragraph("Resolución inmediata de dudas de inscripción en mesa técnica.", body_style)
        ],
        [
            Paragraph("<b>Protección a Categorías Menores</b>", body_style),
            Paragraph("Verificación rigurosa de seguros para pilotos infantiles y juveniles (categorías formativas: 50cc, 65cc, 85cc, Escuela e Infantil), garantizando estricta cobertura antes de autorizar pista.", body_style),
            Paragraph("Cumplimiento normativo integral con el deporte formativo nacional.", body_style)
        ]
    ]
    t_polizas = Table(t_polizas_data, colWidths=[2.0 * inch, 4.0 * inch, 1.5 * inch])
    t_polizas.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), PRIMARY),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, 0), 'LEFT'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3.5),
        ('TOPPADDING', (0, 0), (-1, -1), 3.5),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, SURFACE_BG]),
        ('GRID', (0, 0), (-1, -1), 0.5, BORDER_COLOR),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))
    for r in range(1):
        for c in range(3):
            t_polizas_data[r][c].style = body_white_bold
    story.append(t_polizas)
    story.append(Spacer(1, 8))

    # ========================== SECCIÓN 6: SOPORTE A LIGAS Y ATENCIÓN 24/7 ==========================
    story.append(Paragraph("6. Acompañamiento Continuo a Ligas, Licenciamiento y Peticiones", h1_style))
    story.append(Paragraph(
        "• <b>Monitoreo y Soporte a Ligas casi 24/7:</b> Atención técnica continua a las <b>16 ligas departamentales</b> durante los periodos ordinarios y extraordinarios de inscripción. Se resuelven incidencias de plataforma, cruces de grilla y validación de nóminas en horarios extendidos (noches y fines de semana previos al evento).<br/>"
        "• <b>Asistencia en Procesos de Licenciamiento:</b> Orientación directa a delegados y pilotos para la expedición, renovación y homologación de licencias nacionales vs. licencias de evento (-E), verificando el cumplimiento de la reglamentación deportiva vigente.<br/>"
        "• <b>Recepción y Resolución de Cartas de Petición:</b> Estudio técnico riguroso de telemetría, pasos por meta, transponders y planillas oficiales para fundamentar y redactar respuestas oficiales a las solicitudes o reclamaciones radicadas ante la Federación.",
        body_style
    ))
    story.append(Spacer(1, 8))

    # ========================== SECCIÓN 7: MESA DE AYUDA Y SOPORTE REMOTO EN PISTA ==========================
    story.append(Paragraph("7. Respaldo Remoto en Tiempo Real al Cronometrista en Pista", h1_style))
    story.append(Paragraph(
        "En aquellas válidas nacionales a las cuales no asisto de manera presencial, establezco una <b>mesa de ayuda y monitoreo remoto permanente durante toda la jornada de competencia</b>:<br/>"
        "1. <b>Disponibilidad permanente:</b> Conexión activa para asistir al cronometrista en pista ante cualquier eventualidad técnica con Orbits o dudas reglamentarias.<br/>"
        "2. <b>Verificación remota de pilotos:</b> Consulta y validación remota en bases de datos para comprobar si pilotos en pista existen en el sistema federativo, cruzar nombres, dorsales o categorías.<br/>"
        "3. <b>Generación remota de resultados de emergencia:</b> Capacidad de procesar y extraer resultados o planillas en remoto en caso de complicaciones locales en el puesto de cronometraje.<br/>"
        "4. <b>Soporte de información y auditoría:</b> Cruce inmediato de información para que comisarios y cronometristas en pista tomen decisiones acertadas y el evento culmine con éxito.",
        body_style
    ))
    story.append(Spacer(1, 8))

    # ========================== SECCIÓN 8: ECOSISTEMA TECNOLÓGICO Y DESARROLLOS ==========================
    story.append(Paragraph("8. Ecosistema Digital Desarrollado para Procesamiento y Publicación", h1_style))
    story.append(Paragraph(
        "Para materializar la modernización de FEDEMOTO, concebí y programé una arquitectura de software propia que automatiza toda la cadena de datos deportivos. "
        "Este ecosistema tecnológico propio cuenta a la fecha con <b>40 scripts de desarrollo y procesamiento en Python (.py)</b>, una red de <b>63 portales web institucionales (.html)</b>, <b>99 enlaces funcionales integrados</b> en el menú oficial de navegación, y módulos de lógica en JavaScript y diseño CSS corporativo:",
        body_style
    ))

    t_dev_data = [
        [
            Paragraph("<b>Módulo Desarrollado</b>", body_white_bold),
            Paragraph("<b>Ingeniería y Funcionamiento del Desarrollo</b>", body_white_bold),
            Paragraph("<b>Beneficio Institucional</b>", body_white_bold)
        ],
        [
            Paragraph("<b>Pipeline de Ingesta y Limpieza de CSVs</b>", body_style),
            Paragraph("Scripts automatizados para extracción, lectura, saneamiento y validación de archivos crudos CSV exportados de Orbits y consolas de tiempo.", body_style),
            Paragraph("Eliminación del error humano y máxima precisión en el procesamiento.", body_style)
        ],
        [
            Paragraph("<b>Cruce y Normalización de Metadatos</b>", body_style),
            Paragraph("Algoritmo de consolidación que cruza sesiones clasificatorias y finales para homologar Moto, Liga y Club, eliminando celdas vacías.", body_style),
            Paragraph("Planillas y tablas 100% completas y profesionales.", body_style)
        ],
        [
            Paragraph("<b>Generador de Páginas Web de Válidas</b>", body_style),
            Paragraph("Generación de portales HTML institucionales por válida con visor de vuelta a vuelta, bloques de mangas y responsive móvil.", body_style),
            Paragraph("Publicación inmediata y transparente para el público.", body_style)
        ],
        [
            Paragraph("<b>Exportador de PDF Vectorial Oficial</b>", body_style),
            Paragraph("Módulo JavaScript en el navegador que convierte la tabla de resultados en un PDF oficial vectorial estilo Excel con logo FEDEMOTO.", body_style),
            Paragraph("Documento legal listo para firma de comisarios.", body_style)
        ],
        [
            Paragraph("<b>Motor de Clasificaciones Generales Acumuladas</b>", body_style),
            Paragraph("Software de acumulación por campeonato: suma de puntos, criterios de desempate, gestión de exclusiones y cálculo del bono de 8 pts.", body_style),
            Paragraph("Tablas de posiciones al día sin discrepancias.", body_style)
        ],
        [
            Paragraph("<b>Sincronizador de Reglamentos (RPs)</b>", body_style),
            Paragraph("Detector automático que analiza nuevos archivos PDF de reglamentos en disco y los indexa con enlaces directos en el menú del portal.", body_style),
            Paragraph("Acceso centralizado e instantáneo a la normativa.", body_style)
        ],
        [
            Paragraph("<b>Informe Estadístico Anual y por Válida</b>", body_style),
            Paragraph("Plataforma analítica con 6 vistas: General, Modalidad, Campeonato, Comparativa 1S vs 2S, Semestre General e Inteligencia Comercial.", body_style),
            Paragraph("Insumo de alto valor deportivo, técnico y comercial.", body_style)
        ]
    ]
    t_dev = Table(t_dev_data, colWidths=[2.0 * inch, 4.0 * inch, 1.5 * inch])
    t_dev.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), PRIMARY),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, 0), 'LEFT'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, SURFACE_BG]),
        ('GRID', (0, 0), (-1, -1), 0.5, BORDER_COLOR),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))
    for r in range(1):
        for c in range(3):
            t_dev_data[r][c].style = body_white_bold
    story.append(t_dev)
    story.append(Spacer(1, 8))

    # ========================== SECCIÓN 9: BALANCE CUANTITATIVO Y CONCLUSIÓN ==========================
    t_resumen_data = [
        [Paragraph("<b>Indicador / Actividad Operativa 2026</b>", body_white_bold), Paragraph("<b>Cantidad / Métrica</b>", body_white_bold), Paragraph("<b>Estado</b>", body_white_bold)],
        [Paragraph("Eventos creados y configurados en Mylaps Orbits 5", body_style), Paragraph("<b>25 eventos</b>", body_style), Paragraph("100% Ejecutado", body_style)],
        [Paragraph("Backups de configuración entregados a cronometristas", body_style), Paragraph("<b>25 respaldos</b>", body_style), Paragraph("100% Ejecutado", body_style)],
        [Paragraph("Headers y Footers institucionales diseñados", body_style), Paragraph("<b>25 paquetes oficiales</b>", body_style), Paragraph("100% Ejecutado", body_style)],
        [Paragraph("Reportes de cruce de pólizas y pilotos faltantes generados", body_style), Paragraph("<b>25 reportes masivos</b>", body_style), Paragraph("100% Auditado", body_style)],
        [Paragraph("Jornadas de soporte remoto en vivo a cronometristas en pista", body_style), Paragraph("<b>Totalidad de válidas no presenciales</b>", body_style), Paragraph("100% Cobertura", body_style)],
        [Paragraph("Ligas departamentales atendidas con soporte continuo", body_style), Paragraph("<b>16 ligas activas</b>", body_style), Paragraph("Atención Permanente", body_style)],
        [Paragraph("Páginas web oficiales construidas y publicadas", body_style), Paragraph("<b>63 portales web interactivos</b>", body_style), Paragraph("En producción", body_style)],
        [Paragraph("Scripts de procesamiento y automatización en Python (.py)", body_style), Paragraph("<b>40 módulos de software propios</b>", body_style), Paragraph("100% Operativo", body_style)],
        [Paragraph("Enlaces activos y estructurados en menú de navegación", body_style), Paragraph("<b>99 accesos directos validados</b>", body_style), Paragraph("En línea", body_style)],
        [Paragraph("Campeonatos acumulados calculados y publicados", body_style), Paragraph("<b>8 campeonatos (6 finalizados / 2 en curso)</b>", body_style), Paragraph("Al día", body_style)],
        [Paragraph("Reglamentos Particulares (RP) integrados en el menú", body_style), Paragraph("<b>25 documentos PDF vinculados</b>", body_style), Paragraph("Sincronizado", body_style)],
        [Paragraph("Pilotos únicos y salidas a grilla auditadas", body_style), Paragraph("<b>1.048 pilotos / 4.073 participaciones</b>", body_style), Paragraph("Récord federativo", body_style)]
    ]
    t_resumen = Table(t_resumen_data, colWidths=[3.8 * inch, 2.3 * inch, 1.4 * inch])
    t_resumen.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), PRIMARY_DARK),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, 0), 'LEFT'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2.8),
        ('TOPPADDING', (0, 0), (-1, -1), 2.8),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, SURFACE_BG]),
        ('GRID', (0, 0), (-1, -1), 0.5, BORDER_COLOR),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    for r in range(1):
        for c in range(3):
            t_resumen_data[r][c].style = body_white_bold

    firma_data = [
        [
            Paragraph("____________________________________________________<br/>"
                      "<b>MAURICIO SÁNCHEZ AGUILAR</b><br/>"
                      "Jefe de Cronometraje<br/>"
                      "Federación Colombiana de Motociclismo — FEDEMOTO<br/>"
                      "<font color='#64748B'>cronometraje@fedemoto.org &nbsp;|&nbsp; Bogotá D.C., Colombia</font>",
                      ParagraphStyle("Firma", parent=body_style, alignment=1))
        ]
    ]
    t_firma = Table(firma_data, colWidths=[7.5 * inch])
    t_firma.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))

    story.append(KeepTogether([
        Paragraph("9. Balance Cuantitativo de Gestión y Conclusiones", h1_style),
        Paragraph(
            "A continuación se resume el volumen operativo y técnico consolidado durante la temporada oficial 2026:",
            body_style
        ),
        t_resumen,
        Spacer(1, 8),
        Paragraph(
            "<b>Conclusión Institucional:</b> La temporada 2026 marca el antes y el después para la Federación Colombiana de Motociclismo. "
            "El paso de un esquema tradicional basado en archivos dispersos de Drive a un ecosistema web centralizado, complementado con auditoría de pólizas, acompañamiento continuo a ligas, alistamiento riguroso en Orbits 5 y respaldo remoto en pista, ha elevado los estándares de transparencia, exactitud deportiva y modernización institucional del deporte a motor en Colombia.",
            body_style
        ),
        Spacer(1, 14),
        t_firma
    ]))

    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"[ÉXITO] Documento PDF oficial generado exitosamente: {output_pdf}")


if __name__ == "__main__":
    create_report()
