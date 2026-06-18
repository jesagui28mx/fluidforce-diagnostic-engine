import streamlit as st
import urllib.parse
from io import BytesIO
from datetime import datetime

from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    Image
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle


# ---------------------------------------------------
# CONFIGURACIÓN GENERAL
# ---------------------------------------------------

st.set_page_config(
    page_title="Water Asset Protection Program",
    page_icon="💧",
    layout="centered"
)

LOGO_PATH = "LOGO_FLUID_FORCE2,3.png"

# CAMBIA ESTE NÚMERO POR EL WHATSAPP REAL
# Formato México: 52 + 1 + número a 10 dígitos
TELEFONO_WHATSAPP = "5215527630274"


# ---------------------------------------------------
# FUNCIONES AUXILIARES
# ---------------------------------------------------

def formato_mxn(valor):
    return f"${valor:,.0f} MXN"


def color_semaforo(nivel_oportunidad):
    if nivel_oportunidad == "ALTO":
        return "#D93025"  # rojo ejecutivo
    if nivel_oportunidad == "MEDIO":
        return "#F9AB00"  # ámbar
    return "#188038"      # verde


def calcular_diagnostico(
    habitaciones,
    ocupacion,
    infraestructura_flags,
    problemas_seleccionados,
    prioridad_operativa,
    energia,
    agua,
    quimicos,
    mantenimiento
):
    costo_total = energia + agua + quimicos + mantenimiento
    costo_anual = costo_total * 12

    # Puntaje por infraestructura crítica
    puntos = 0
    puntos += 2 if infraestructura_flags.get("caldera") else 0
    puntos += 2 if infraestructura_flags.get("hvac") else 0
    puntos += 2 if infraestructura_flags.get("torres") else 0
    puntos += 1 if infraestructura_flags.get("alberca") else 0
    puntos += 1 if infraestructura_flags.get("lavanderia") else 0
    puntos += 1 if infraestructura_flags.get("cocina") else 0
    puntos += 1 if infraestructura_flags.get("ptar") else 0
    puntos += 1 if infraestructura_flags.get("spa") else 0
    puntos += 1 if infraestructura_flags.get("cisterna_cruda") else 0
    puntos += 1 if infraestructura_flags.get("potabilizacion") else 0
    puntos += 1 if infraestructura_flags.get("cisterna_tratada") else 0

    # Puntaje por tamaño y operación
    if habitaciones >= 80:
        puntos += 3
    elif habitaciones >= 40:
        puntos += 2
    else:
        puntos += 1

    if ocupacion >= 75:
        puntos += 2
    elif ocupacion >= 55:
        puntos += 1

    # Puntaje por problemas operativos reportados
    problemas_reales = [p for p in problemas_seleccionados if p != "Ninguno identificado"]
    puntos += min(len(problemas_reales), 6)

    problemas_criticos = [
        "Corrosión, sarro o incrustaciones visibles en tubería, equipamiento y grifería",
        "Rotura de resistencias eléctricas o pérdida de presión en calderas",
        "Intercambiadores con placas, empaques o componentes corroídos",
        "Sobrecalentamiento de compresores en aire acondicionado",
        "Mantenimiento recurrente de bombas o intercambiadores",
        "Consumo elevado de químicos"
    ]

    if any(p in problemas_reales for p in problemas_criticos):
        puntos += 2

    if prioridad_operativa in [
        "Reducir paros operativos costosos",
        "Incrementar vida útil de equipos",
        "Mejorar eficiencia energética"
    ]:
        puntos += 1

    # Semáforo de oportunidad
    if puntos >= 13 or costo_anual >= 2_000_000:
        nivel_oportunidad = "ALTO"
        factor_ahorro = 0.24
        riesgo_min_factor = 0.14
        riesgo_max_factor = 0.28
        prioridad_ff = "Alta"
        mensaje_semaforo = "La operación presenta señales relevantes de pérdida operativa y oportunidad financiera."
    elif puntos >= 8 or costo_anual >= 900_000:
        nivel_oportunidad = "MEDIO"
        factor_ahorro = 0.18
        riesgo_min_factor = 0.09
        riesgo_max_factor = 0.18
        prioridad_ff = "Media"
        mensaje_semaforo = "La operación muestra oportunidades de mejora que conviene validar técnicamente."
    else:
        nivel_oportunidad = "BAJO"
        factor_ahorro = 0.12
        riesgo_min_factor = 0.04
        riesgo_max_factor = 0.10
        prioridad_ff = "Baja"
        mensaje_semaforo = "La oportunidad detectada es preliminar y requiere mayor información operativa."

    ahorro_mensual = costo_total * factor_ahorro
    ahorro_anual = ahorro_mensual * 12
    riesgo_min = costo_anual * riesgo_min_factor
    riesgo_max = costo_anual * riesgo_max_factor

    # Inversión inicial estimada simple MVP
    inversion = habitaciones * 2800

    # Ajustes por infraestructura crítica
    if infraestructura_flags.get("caldera"):
        inversion += 18586
    if infraestructura_flags.get("hvac"):
        inversion += 22029
    if infraestructura_flags.get("torres"):
        inversion += 44058
    if infraestructura_flags.get("alberca"):
        inversion += 18586
    if infraestructura_flags.get("lavanderia"):
        inversion += 18586
    if infraestructura_flags.get("cocina"):
        inversion += 18586
    if infraestructura_flags.get("ptar"):
        inversion += 12599
    if infraestructura_flags.get("spa"):
        inversion += 12599
    if infraestructura_flags.get("cisterna_cruda"):
        inversion += 12599
    if infraestructura_flags.get("potabilizacion"):
        inversion += 18586
    if infraestructura_flags.get("cisterna_tratada"):
        inversion += 12599

    payback = round(inversion / ahorro_mensual, 1) if ahorro_mensual > 0 else 0

    # Nivel recomendado de solución
    nivel = "Protección Básica"
    if habitaciones >= 40 or puntos >= 8:
        nivel = "Optimización Operativa"
    if habitaciones >= 80 or puntos >= 13:
        nivel = "Sistema Integral"

    return {
        "costo_total": costo_total,
        "costo_anual": costo_anual,
        "puntos": puntos,
        "nivel_oportunidad": nivel_oportunidad,
        "mensaje_semaforo": mensaje_semaforo,
        "prioridad_ff": prioridad_ff,
        "factor_ahorro": factor_ahorro,
        "riesgo_min": riesgo_min,
        "riesgo_max": riesgo_max,
        "ahorro_mensual": ahorro_mensual,
        "ahorro_anual": ahorro_anual,
        "inversion": inversion,
        "payback": payback,
        "nivel": nivel,
    }


