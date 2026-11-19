import streamlit as st
import paho.mqtt.client as mqtt
import paho.mqtt.publish as publish
import time

st.set_page_config(page_title="blueberry. | mesa de taller", page_icon="🪡", layout="wide")

# Estética Modo Taller Artesanal (Ink Black + Blueberry Indigo + Vanilla Custard)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@300;400;500;600&family=Playfair+Display:ital,wght@0,500;0,600;1,400&display=swap');
    
    .stApp {
        background-color: #18222D !important;
        color: #FAF5F5 !important;
        font-family: 'Montserrat', sans-serif;
    }
    h1, h2, h3 {
        font-family: 'Playfair Display', serif !important;
        color: #F6EFA6 !important;
    }
    p, span, label, div, li {
        color: #FAF5F5 !important;
    }
    [data-testid="stMetricValue"] {
        color: #F6EFA6 !important;
        font-family: 'Playfair Display', serif !important;
    }
    [data-testid="stMetricLabel"] {
        color: #6997BF !important;
    }
    .stButton > button[kind="secondary"] {
        background-color: #2A375A !important;
        color: #F6EFA6 !important;
        border: 1.5px solid #F6EFA6 !important;
    }
    .workshop-banner {
        background-color: #2A375A;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 5px solid #F6EFA6;
        margin-bottom: 1.5rem;
    }
    .pending-card {
        background-color: #2A375A;
        padding: 1rem 1.2rem;
        border-radius: 8px;
        border-left: 4px solid #F6EFA6;
        margin-bottom: 0.7rem;
    }
    .done-card {
        background-color: #1F2D3D;
        padding: 0.9rem 1.1rem;
        border-radius: 8px;
        border-left: 4px solid #6997BF;
        margin-bottom: 0.7rem;
    }
    </style>
""", unsafe_allow_html=True)

BROKER = "broker.hivemq.com"
TOPIC_CMD = "eafit2026/mariangel_blueberry_9842/cmd"
TOPIC_STOCK = "eafit2026/mariangel_blueberry_9842/stock"
TOPIC_ESTADO = "eafit2026/mariangel_blueberry_9842/estado"

if "stock_taller" not in st.session_state:
    st.session_state["stock_taller"] = 75
if "historial_pedidos" not in st.session_state:
    st.session_state["historial_pedidos"] = []

def leer_estado_retenido_wokwi():
    datos = {"stock": None, "estado": None}
    
    def on_message(client, userdata, msg):
        texto = msg.payload.decode()
        if msg.topic == TOPIC_STOCK:
            datos["stock"] = int(texto)
        elif msg.topic == TOPIC_ESTADO:
            datos["estado"] = texto

    client = mqtt.Client(client_id=f"BB_Taller_{int(time.time())}")
    client.on_message = on_message
    client.connect(BROKER, 1883, 60)
    client.subscribe([(TOPIC_STOCK, 0), (TOPIC_ESTADO, 0)])
    client.loop_start()
    time.sleep(1.2)
    client.loop_stop()
    client.disconnect()
    return datos

# --- ENCABEZADO MESA DE TALLER ---
st.markdown("""
<div class="workshop-banner">
    <h1 style="margin:0;">🪡 mesa de taller · blueberry studio</h1>
    <p style="color:#6997BF !important; font-style:italic; margin-top:0.3rem; margin-bottom:0;">
        inventario en vivo (0–100%) y registro de producción · sincronizado con Wokwi
    </p>
