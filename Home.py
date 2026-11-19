import streamlit as st
import paho.mqtt.publish as publish
from PIL import Image
import numpy as np

st.set_page_config(page_title="Blueberry · Boutique", page_icon="🫐", layout="centered")

BROKER = "broker.hivemq.com"
TOPIC_CMD = "eafit2026/mariangel_blueberry_9842/cmd"

# Catálogo real de Blueberry y ángulo correspondiente del dispensador en Wokwi
CATALOGO = {
    "The Blueberry Wrap Azul ($35.000)": ("Wrap Azul", 45),
    "The Blueberry Wrap Coral ($35.000)": ("Wrap Coral", 135),
    "Pearl Essential Choker ($85.000)": ("Pearl Choker", 90),
    "The Blueberry Wrap Neutro ($35.000)": ("Wrap Neutro", 0),
}

def enviar_orden_wokwi(nombre_corto, angulo):
    mensaje = f"PEDIDO:{nombre_corto}:{angulo}"
    publish.single(TOPIC_CMD, payload=mensaje, hostname=BROKER, port=1883)

# --- INTERFAZ LIMPIA ---
st.title("🫐 Blueberry")
st.caption("Asistente multimodal de estilo · Medellín, Colombia")
st.markdown("**¿Para qué sirve esta app?** Ayuda a las clientas a elegir su collar ideal según su outfit y envía la orden al instante al taller físico (Wokwi + MyMQTT).")

st.divider()

# MODALIDAD 1: VISIÓN (IMAGEN)
st.subheader("1. Asesor Visual (Sube foto de tu outfit)")
foto = st.file_uploader("Opcional: sube una foto de tu ropa para recomendarte un tono", type=["jpg", "jpeg", "png"])

sugerencia_default = 0
if foto is not None:
    img = Image.open(foto).convert("RGB").resize((60, 60))
    datos = np.array(img)
    r, g, b = datos[:, :, 0].mean(), datos[:, :, 1].mean(), datos[:, :, 2].mean()
    
    col_img, col_txt = st.columns([1, 2])
    with col_img:
        st.image(foto, width=130)
    with col_txt:
        if r > b + 20:
            st.success("Detectamos tonos cálidos en tu ropa. Te sugerimos **The Blueberry Wrap Coral**.")
            sugerencia_default = 1
        elif b > r + 15:
            st.info("Detectamos tonos fríos/azules. Te sugerimos **The Blueberry Wrap Azul**.")
            sugerencia_default = 0
        else:
            st.info("Detectamos tonos neutros. Te sugerimos **Pearl Essential Choker**.")
            sugerencia_default = 2

st.divider()

# MODALIDAD 2: TEXTO Y BOTONES DIGITALES
st.subheader("2. Personaliza y confirma tu pedido")

collar_seleccionado = st.selectbox(
    "Elige tu pieza:",
    list(CATALOGO.keys()),
    index=sugerencia_default
)

uso = st.radio(
    "¿Cómo planeas usarlo?",
    ["Gargantilla doble", "Collar largo", "Waistbead (Cintura)", "Pulsera"],
    horizontal=True
)

nombre_cliente = st.text_input("Tu nombre (para identificar el pedido):", placeholder="Ej. Camila")

st.write("")

# MODALIDAD 3: ACCIÓN HACIA EL MUNDO FÍSICO (WOKWI + MYMQTT)
if st.button("✨ Confirmar Pedido y Enviar al Taller", type="primary", use_container_width=True):
    nombre_corto, angulo = CATALOGO[collar_seleccionado]
    try:
        enviar_orden_wokwi(nombre_corto, angulo)
        st.session_state["ultimo_pedido"] = f"{nombre_corto} ({uso}) — Cliente: {nombre_cliente or 'Invitada'}"
        st.success(f"¡Listo! Se envió **{nombre_corto}** al taller. En Wokwi se encendió el LED, sonó la alerta y el motor giró a **{angulo}°**.")
    except Exception as e:
        st.error(f"No se pudo conectar con MQTT: {e}")