# ---------------------------------------------------
# FUNCIÓN PDF
# ---------------------------------------------------

def generar_pdf(datos):
    buffer = BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=40,
        leftMargin=40,
        topMargin=35,
        bottomMargin=35
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "TitleFluid",
        parent=styles["Title"],
        fontSize=17,
        textColor=colors.HexColor("#12345A"),
        alignment=1,
        spaceAfter=10
    )

    subtitle_style = ParagraphStyle(
        "SubtitleFluid",
        parent=styles["Heading2"],
        fontSize=12,
        textColor=colors.HexColor("#12345A"),
        spaceAfter=8
    )

    normal_style = ParagraphStyle(
        "NormalFluid",
        parent=styles["Normal"],
        fontSize=9,
        leading=12
    )

    small_style = ParagraphStyle(
        "SmallFluid",
        parent=styles["Normal"],
        fontSize=8,
        leading=10,
        textColor=colors.grey
    )

    story = []

    try:
        logo = Image(LOGO_PATH, width=2.6 * inch, height=1.1 * inch)
        logo.hAlign = "CENTER"
        story.append(logo)
        story.append(Spacer(1, 8))
    except Exception:
        pass

    story.append(Paragraph("Hotel Water Asset Protection Program", title_style))
    story.append(Paragraph("Diagnóstico preliminar de eficiencia hídrica, desempeño operativo y protección de activos", subtitle_style))
    story.append(Spacer(1, 8))

    story.append(Paragraph(
        "Este documento resume una evaluación preliminar basada en la información proporcionada por el prospecto. "
        "Los resultados son estimados y requieren validación técnica especializada.",
        normal_style
    ))

    story.append(Spacer(1, 12))

    # Resumen Ejecutivo
    semaforo_color = color_semaforo(datos["nivel_oportunidad"])
    resumen_data = [
        ["Nivel de oportunidad detectado", datos["nivel_oportunidad"]],
        ["Prioridad recomendada por Fluid Force", datos["prioridad_ff"]],
        ["Riesgo financiero potencial anual", f'{formato_mxn(datos["riesgo_min"])} a {formato_mxn(datos["riesgo_max"])}'],
        ["Ahorro anual potencial", formato_mxn(datos["ahorro_anual"])],
        ["Recuperación estimada", f'{datos["payback"]} meses'],
        ["Nivel recomendado", datos["nivel"]],
    ]

    tabla_resumen = Table(resumen_data, colWidths=[2.8 * inch, 3.7 * inch])
    tabla_resumen.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#EAF2F8")),
        ("TEXTCOLOR", (0, 0), (0, -1), colors.HexColor("#12345A")),
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("BACKGROUND", (1, 0), (1, 0), colors.HexColor(semaforo_color)),
        ("TEXTCOLOR", (1, 0), (1, 0), colors.white),
        ("FONTNAME", (1, 0), (1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("GRID", (0, 0), (-1, -1), 0.3, colors.lightgrey),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("PADDING", (0, 0), (-1, -1), 6),
    ]))

    story.append(Paragraph("Resumen Ejecutivo", subtitle_style))
    story.append(tabla_resumen)
    story.append(Spacer(1, 8))
    story.append(Paragraph(datos["mensaje_semaforo"], normal_style))
    story.append(Spacer(1, 12))

    # Datos contacto
    contacto_data = [
        ["Fecha", datos["fecha"]],
        ["Nombre contacto", datos["contacto_nombre"]],
        ["WhatsApp contacto", datos["contacto_whatsapp"]],
        ["Email contacto", datos["contacto_email"]],
        ["Hotel", datos["hotel_nombre"]],
        ["Ciudad", datos["ciudad"]],
        ["Tipo de hotel", datos["tipo_hotel"]],
        ["Habitaciones", str(datos["habitaciones"])],
        ["Ocupación promedio", f'{datos["ocupacion"]}%'],
    ]

    tabla_contacto = Table(contacto_data, colWidths=[2.1 * inch, 4.4 * inch])
    tabla_contacto.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#EAF2F8")),
        ("TEXTCOLOR", (0, 0), (0, -1), colors.HexColor("#12345A")),
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("GRID", (0, 0), (-1, -1), 0.3, colors.lightgrey),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("PADDING", (0, 0), (-1, -1), 6),
    ]))

    story.append(Paragraph("1. Datos del prospecto", subtitle_style))
    story.append(tabla_contacto)
    story.append(Spacer(1, 12))

    # Infraestructura
    infraestructura_texto = ", ".join(datos["infraestructura"]) if datos["infraestructura"] else "No especificada"

    story.append(Paragraph("2. Infraestructura operativa reportada", subtitle_style))
    story.append(Paragraph(infraestructura_texto, normal_style))
    story.append(Spacer(1, 12))

    # Problemas y prioridad
    problemas_texto = ", ".join(datos["problemas"]) if datos["problemas"] else "No especificados"
    story.append(Paragraph("3. Problemas operativos reportados", subtitle_style))
    story.append(Paragraph(problemas_texto, normal_style))
    story.append(Spacer(1, 6))
    story.append(Paragraph(f'<b>Prioridad operativa del hotel:</b> {datos["prioridad_operativa"]}', normal_style))
    story.append(Spacer(1, 12))

    # Costos
    costos_data = [
        ["Concepto", "Monto mensual estimado"],
        ["Energía", formato_mxn(datos["energia"])],
        ["Agua", formato_mxn(datos["agua"])],
        ["Químicos", formato_mxn(datos["quimicos"])],
        ["Mantenimiento hidráulico", formato_mxn(datos["mantenimiento"])],
        ["Costo operativo analizado", formato_mxn(datos["costo_total"])],
    ]

    tabla_costos = Table(costos_data, colWidths=[3.3 * inch, 3.2 * inch])
    tabla_costos.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#12345A")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("GRID", (0, 0), (-1, -1), 0.3, colors.lightgrey),
        ("PADDING", (0, 0), (-1, -1), 6),
    ]))

    story.append(Paragraph("4. Costos operativos aproximados", subtitle_style))
    story.append(tabla_costos)
    story.append(Spacer(1, 12))

    # Áreas detectadas
    story.append(Paragraph("5. Áreas potenciales de oportunidad", subtitle_style))
    for area in datos["areas"]:
        story.append(Paragraph(f"• {area}", normal_style))

    story.append(Spacer(1, 12))

    story.append(Paragraph("Próximo paso recomendado por Fluid Force", subtitle_style))
    story.append(Paragraph(
        "Validación técnica especializada para confirmar condiciones operativas, validar oportunidades detectadas "
        "y determinar la estrategia de optimización más adecuada para la instalación.",
        normal_style
    ))

    story.append(Spacer(1, 10))

    story.append(Paragraph("Nota importante", subtitle_style))
    story.append(Paragraph(
        "Este diagnóstico no sustituye un levantamiento técnico formal. La selección final de equipos, puntos de instalación, "
        "diámetros, cantidades, inversión definitiva y retorno estimado deben validarse mediante revisión técnica especializada. "
        "Los montos mostrados son estimaciones preliminares sujetas a condiciones operativas reales.",
        small_style
    ))

    story.append(Spacer(1, 8))

    story.append(Paragraph(
        "Para dar seguimiento adecuado, conserve este PDF y adjúntelo al enviarnos su solicitud por WhatsApp.",
        small_style
    ))

    doc.build(story)

    buffer.seek(0)
    return buffer