</div>
""", unsafe_allow_html=True)

# --- CONTROLES DE SINCRONIZACIÓN Y RESTOCK ---
col_info, col_btn1, col_btn2 = st.columns([2, 1, 1])

with col_info:
    st.write("Mueve el potenciómetro o presiona el botón azul en Wokwi, o ejecuta un restock de insumos:")

with col_btn1:
    if st.button("🔄 Sincronizar con Wokwi", type="primary", use_container_width=True):
        datos = leer_estado_retenido_wokwi()
        if datos["stock"] is not None:
            st.session_state["stock_taller"] = datos["stock"]
        if datos["estado"] == "LISTO":
            for p in st.session_state["historial_pedidos"]:
                if p["estado"] == "Pendiente":
                    p["estado"] = "Finalizado"
                    break
        st.toast(f"✅ Sincronizado: Stock en {st.session_state['stock_taller']}%")

with col_btn2:
    if st.button("📦 Hacer Restock (100%)", use_container_width=True):
        st.session_state["stock_taller"] = 100
        try:
            publish.single(TOPIC_CMD, payload="RESTOCK", hostname=BROKER, port=1883)
            publish.single(TOPIC_STOCK, payload="100", hostname=BROKER, port=1883, retain=True)
        except Exception:
            pass
        st.toast("✨ Restock completado (100% en Insumos Hag / Mega Balsos)")
        st.rerun()

st.divider()

# --- MÉTRICAS DE INVENTARIO Y CONTEO DE PRODUCCIÓN ---
pedidos = st.session_state["historial_pedidos"]
pendientes = [p for p in pedidos if p["estado"] == "Pendiente"]
finalizados = [p for p in pedidos if p["estado"] == "Finalizado"]

stock_actual = st.session_state["stock_taller"]
collares_posibles = int((stock_actual / 100) * 20)

m1, m2, m3, m4 = st.columns(4)
m1.metric("Stock de Insumos", f"{stock_actual}%", f"~{collares_posibles} collares armables")
m2.metric("Pendientes por Tejer", f"{len(pendientes)}", f"{len(pendientes) * 30} min estimados")
m3.metric("Collares Finalizados", f"{len(finalizados)}", "Listos para entregar")
m4.metric("Total Sesión", f"{len(pedidos)} / 18", "Techo sano semanal")

st.progress(stock_actual / 100)

if stock_actual <= 20:
    st.error("🚨 **ALERTA DE RESTOCK (≤ 20%):** Comprar mostacillas en **Mega Balsos** e insumos en **Insumos Hag** ($120.000 COP mínimo).")
else:
    st.success(f"✅ **Inventario operativo ({stock_actual}%):** Suficiente para cubrir la producción en curso.")

st.divider()

# --- REGISTRO DE PENDIENTES VS FINALIZADOS ---
col_pend, col_done = st.columns(2)

with col_pend:
    st.subheader(f"⏳ Pendientes ({len(pendientes)})")
    if not pendientes:
        st.write("*No hay collares pendientes. Ordena uno en la Boutique para verlo aquí.*")
    else:
        for idx, p in enumerate(pedidos):
            if p["estado"] == "Pendiente":
                st.markdown(f"""
                <div class="pending-card">
                    <strong style="color:#F6EFA6 !important;">{p['pieza']}</strong><br>
                    <span>Clienta: {p['clienta']} · Entrega: {p['entrega']}</span>
                </div>
                """, unsafe_allow_html=True)
                if st.button("✅ Marcar como terminado", key=f"done_{idx}"):
                    st.session_state["historial_pedidos"][idx]["estado"] = "Finalizado"
                    st.rerun()

with col_done:
    st.subheader(f"✅ Finalizados ({len(finalizados)})")
    if not finalizados:
        st.write("*Aún no has finalizado collares en esta sesión.*")
    else:
        for p in reversed(finalizados):
            st.markdown(f"""
            <div class="done-card">
                <strong style="color:#6997BF !important;">{p['pieza']}</strong> · <span>${p['precio']:,} COP</span><br>
                <span>Clienta: {p['clienta']} · Punto: {p['entrega']}</span>
            </div>
            """, unsafe_allow_html=True)

st.divider()

# --- RESUMEN FINANCIERO (40 / 20 / COGS / REINVERSIÓN) ---
st.subheader("💰 Caja de la Sesión (Pedidos Registrados)")
ventas = sum(p["precio"] for p in pedidos)
cogs = sum(p["cogs"] for p in pedidos)
creadora = int(ventas * 0.40)
socio = int(ventas * 0.20)
reinversion = ventas - cogs - creadora - socio

f1, f2, f3, f4, f5 = st.columns(5)
f1.metric("Ingreso Bruto", f"${ventas:,}")
f2.metric("Mariangel (40%)", f"${creadora:,}")
f3.metric("Strategist (20%)", f"${socio:,}")
f4.metric("Reposición COGS", f"${cogs:,}")
f5.metric("Reinversión Hag", f"${reinversion:,}")
