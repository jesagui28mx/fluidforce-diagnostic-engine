import streamlit as st
import urllib.parse

# ---------------------------------------------------
# CONFIGURACIÓN GENERAL
# ---------------------------------------------------

st.set_page_config(
    page_title="Fluid Force Diagnostic Engine",
    page_icon="💧",
    layout="centered"
)

# ---------------------------------------------------
# HEADER
# ---------------------------------------------------

st.title("💧 Fluid Force Diagnostic Engine")

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
# DATOS GENERALES
# ---------------------------------------------------

st.header("1. Perfil del Hotel")

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

st.header("2. Infraestructura Operativa")

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

st.header("3. Costos Operativos Aproximados")

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

    # -----------------------------------------------
    # LÓGICA SIMPLE MVP
    # -----------------------------------------------

    costo_total = energia + agua + quimicos + mantenimiento

    ahorro_mensual = costo_total * 0.22

    ahorro_anual = ahorro_mensual * 12

    inversion = habitaciones * 2800

    payback = round(inversion / ahorro_mensual, 1)

    # -----------------------------------------------
    # NIVEL RECOMENDADO
    # -----------------------------------------------

    nivel = "Protección Básica"

    if habitaciones >= 40:
        nivel = "Optimización Operativa"

    if habitaciones >= 80:
        nivel = "Sistema Integral"

    # -----------------------------------------------
    # RESULTADOS
    # -----------------------------------------------

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

    st.divider()

    # -----------------------------------------------
    # WHATSAPP
    # -----------------------------------------------

    mensaje = f"""
Hola, realicé la evaluación preliminar de eficiencia hídrico-operativa para mi hotel.

Hotel: {hotel_nombre}
Ciudad: {ciudad}
Habitaciones: {habitaciones}

Nivel recomendado: {nivel}

Ahorro mensual potencial estimado:
${ahorro_mensual:,.0f} MXN

Payback estimado:
{payback} meses

Me interesa recibir una validación técnica especializada.
"""

    mensaje_encoded = urllib.parse.quote(mensaje)

    telefono = "5210000000000"

    whatsapp_url = f"https://wa.me/{telefono}?text={mensaje_encoded}"

    st.link_button(
        "Solicitar Validación Técnica por WhatsApp",
        whatsapp_url
    )

    st.caption(
        "Los resultados mostrados son estimaciones preliminares sujetas a validación técnica y condiciones operativas reales."
    )