# ---------------------------------------------------
# HEADER
# ---------------------------------------------------

try:
    st.image(LOGO_PATH, width=320)
except Exception:
    pass

st.title("Water Asset Protection Program")

st.subheader("Hoteles")

st.markdown("""
Evaluación preliminar de eficiencia hídrica, desempeño operativo y protección de activos para instalaciones hoteleras.  
**Tiempo estimado de llenado: 5 minutos**

La operación hidráulica de un hotel impacta directamente los costos energéticos, consumo de insumos químicos, mantenimiento correctivo y vida útil de los equipos.

Descubre posibles áreas de optimización relacionadas con:

- eficiencia térmica
- formación de incrustaciones minerales
- mantenimiento hidráulico
- consumo energético
- uso de químicos
- protección de activos

⚠️ *Los resultados mostrados son estimaciones preliminares y requieren validación técnica especializada.*
""")

st.divider()


# ---------------------------------------------------
# DATOS DE CONTACTO
# ---------------------------------------------------

st.header("1. Datos de Contacto")

contacto_nombre = st.text_input("Nombre de contacto")
contacto_whatsapp = st.text_input("WhatsApp de contacto")
contacto_email = st.text_input("Email de contacto")

st.divider()


# ---------------------------------------------------
# DATOS GENERALES
# ---------------------------------------------------

