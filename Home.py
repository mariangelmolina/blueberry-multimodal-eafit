import streamlit as st
import paho.mqtt.publish as publish
from PIL import Image
import numpy as np
import os

st.set_page_config(page_title="blueberry. | boutique multimodal", page_icon="🫐", layout="wide")

# Identidad visual oficial Blueberry (Snow White, Parchment, Blueberry Indigo, Blue Gray)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@300;400;500;600&family=Playfair+Display:ital,wght@0,500;0,600;1,400&display=swap');
    
    .stApp {
        background-color: #FAF5F5;
        color: #18222D;
        font-family: 'Montserrat', sans-serif;
    }
    h1, h2, h3 {
        font-family: 'Playfair Display', serif !important;
        color: #2A375A !important;
    }
    .hero-box {
        background-color: #F4F1EA;
        padding: 2rem;
        border-radius: 10px;
        border-left: 5px solid #2A375A;
        margin-bottom: 1.5rem;
    }
    .price-tag {
        color: #6997BF;
        font-weight: 600;
        font-size: 0.95rem;
    }
    </style>
""", unsafe_allow_html=True)

BROKER = "broker.hivemq.com"
TOPIC_CMD = "eafit2026/mariangel_blueberry_9842/cmd"

# Catálogo de 5 piezas con su imagen, precio, costo COGS y ángulo del dispensador Wokwi
COLLARES = [
    {"id": "Wrap Azul", "nombre": "The Blueberry Wrap Azul", "precio": 35000, "cogs": 6000, "img": "images/collar-azul.jpg", "angulo": 30, "desc": "Perlas & mostacilla índigo · 4+ usos"},
    {"id": "Wrap Vinotinto", "nombre": "The Blueberry Wrap Vinotinto", "precio": 35000, "cogs": 6000, "img": "images/collar-vinotinto.jpg", "angulo": 65, "desc": "Tono profundo · Collar, cintura o pulsera"},
    {"id": "Wrap Coral", "nombre": "The Blueberry Wrap Coral", "precio": 35000, "cogs": 6000, "img": "images/collar-coral.jpg", "angulo": 100, "desc": "Vibra veraniega · Hecho a mano"},
    {"id": "Wrap Neutro", "nombre": "The Blueberry Wrap Neutro", "precio": 35000, "cogs": 6000, "img": "images/collar-beige.jpg", "angulo": 135, "desc": "Crema perlada · Combina con todo"},
    {"id": "Pearl Choker", "nombre": "Pearl Essential Choker", "precio": 85000, "cogs": 47664, "img": "images/collar-perlas.jpg", "angulo": 170, "desc": "Perlas auténticas de río · Edición especial"},
]

if "seleccionado" not in st.session_state:
    st.session_state["seleccionado"] = COLLARES[0]["nombre"]
if "historial_pedidos" not in st.session_state:
    st.session_state["historial_pedidos"] = []

def enviar_a_wokwi(nombre_corto, angulo):
    publish.single(TOPIC_CMD, payload=f"PEDIDO:{nombre_corto}:{angulo}", hostname=BROKER, port=1883)

# --- HEADER EDITORIAL ---
st.markdown("""
<div class="hero-box">
    <h1 style="margin-bottom:0.2rem;">blueberry.</h1>
    <p style="color:#6997BF; font-style:italic; margin-bottom:0.6rem;">hecho a mano en medellín con intención · 1 pieza = 4+ formas de usarla</p>
    <p style="margin:0; font-size:0.9rem;">Explora la colección, deja que nuestro asesor visual te recomiende según tu outfit o elige tu pieza favorita para activar su ensamble en el taller físico.</p>
</div>
""", unsafe_allow_html=True)

# --- MODALIDAD 1: ASESOR VISUAL DE OUTFIT ---
with st.expander("📸 Modalidad Visual: ¿No sabes cuál elegir? Sube una foto de tu outfit", expanded=False):
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
                st.success("Tonos cálidos detectados → Te recomendamos **The Blueberry Wrap Coral** o **Vinotinto**.")
                st.session_state["seleccionado"] = "The Blueberry Wrap Coral"
            elif b > r + 15:
                st.info("Tonos fríos/azules detectados → Te recomendamos **The Blueberry Wrap Azul**.")
                st.session_state["seleccionado"] = "The Blueberry Wrap Azul"
            else:
                st.info("Tonos neutros/clásicos → Te recomendamos **The Blueberry Wrap Neutro** o **Pearl Essential Choker**.")
                st.session_state["seleccionado"] = "The Blueberry Wrap Neutro"

# --- MODALIDAD 2: GALERÍA VISUAL DE 5 COLLARES ---
st.subheader("Nuestras Piezas")
cols = st.columns(5)

for idx, item in enumerate(COLLARES):
    with cols[idx]:
        if os.path.exists(item["img"]):
            st.image(item["img"], use_container_width=True)
        else:
            st.info(f"📷 Sube `{item['img']}`")
        st.markdown(f"**{item['nombre']}**")
        st.markdown(f"<span class='price-tag'>${item['precio']:,} COP</span>", unsafe_allow_html=True)
        st.caption(item["desc"])
        if st.button("Elegir ✨", key=f"btn_{idx}", use_container_width=True):
            st.session_state["seleccionado"] = item["nombre"]

st.divider()

# --- MODALIDAD 3: PERSONALIZACIÓN Y ENVÍO AL MUNDO FÍSICO ---
st.subheader("Confirmar Pedido & Enviar al Taller")
c1, c2, c3 = st.columns([2, 2, 1.5])

with c1:
    nombres_lista = [c["nombre"] for c in COLLARES]
    idx_actual = nombres_lista.index(st.session_state["seleccionado"])
    pieza_final = st.selectbox("Pieza seleccionada:", nombres_lista, index=idx_actual)
    st.session_state["seleccionado"] = pieza_final

with c2:
    uso = st.selectbox("¿Cómo lo usarás principalmente?", ["Gargantilla doble", "Collar largo", "Waistbead (Cintura)", "Pulsera multi-capa"])
    entrega = st.selectbox("Punto de entrega:", ["Portería Universidad EAFIT", "Portería Ciudad del Río", "Rappi Favor (Medellín)"])

with c3:
    clienta = st.text_input("Tu nombre:", placeholder="Ej. Camila")
    st.write("")
    confirmar = st.button("✨ Ordenar Ahora", type="primary", use_container_width=True)

if confirmar:
    collar_obj = next(c for c in COLLARES if c["nombre"] == pieza_final)
    try:
        enviar_a_wokwi(collar_obj["id"], collar_obj["angulo"])
        st.session_state["historial_pedidos"].append({
            "clienta": clienta or "Clienta Web",
            "pieza": collar_obj["nombre"],
            "id": collar_obj["id"],
            "precio": collar_obj["precio"],
            "cogs": collar_obj["cogs"],
            "uso": uso,
            "entrega": entrega,
            "estado": "🔨 En ensamble (Taller activado)"
        })
        st.success(f"¡Pedido enviado! En **Wokwi** se encendió el LED, sonó la alerta y el dispensador giró a **{collar_obj['angulo']}°** para armar tu **{collar_obj['id']}**.")
    except Exception as e:
        st.error(f"Error enviando señal MQTT: {e}")
