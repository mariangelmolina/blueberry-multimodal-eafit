import streamlit as st
import paho.mqtt.client as mqtt
from PIL import Image
import numpy as np
import time

st.set_page_config(page_title="Blueberry · Vitrina Multimodal", page_icon="🫐", layout="wide")

# Estilos personalizados con la paleta oficial de Blueberry
st.markdown("""
    <style>
    .stApp { background-color: #FAF5F5; color: #18222D; }
    h1, h2, h3 { color: #2A375A !important; font-family: Georgia, serif; }
    </style>
""", unsafe_allow_html=True)

TOPIC_CMD = "eafit2026/mariangel_blueberry_9842/cmd"

def enviar_a_wokwi(mensaje):
    client = mqtt.Client(client_id=f"Streamlit_Home_{int(time.time())}")
    client.connect("broker.hivemq.com", 1883, 60)
    client.publish(TOPIC_CMD, mensaje)
    client.disconnect()

st.title("🫐 blueberry — vitrina multimodal interactiva")
st.markdown("*1 pieza = 4+ formas de usarla · hecho a mano en medellín con intención*")
st.divider()

col1, col2 = st.columns(2)

# MODALIDAD 1: VISIÓN / IMAGEN
with col1:
    st.subheader("1. Modalidad Visual: Asesor de Outfit")
    st.write("Sube una foto de tu ropa para detectar el tono y recomendarte el collar ideal:")
    img_file = st.file_uploader("Sube tu outfit (JPG/PNG)", type=["jpg", "png", "jpeg"])
    
    recomendacion = "Collar Luna"
    if img_file:
        img = Image.open(img_file).convert("RGB").resize((50, 50))
        arr = np.array(img)
        r, g, b = arr[:,:,0].mean(), arr[:,:,1].mean(), arr[:,:,2].mean()
        st.image(img_file, width=220, caption="Outfit analizado")
        
        if r > b + 15:
            recomendacion = "Collar Sol"
            st.success("✨ Tonos cálidos detectados: Te recomendamos **The Blueberry Wrap Coral / Sol**")
        else:
            recomendacion = "Collar Luna"
            st.info("✨ Tonos fríos/neutros detectados: Te recomendamos **The Blueberry Wrap Azul / Luna**")

# MODALIDAD 2: AUDIO / VOZ + SELECCIÓN TÁCTIL
with col2:
    st.subheader("2. Modalidad Voz y Personalización")
    audio_val = st.audio_input("Graba una nota de voz con tus preferencias (ej. 'Lo quiero para cintura')")
    if audio_val:
        st.audio(audio_val)
        st.caption("✅ Nota de voz capturada y vinculada a tu orden.")
    
    uso = st.selectbox("¿Cómo lo usarás principalmente?", [
        "Gargantilla doble", 
        "Collar largo clásico", 
        "Waistbead (Cadena de cintura)", 
        "Pulsera multi-capa"
    ])
    
    collar = st.radio("Elige tu pieza Blueberry:", [
        "Collar Luna ($35.000 COP)",
        "Collar Sol ($35.000 COP)",
        "Pearl Choker ($85.000 COP)"
    ])

st.divider()

# MODALIDAD 3: INTERACCIÓN CON EL MUNDO FÍSICO (WOKWI)
st.subheader("3. Confirmación Física en Taller")
if st.button("✨ Confirmar Pedido y Activar Taller Físico", type="primary", use_container_width=True):
    nombre_pieza = collar.split(" (")[0]
    angulo = 45 if "Luna" in nombre_pieza else (135 if "Sol" in nombre_pieza else 90)
    
    try:
        enviar_a_wokwi(f"PEDIDO:{nombre_pieza}:{angulo}")
        st.balloons()
        st.success(f"¡Orden enviada al taller! En Wokwi y MyMQTT se activó el LED, el sonido y el dispensador giró a {angulo}°.")
    except Exception as e:
        st.error(f"Error conectando con el broker MQTT: {e}")