st.header("2. Perfil del Hotel")

hotel_nombre = st.text_input("Nombre del hotel")
ciudad = st.text_input("Ciudad")

habitaciones = st.number_input(
    "Número de habitaciones",
    min_value=1,
    value=50
)

ocupacion = st.slider(
    "Ocupación promedio (%)",
    0,
    100,
    65
)

tipo_hotel = st.selectbox(
    "Tipo de hotel",
    [
        "Business",
        "Boutique",
        "Resort",
        "Urbano",
        "Mixto / otro"
    ]
)

st.divider()


# ---------------------------------------------------
# INFRAESTRUCTURA
# ---------------------------------------------------

st.header("3. Infraestructura Operativa")
st.caption("Selecciona los sistemas presentes en la operación. No es necesario capturar datos técnicos exactos en esta etapa.")

cisterna_cruda = st.checkbox("Cisterna de agua cruda")
potabilizacion = st.checkbox("Tratamiento / potabilización de agua")
cisterna_tratada = st.checkbox("Cisterna de agua tratada")
caldera = st.checkbox("Calderas o calentadores")
hvac = st.checkbox("HVAC / aire acondicionado")
torres = st.checkbox("Torres de enfriamiento")
alberca = st.checkbox("Alberca")
lavanderia = st.checkbox("Lavandería")
cocina = st.checkbox("Cocina industrial")
ptar = st.checkbox("PTAR")
spa = st.checkbox("Spa / cuarto de vapor")

st.divider()


# ---------------------------------------------------
# COSTOS
# ---------------------------------------------------

st.header("4. Costos Operativos Aproximados")

energia = st.number_input(
    "Gasto mensual energía (MXN)",
    min_value=0,
    value=99000
)

agua = st.number_input(
    "Gasto mensual agua (MXN)",
    min_value=0,
    value=18000
)

quimicos = st.number_input(
    "Gasto mensual químicos (MXN)",
    min_value=0,
    value=25000
)

mantenimiento = st.number_input(
    "Gasto mantenimiento hidráulico (MXN)",
    min_value=0,
    value=30000
)

st.caption("No necesitas cifras exactas. Puedes utilizar estimados aproximados.")

st.divider()


# ---------------------------------------------------
# PROBLEMAS OPERATIVOS
# ---------------------------------------------------

st.header("5. Principales Problemas Operativos")

