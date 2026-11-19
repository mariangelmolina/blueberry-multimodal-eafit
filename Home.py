import streamlit as st
import paho.mqtt.client as mqtt
from PIL import Image
import numpy as np
import os
import time

st.set_page_config(page_title="blueberry. | boutique", page_icon="🫐", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@300;400;500;600&family=Playfair+Display:ital,wght@0,500;0,600;1,400&display=swap');
    
    .stApp {
        background-color: #FAF5F5 !important;
        color: #18222D !important;
        font-family: 'Montserrat', sans-serif;
    }
    h1, h2, h3 {
        font-family: 'Playfair Display', serif !important;
        color: #2A375A !important;
    }
    p, label, span, div, small {
        color: #18222D !important;
    }
    details, summary, [data-testid="stExpander"] {
        background-color: #F4F1EA !important;
        color: #2A375A !important;
        border: 1.5px solid #2A375A !important;
        border-radius: 8px !important;
    }
    summary p, summary span, summary svg {
        color: #2A375A !important;
        fill: #2A375A !important;
        font-weight: 600 !important;
    }
    [data-testid="stFileUploaderDropzone"] {
        background-color: #FFFFFF !important;
        border: 1.5px dashed #2A375A !important;
        color: #18222D !important;
    }
    [data-testid="stFileUploaderDropzone"] button {
        background-color: #2A375A !important;
        color: #FAF5F5 !important;
    }
    [data-testid="stFileUploaderDropzone"] button span,
    [data-testid="stFileUploaderDropzone"] button p {
        color: #FAF5F5 !important;
    }
    div[data-baseweb="select"] > div,
    div[data-baseweb="input"] > div,
    input {
        background-color: #FFFFFF !important;
        color: #18222D !important;
        border: 1.5px solid #2A375A !important;
    }
    ul[role="listbox"] li {
        background-color: #FFFFFF !important;
        color: #18222D !important;
    }
    .stButton > button[kind="secondary"] {
        background-color: #FFFFFF !important;
        color: #2A375A !important;
        border: 1.5px solid #2A375A !important;
        font-weight: 600 !important;
    }
    .stButton > button[kind="secondary"]:hover {
        background-color: #2A375A !important;
        color: #FAF5F5 !important;
    }
    .stButton > button[kind="primary"] {
        background-color: #2A375A !important;
        color: #F6EFA6 !important;
        border: none !important;
        font-weight: 600 !important;
    }
    .stButton > button[kind="primary"] p {
        color: #F6EFA6 !important;
    }
    [data-testid="stAlert"], [data-testid="stAlert"] > div {
        background-color: #F4F1EA !important;
        border: 2px solid #2A375A !important;
        color: #18222D !important;
        border-radius: 8px !important;
    }
    [data-testid="stAlert"] p, [data-testid="stAlert"] span, [data-testid="stAlert"] strong {
        color: #18222D !important;
        font-weight: 500 !important;
    }
    .hero-box {
        background-color: #F4F1EA;
        padding: 1.8rem;
        border-radius: 10px;
        border-left: 5px solid #2A375A;
        margin-bottom: 1.5rem;
    }
    .price-tag {
        color: #2A375A !important;
        background-color: #F6EFA6;
        padding: 2px 8px;
        border-radius: 4px;
        font-weight: 600;
        font-size: 0.9rem;
        display: inline-block;
        margin-bottom: 4px;
    }
    </style>
""", unsafe_allow_html=True)

BROKER = "broker.emqx.io"
TOPIC_CMD = "eafit2026/mariangel_blueberry_9842/cmd"

COLLARES = [
    {"id": "Wrap Azul", "nombre": "The Blueberry Wrap Azul", "precio": 35000, "cogs": 6000, "img": "images/collar-azul.jpg", "angulo": 30, "desc": "Perlas & mostacilla índigo · 4+ formas de uso"},
    {"id": "Wrap Vinotinto", "nombre": "The Blueberry Wrap Vinotinto", "precio": 35000, "cogs": 6000, "img": "images/collar-vinotinto.jpg", "angulo": 65, "desc": "Tono profundo · Creado desde el amor"},
    {"id": "Wrap Coral", "nombre": "The Blueberry Wrap Coral", "precio": 35000, "cogs": 6000, "img": "images/collar-coral.jpg", "angulo": 100, "desc": "Vibra veraniega · Effortless chic"},
    {"id": "Wrap Neutro", "nombre": "The Blueberry Wrap Neutro", "precio": 35000, "cogs": 6000, "img": "images/collar-beige.jpg", "angulo": 135, "desc": "Crema perlada · Combina con todos tus básicos"},
    {"id": "Pearl Choker", "nombre": "Pearl Essential Choker", "precio": 85000, "cogs": 47664, "img": "images/collar-perlas.jpg", "angulo": 170, "desc": "Perlas auténticas de río · Edición especial"},
]

if "seleccionado" not in st.session_state:
    st.session_state["seleccionado"] = COLLARES[0]["nombre"]
if "historial_pedidos" not in st.session_state:
    st.session_state["historial_pedidos"] = []

def enviar_a_wokwi(nombre_corto, angulo):
    client = mqtt.Client(client_id=f"BB_Web_{int(time.time()*1000)}")
    client.connect(BROKER, 1883, 60)
    client.loop_start()
    info = client.publish(TOPIC_CMD, f"PEDIDO:{nombre_corto}:{angulo}", qos=1)
    info.wait_for_publish(timeout=3.0)
    client.loop_stop()
    client.disconnect()

# --- HEADER ---
st.markdown("""
<div class="hero-box">
    <h1 style="margin-bottom:0.2rem;">blueberry.</h1>
    <p style="color:#6997BF !important; font-style:italic; margin-bottom:0.5rem;">creado en medellín desde el amor · 1 pieza = 4+ formas de usarla</p>
    <p style="margin:0; font-size:0.95rem;">Selecciona tu pieza favorita en nuestra galería o sube una foto de tu outfit para recibir una recomendación al instante.</p>
</div>
""", unsafe_allow_html=True)

# --- MODALIDAD VISUAL (OUTFIT) ---
with st.expander("📸 Asesor Visual: Sube una foto de tu outfit para recomendarte un collar"):
    col_u, col_r = st.columns([1, 2])
    with col_u:
        foto = st.file_uploader("Sube tu look (JPG/PNG)", type=["jpg", "jpeg", "png"])
    with col_r:
        if foto:
            img = Image.open(foto).convert("RGB").resize((50, 50))
            arr = np.array(img)
            r, g, b = arr[:, :, 0].mean(), arr[:, :, 1].mean(), arr[:, :, 2].mean()
            st.image(foto, width=120)
            if r > b + 20:
                st.success("Tonos cálidos detectados → Te recomendamos The Blueberry Wrap Coral.")
                st.session_state["seleccionado"] = "The Blueberry Wrap Coral"
            elif b > r + 15:
                st.info("Tonos fríos/azules detectados → Te recomendamos The Blueberry Wrap Azul.")
                st.session_state["seleccionado"] = "The Blueberry Wrap Azul"
            else:
                st.info("Tonos neutros/clásicos → Te recomendamos The Blueberry Wrap Neutro.")
                st.session_state["seleccionado"] = "The Blueberry Wrap Neutro"

# --- GALERÍA DE 5 COLLARES ---
st.subheader("Nuestras Piezas")
cols = st.columns(5)

for idx, item in enumerate(COLLARES):
    with cols[idx]:
        if os.path.exists(item["img"]):
            st.image(item["img"], use_container_width=True)
        else:
            st.info(f"📷 `{item['img']}`")
        st.markdown(f"**{item['nombre']}**")
        st.markdown(f"<span class='price-tag'>${item['precio']:,} COP</span>", unsafe_allow_html=True)
        st.caption(item["desc"])
        if st.button("Elegir ✨", key=f"btn_{idx}", use_container_width=True):
            st.session_state["seleccionado"] = item["nombre"]
            st.rerun()

st.divider()

# --- CONFIRMACIÓN SIMPLIFICADA ---
st.subheader("Finalizar Pedido")
c1, c2, c3 = st.columns([2, 2, 1.5])

with c1:
    nombres_lista = [c["nombre"] for c in COLLARES]
    idx_actual = nombres_lista.index(st.session_state["seleccionado"])
    pieza_final = st.selectbox("Pieza seleccionada:", nombres_lista, index=idx_actual)
    st.session_state["seleccionado"] = pieza_final

with c2:
    entrega = st.selectbox("Punto de entrega:", ["Portería Universidad EAFIT", "Portería Ciudad del Río", "Rappi Favor (Medellín)"])

with c3:
    clienta = st.text_input("Tu nombre:", placeholder="Ej. Camila")

if st.button("✨ Confirmar Pedido y Enviar al Taller", type="primary", use_container_width=True):
    collar_obj = next(c for c in COLLARES if c["nombre"] == pieza_final)
    try:
        enviar_a_wokwi(collar_obj["id"], collar_obj["angulo"])
        st.session_state["historial_pedidos"].append({
            "clienta": clienta or "Clienta Web",
            "pieza": collar_obj["nombre"],
            "id": collar_obj["id"],
            "precio": collar_obj["precio"],
            "cogs": collar_obj["cogs"],
            "entrega": entrega,
            "estado": "Pendiente"
        })
        st.success(f"¡Pedido enviado! En Wokwi se activó la alerta y el dispensador giró a {collar_obj['angulo']}° para armar tu {collar_obj['id']}.")
    except Exception as e:
        st.error(f"Error enviando señal MQTT: {e}")
