import streamlit as st
import paho.mqtt.client as mqtt
import time

st.set_page_config(page_title="blueberry. | mesa de taller", page_icon="🪡", layout="wide")

# Estética Modo Taller Artesanal (Ink Black + Blueberry Indigo + Vanilla Custard)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@300;400;500;600&family=Playfair+Display:ital,wght@0,500;0,600;1,400&display=swap');
    
    .stApp {
        background-color: #18222D;
        color: #FAF5F5;
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
    .workshop-banner {
        background-color: #2A375A;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 5px solid #F6EFA6;
        margin-bottom: 1.5rem;
    }
    .order-card {
        background-color: #2A375A;
        padding: 1rem 1.2rem;
        border-radius: 8px;
        border: 1px solid #6997BF;
        margin-bottom: 0.8rem;
    }
    </style>
""", unsafe_allow_html=True)

BROKER = "broker.hivemq.com"
TOPIC_STATUS = "eafit2026/mariangel_blueberry_9842/status"

# Stock en pasos de 20 en 20 (0, 20, 40, 60, 80, 100)
if "stock_taller" not in st.session_state:
    st.session_state["stock_taller"] = 80
if "estado_mesa" not in st.session_state:
    st.session_state["estado_mesa"] = "🟢 Mesa de trabajo lista"
if "historial_pedidos" not in st.session_state:
    st.session_state["historial_pedidos"] = []

def leer_hardware_wokwi():
    mensajes = []
    def on_message(client, userdata, msg):
        mensajes.append(msg.payload.decode())

    client = mqtt.Client(client_id=f"BB_Taller_{int(time.time())}")
    client.on_message = on_message
    client.connect(BROKER, 1883, 60)
    client.subscribe(TOPIC_STATUS)
    client.loop_start()
    time.sleep(2.0)
    client.loop_stop()
    client.disconnect()
    return mensajes

# --- ENCABEZADO MESA DE TALLER ---
st.markdown("""
<div class="workshop-banner">
    <h1 style="margin:0;">🪡 mesa de taller · blueberry studio</h1>
    <p style="color:#6997BF !important; font-style:italic; margin-top:0.3rem; margin-bottom:0;">
        control artesanal de insumos (mostacillas, perlas & nailon) · sincronizado con Wokwi
    </p>
</div>
""", unsafe_allow_html=True)

# --- CONTROL DE STOCK DE 20 EN 20 (FÍSICO Y DIGITAL) ---
col_sync, col_manual = st.columns([2, 1.5])

with col_sync:
    st.write("**Sincronización con Hardware (Wokwi):** Mueve el potenciómetro (salta de 20 en 20) o presiona el botón azul de *Pedido Listo*:")
    if st.button("🔄 Leer Sensor y Botón de Wokwi", type="primary", use_container_width=True):
        with st.spinner("Conectando con la mesa física..."):
            msgs = leer_hardware_wokwi()
            if msgs:
                for m in msgs:
                    if m.startswith("STOCK:"):
                        val = int(m.split(":")[1])
                        # Asegurar múltiplo exacto de 20
                        st.session_state["stock_taller"] = round(val / 20) * 20
                    elif m == "ESTADO:LISTO":
                        st.session_state["estado_mesa"] = "✅ ¡Pieza terminada! (Botón físico presionado)"
                        if st.session_state["historial_pedidos"]:
                            st.session_state["historial_pedidos"][-1]["estado"] = "✅ Listo para entregar"
                st.toast("¡Datos del taller actualizados!")
            else:
                st.warning("No hubo cambios nuevos. Mueve el potenciómetro o presiona el botón azul en Wokwi y vuelve a pulsar.")

with col_manual:
    st.write("**Ajuste rápido de frasco (20 en 20):**")
    b1, b2 = st.columns(2)
    with b1:
        if st.button("➖ Gastar 20%", use_container_width=True):
            st.session_state["stock_taller"] = max(0, st.session_state["stock_taller"] - 20)
            st.rerun()
    with b2:
        if st.button("➕ Reponer 20%", use_container_width=True):
            st.session_state["stock_taller"] = min(100, st.session_state["stock_taller"] + 20)
            st.rerun()

st.divider()

# --- MÉTRICAS DE TALLER ---
pedidos = st.session_state["historial_pedidos"]
stock_actual = st.session_state["stock_taller"]
collares_estimados = (stock_actual // 20) * 4  # Cada 20% alcanza para 4 collares (100% = 20 collares)

m1, m2, m3, m4 = st.columns(4)
m1.metric("Frasco de Mostacillas", f"{stock_actual}%", "Pasos de 20%")
m2.metric("Collares Armables", f"{collares_estimados} und.", "4 collares por cada 20%")
m3.metric("Pedidos en Cola", f"{len(pedidos)} / 18", "Techo sano semanal")
m4.metric("Tiempo de Ensamble", f"{len(pedidos) * 30} min", "30 min por pieza")

st.progress(stock_actual / 100)

if stock_actual <= 20:
    st.error("🚨 **ALERTA DE TALLER (≤ 20%):** Quedan insumos para 4 collares o menos. Ir a **Mega Balsos / Insumos Hag** ($120.000 COP mínimo).")
else:
    st.success(f"✅ **Stock operativo ({stock_actual}%):** Insumos listos en mesa para tejer.")

st.divider()

# --- COLA DE PRODUCCIÓN Y CAJA ---
c_left, c_right = st.columns([1.3, 1])

with c_left:
    st.subheader("📋 Órdenes en Mesa de Trabajo")
    st.write(f"**Estado actual:** {st.session_state['estado_mesa']}")
    
    if not pedidos:
        st.write("*No hay collares pendientes por tejer. Cuando una clienta ordene en la Boutique, aparecerá aquí.*")
    else:
        for i, p in enumerate(reversed(pedidos), 1):
            st.markdown(f"""
            <div class="order-card">
                <strong style="color:#F6EFA6 !important;">#{len(pedidos)-i+1} · {p['pieza']}</strong><br>
                <span>Clienta: {p['clienta']} · Entrega: {p['entrega']}</span><br>
                <span style="color:#6997BF !important; font-size:0.85rem;">Estado: {p['estado']}</span>
            </div>
            """, unsafe_allow_html=True)

with c_right:
    st.subheader("💰 Reparto de Caja (40 / 20 / COGS)")
    ventas = sum(p["precio"] for p in pedidos)
    cogs = sum(p["cogs"] for p in pedidos)
    creadora = int(ventas * 0.40)
    socio = int(ventas * 0.20)
    reinversion = ventas - cogs - creadora - socio

    st.metric("Ventas de la Sesión", f"${ventas:,} COP")
    st.markdown(f"""
    * **Utilidad Mariangel (40%):** `${creadora:,} COP`
    * **Insta Strategist (20%):** `${socio:,} COP`
    * **Reposición Materiales (COGS):** `${cogs:,} COP`
    * **Fondo Reinversión (Meta $120k Hag):** `${reinversion:,} COP`
    """)