problemas_opciones = [
    "Corrosión, sarro o incrustaciones visibles en tubería, equipamiento y grifería",
    "Alto consumo energético",
    "Rotura de resistencias eléctricas o pérdida de presión en calderas",
    "Intercambiadores con placas, empaques o componentes corroídos",
    "Sobrecalentamiento de compresores en aire acondicionado",
    "Manchas en cristalería o vajilla",
    "Problemas en lavandería",
    "Desgaste prematuro en resistencias, tanques o válvulas",
    "Mantenimiento recurrente de bombas o intercambiadores",
    "Consumo elevado de químicos",
    "Ninguno identificado"
]

problemas = st.multiselect(
    "Seleccione los problemas que actualmente enfrenta su operación",
    problemas_opciones
)

st.divider()


# ---------------------------------------------------
# PRIORIDAD OPERATIVA
# ---------------------------------------------------

st.header("6. Prioridad Operativa")

prioridad_operativa = st.radio(
    "¿Cuál es actualmente su principal objetivo?",
    [
        "Reducir costos operativos",
        "Reducir paros operativos costosos",
        "Reducir mantenimiento",
        "Mejorar eficiencia energética",
        "Incrementar vida útil de equipos",
        "Cumplir objetivos de sostenibilidad",
        "Evaluar oportunidades de mejora"
    ]
)

st.divider()


# ---------------------------------------------------
# BOTÓN CALCULAR
# ---------------------------------------------------

