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
    page_title="Fluid Force Diagnostic Engine",
    page_icon="💧",
    layout="centered"
)

LOGO_PATH = "LOGO_FLUID_FORCE2,3.png"

# CAMBIA ESTE NÚMERO POR EL WHATSAPP REAL
# Formato México: 52 + 1 + número a 10 dígitos
TELEFONO_WHATSAPP = "5210000000000"


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
        fontSize=18,
        textColor=colors.HexColor("#12345A"),
        alignment=1,
        spaceAfter=14
    )

    subtitle_style = ParagraphStyle(
        "SubtitleFluid",
        parent=styles["Heading2"],
        fontSize=12,
        textColor=colors.HexColor("#12345A"),
        spaceAfter=10
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
        story.append(Spacer(1, 10))
    except Exception:
        pass

    story.append(Paragraph("Diagnóstico Preliminar de Eficiencia Hídrico-Operativa", title_style))
    story.append(Paragraph("Fluid Force · Tratamiento Natural del Agua", subtitle_style))
    story.append(Spacer(1, 12))

    story.append(Paragraph(
        "Este documento resume una evaluación preliminar basada en la información proporcionada por el prospecto. "
        "Los resultados son estimados y requieren validación técnica especializada.",
        normal_style
    ))

    story.append(Spacer(1, 14))

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
    story.append(Spacer(1, 14))

    # Infraestructura
    infraestructura_texto = ", ".join(datos["infraestructura"]) if datos["infraestructura"] else "No especificada"

    story.append(Paragraph("2. Infraestructura operativa reportada", subtitle_style))
    story.append(Paragraph(infraestructura_texto, normal_style))
    story.append(Spacer(1, 14))

    # Costos
    costos_data = [
        ["Concepto", "Monto mensual estimado"],
        ["Energía", f'${datos["energia"]:,.0f} MXN'],
        ["Agua", f'${datos["agua"]:,.0f} MXN'],
        ["Químicos", f'${datos["quimicos"]:,.0f} MXN'],
        ["Mantenimiento hidráulico", f'${datos["mantenimiento"]:,.0f} MXN'],
        ["Costo operativo analizado", f'${datos["costo_total"]:,.0f} MXN'],
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

    story.append(Paragraph("3. Costos operativos aproximados", subtitle_style))
    story.append(tabla_costos)
    story.append(Spacer(1, 14))

    # Resultados
    resultados_data = [
        ["Resultado", "Estimación preliminar"],
        ["Nivel recomendado", datos["nivel"]],
        ["Inversión estimada", f'${datos["inversion"]:,.0f} MXN'],
        ["Ahorro mensual potencial", f'${datos["ahorro_mensual"]:,.0f} MXN'],
        ["Ahorro anual potencial", f'${datos["ahorro_anual"]:,.0f} MXN'],
        ["Payback estimado", f'{datos["payback"]} meses'],
    ]

    tabla_resultados = Table(resultados_data, colWidths=[3.3 * inch, 3.2 * inch])
    tabla_resultados.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0B5CAD")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("BACKGROUND", (0, 1), (-1, -1), colors.HexColor("#F7FBFF")),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("GRID", (0, 0), (-1, -1), 0.3, colors.lightgrey),
        ("PADDING", (0, 0), (-1, -1), 6),
    ]))

    story.append(Paragraph("4. Resultado preliminar", subtitle_style))
    story.append(tabla_resultados)
    story.append(Spacer(1, 14))

    # Áreas detectadas
    story.append(Paragraph("5. Áreas potenciales de oportunidad", subtitle_style))

    for area in datos["areas"]:
        story.append(Paragraph(f"• {area}", normal_style))

    story.append(Spacer(1, 14))

    story.append(Paragraph("Nota importante", subtitle_style))
    story.append(Paragraph(
        "Este diagnóstico no sustituye un levantamiento técnico formal. "
        "La selección final de equipos, puntos de instalación, diámetros, cantidades, inversión definitiva y retorno estimado "
        "deben validarse mediante revisión técnica especializada.",
        small_style
    ))

    story.append(Spacer(1, 12))

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

st.title("Fluid Force Diagnostic Engine")

st.subheader(
    "Evaluación preliminar de eficiencia hídrico-operativa para hoteles"
)