if st.button("Calcular Potencial de Optimización"):

    infraestructura_flags = {
        "cisterna_cruda": cisterna_cruda,
        "potabilizacion": potabilizacion,
        "cisterna_tratada": cisterna_tratada,
        "caldera": caldera,
        "hvac": hvac,
        "torres": torres,
        "alberca": alberca,
        "lavanderia": lavanderia,
        "cocina": cocina,
        "ptar": ptar,
        "spa": spa,
    }

    infraestructura = []
    if cisterna_cruda:
        infraestructura.append("Cisterna de agua cruda")
    if potabilizacion:
        infraestructura.append("Tratamiento / potabilización de agua")
    if cisterna_tratada:
        infraestructura.append("Cisterna de agua tratada")
    if caldera:
        infraestructura.append("Calderas o calentadores")
    if hvac:
        infraestructura.append("HVAC / aire acondicionado")
    if torres:
        infraestructura.append("Torres de enfriamiento")
    if alberca:
        infraestructura.append("Alberca")
    if lavanderia:
        infraestructura.append("Lavandería")
    if cocina:
        infraestructura.append("Cocina industrial")
    if ptar:
        infraestructura.append("PTAR")
    if spa:
        infraestructura.append("Spa / cuarto de vapor")

    diagnostico = calcular_diagnostico(
        habitaciones=habitaciones,
        ocupacion=ocupacion,
        infraestructura_flags=infraestructura_flags,
        problemas_seleccionados=problemas,
        prioridad_operativa=prioridad_operativa,
        energia=energia,
        agua=agua,
        quimicos=quimicos,
        mantenimiento=mantenimiento
    )

    # Áreas dinámicas
    areas = []

    if caldera:
        areas.append("Posible optimización en calderas, calentadores y transferencia térmica.")
    if hvac:
        areas.append("Posible mejora en eficiencia energética relacionada con HVAC / aire acondicionado.")
    if torres:
        areas.append("Posible reducción de incrustación y químicos en torres de enfriamiento.")
    if alberca:
        areas.append("Posible reducción de incrustación y consumo químico en alberca.")
    if lavanderia:
        areas.append("Posible reducción de consumo operativo y afectaciones por dureza de agua en lavandería.")
    if cocina:
        areas.append("Posible protección de equipos y reducción de mantenimiento en cocina industrial.")
    if ptar:
        areas.append("Posible oportunidad de mejora operativa en PTAR.")
    if spa:
        areas.append("Posible reducción de incrustación y mantenimiento en spa / cuarto de vapor.")
    if cisterna_cruda or potabilizacion or cisterna_tratada:
        areas.append("Posible mejora en control de calidad de agua desde almacenamiento, tratamiento y distribución.")

    for problema in problemas:
        if problema != "Ninguno identificado":
            areas.append(f"Validar impacto operativo asociado a: {problema}.")

    if not areas:
        areas.append("Se recomienda validar puntos críticos de entrada, bombeo y distribución hidráulica.")

    datos = {
        "fecha": datetime.now().strftime("%d/%m/%Y %H:%M"),
        "contacto_nombre": contacto_nombre,
        "contacto_whatsapp": contacto_whatsapp,
        "contacto_email": contacto_email,
        "hotel_nombre": hotel_nombre,
        "ciudad": ciudad,
        "habitaciones": habitaciones,
        "ocupacion": ocupacion,
        "tipo_hotel": tipo_hotel,
        "infraestructura": infraestructura,
        "problemas": problemas,
        "prioridad_operativa": prioridad_operativa,
        "energia": energia,
        "agua": agua,
        "quimicos": quimicos,
        "mantenimiento": mantenimiento,
        "areas": areas,
        **diagnostico
    }

    pdf_buffer = generar_pdf(datos)

    st.success("Se generó un diagnóstico preliminar de oportunidad hídrico-operativa.")

    st.header("Resumen Ejecutivo")

    semaforo = diagnostico["nivel_oportunidad"]
    semaforo_hex = color_semaforo(semaforo)

    st.markdown(
        f"""
        <div style="border-radius:12px; padding:18px; border:1px solid #ddd;">
            <div style="font-size:14px; color:#555;">Nivel de oportunidad detectado</div>
            <div style="font-size:34px; font-weight:700; color:{semaforo_hex};">● {semaforo}</div>
            <div style="font-size:15px; color:#333;">{diagnostico['mensaje_semaforo']}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

    col1, col2, col3 = st.columns(3)
    col1.metric("Ahorro anual potencial", formato_mxn(diagnostico["ahorro_anual"]))
    col2.metric("Payback estimado", f'{diagnostico["payback"]} meses')
    col3.metric("Prioridad FF", diagnostico["prioridad_ff"])

    st.info(
        f"Riesgo financiero potencial anual estimado: "
        f"{formato_mxn(diagnostico['riesgo_min'])} a {formato_mxn(diagnostico['riesgo_max'])}"
    )

    st.header("Resultados Estimados")

    st.metric("Inversión estimada", formato_mxn(diagnostico["inversion"]))
    st.metric("Ahorro mensual potencial", formato_mxn(diagnostico["ahorro_mensual"]))
    st.metric("Costo operativo mensual analizado", formato_mxn(diagnostico["costo_total"]))

    st.info(f"Nivel recomendado: {diagnostico['nivel']}")

    st.subheader("Áreas potenciales detectadas")
    for area in areas:
        st.write(f"• {area}")

    st.subheader("Próximo paso recomendado por Fluid Force")
    st.write(
        "Validación técnica especializada para confirmar condiciones operativas, validar oportunidades detectadas "
        "y determinar la estrategia de optimización más adecuada para la instalación."
    )

    st.divider()

    st.download_button(
        label="📄 Descargar PDF del diagnóstico",
        data=pdf_buffer,
        file_name="diagnostico_fluid_force.pdf",
        mime="application/pdf"
    )

    st.warning(
        "Importante: conserva este PDF y adjúntalo en WhatsApp para que podamos dar seguimiento técnico adecuado a tu evaluación."
    )

    mensaje = f"""
Hola, realicé el diagnóstico preliminar de eficiencia hídrico-operativa para mi hotel.

Hotel: {hotel_nombre}
Ciudad: {ciudad}
Contacto: {contacto_nombre}
WhatsApp: {contacto_whatsapp}
Email: {contacto_email}

Habitaciones: {habitaciones}
Nivel de oportunidad detectado: {semaforo}
Prioridad recomendada por Fluid Force: {diagnostico['prioridad_ff']}
Nivel recomendado: {diagnostico['nivel']}

Riesgo financiero potencial anual estimado:
{formato_mxn(diagnostico['riesgo_min'])} a {formato_mxn(diagnostico['riesgo_max'])}

Ahorro anual potencial estimado:
{formato_mxn(diagnostico['ahorro_anual'])}

Payback estimado:
{diagnostico['payback']} meses

Mi objetivo principal es:
{prioridad_operativa}

Me interesa recibir una validación técnica especializada.

Adjunto el PDF generado para dar seguimiento a mi evaluación.
"""

    mensaje_encoded = urllib.parse.quote(mensaje)
    whatsapp_url = f"https://wa.me/+{TELEFONO_WHATSAPP}?text={mensaje_encoded}"

    st.link_button("Solicitar Validación Técnica por WhatsApp", whatsapp_url)

    st.caption(
        "Los resultados mostrados son estimaciones preliminares sujetas a validación técnica y condiciones operativas reales."
    )