st.markdown("""
Descubre posibles áreas de optimización relacionadas con:

- eficiencia térmica
- incrustación
- mantenimiento hidráulico
- consumo energético
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
        "Urbano"
    ]
)

st.divider()


# ---------------------------------------------------
# INFRAESTRUCTURA
# ---------------------------------------------------

st.header("3. Infraestructura Operativa")

caldera = st.checkbox("Calderas")
hvac = st.checkbox("HVAC")
torres = st.checkbox("Torres de enfriamiento")
alberca = st.checkbox("Alberca")
lavanderia = st.checkbox("Lavandería")
cocina = st.checkbox("Cocina industrial")
ptar = st.checkbox("PTAR")
spa = st.checkbox("Spa")

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

st.caption(
    "No necesitas cifras exactas. Puedes utilizar estimados aproximados."
)

st.divider()


# ---------------------------------------------------
# BOTÓN CALCULAR
# ---------------------------------------------------

if st.button("Generar Diagnóstico"):

    infraestructura = []

    if caldera:
        infraestructura.append("Calderas")
    if hvac:
        infraestructura.append("HVAC")
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
        infraestructura.append("Spa")

    costo_total = energia + agua + quimicos + mantenimiento

    # Factor conservador preliminar
    ahorro_mensual = costo_total * 0.22
    ahorro_anual = ahorro_mensual * 12

    # Inversión inicial estimada simple MVP
    inversion = habitaciones * 2800

    # Ajustes por infraestructura crítica
    if caldera:
        inversion += 18586
    if hvac:
        inversion += 22029
    if torres:
        inversion += 44058
    if alberca:
        inversion += 18586
    if lavanderia:
        inversion += 18586
    if cocina:
        inversion += 18586
    if ptar:
        inversion += 12599
    if spa:
        inversion += 12599

    if ahorro_mensual > 0:
        payback = round(inversion / ahorro_mensual, 1)
    else:
        payback = 0

    # Nivel recomendado
    nivel = "Protección Básica"

    puntos = 0
    puntos += 2 if caldera else 0
    puntos += 2 if hvac else 0
    puntos += 2 if torres else 0
    puntos += 1 if alberca else 0
    puntos += 1 if lavanderia else 0
    puntos += 1 if cocina else 0
    puntos += 1 if ptar else 0
    puntos += 1 if spa else 0

    if habitaciones >= 40 or puntos >= 4:
        nivel = "Optimización Operativa"

    if habitaciones >= 80 or puntos >= 7:
        nivel = "Sistema Integral"

    # Áreas dinámicas
    areas = []

    if caldera:
        areas.append("Posible optimización en calderas y transferencia térmica.")
    if hvac:
        areas.append("Posible mejora en eficiencia energética relacionada con HVAC.")
    if torres:
        areas.append("Posible reducción de incrustación y químicos en torres de enfriamiento.")
    if alberca:
        areas.append("Posible reducción de incrustación y consumo químico en alberca.")
    if lavanderia:
        areas.append("Posible reducción de consumo operativo en lavandería.")
    if cocina:
        areas.append("Posible protección de equipos y reducción de mantenimiento en cocina industrial.")
    if ptar:
        areas.append("Posible oportunidad de mejora operativa en PTAR.")
    if spa:
        areas.append("Posible reducción de incrustación y mantenimiento en spa.")

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
        "energia": energia,
        "agua": agua,
        "quimicos": quimicos,
        "mantenimiento": mantenimiento,
        "costo_total": costo_total,
        "inversion": inversion,
        "ahorro_mensual": ahorro_mensual,
        "ahorro_anual": ahorro_anual,
        "payback": payback,
        "nivel": nivel,
        "areas": areas
    }

    pdf_buffer = generar_pdf(datos)

    st.success("Se detecta potencial de optimización operativa.")

    st.header("Resultados Estimados")

    st.metric(
        "Inversión estimada",
        f"${inversion:,.0f} MXN"
    )

    st.metric(
        "Ahorro mensual potencial",
        f"${ahorro_mensual:,.0f} MXN"
    )

    st.metric(
        "Ahorro anual potencial",
        f"${ahorro_anual:,.0f} MXN"
    )

    st.metric(
        "Payback estimado",
        f"{payback} meses"
    )

    st.info(f"Nivel recomendado: {nivel}")

    st.subheader("Áreas potenciales detectadas")

    for area in areas:
        st.write(f"• {area}")

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
Nivel recomendado: {nivel}

Ahorro mensual potencial estimado:
${ahorro_mensual:,.0f} MXN

Payback estimado:
{payback} meses

Me interesa recibir una validación técnica especializada.

Por favor indíquenme cómo adjuntar el PDF generado para dar seguimiento a mi evaluación.
"""

    mensaje_encoded = urllib.parse.quote(mensaje)

    whatsapp_url = f"https://wa.me/{TELEFONO_WHATSAPP}?text={mensaje_encoded}"

    st.link_button(
        "Solicitar Validación Técnica por WhatsApp",
        whatsapp_url
    )

    st.caption(
        "Los resultados mostrados son estimaciones preliminares sujetas a validación técnica y condiciones operativas reales."
    )
