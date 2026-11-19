import streamlit as st
import paho.mqtt.client as mqtt
import time

st.set_page_config(page_title="blueberry. | taller & stock", page_icon="🧵", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@300;400;500;600&family=Playfair+Display:ital,wght@0,500;0,600;1,400&display=swap');
    .stApp { background-color: #F4F1EA; color: #18222D; font-family: 'Montserrat', sans-serif; }
    h1, h2, h3 { font-family: 'Playfair Display', serif !important; color: #2A375A !important; }
    </style>
""", unsafe_allow_html=True)

BROKER = "broker.hivemq.com"
TOPIC_STATUS = "eafit2026/mariangel_blueberry_9842/status"

# Inicializar estado del taller
if "gramos_mostacilla" not in st.session_state:
    st.session_state["gramos_mostacilla"] = 180  # Alcanza para 18 collares (10g c/u)
if "estado_fisico" not in st.session_state:
    st.session_state["estado_fisico"] = "🟢 Taller listo y esperando orden"
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
    time.sleep(2.5)  # Ventana de escucha de 2.5 segundos
    client.loop_stop()
    client.disconnect()
    return mensajes

st.title("🧵 taller blueberry & control de inventario")
st.caption("Panel operativo de Mariangel · Sincronizado con hardware Wokwi y pedidos de boutique")

# --- BARRA DE SINCRONIZACIÓN CON HARDWARE (WOKWI) ---
col_sync1, col_sync2 = st.columns([2, 1])
with col_sync1:
    st.info("**Instrucción:** Mueve el potenciómetro en Wokwi (simula peso de frasco de mostacillas) o presiona el botón azul (collar terminado) y pulsa sincronizar:")
with col_sync2:
    if st.button("🔄 Sincronizar con Wokwi", type="primary", use_container_width=True):
        with st.spinner("Leyendo sensor de peso y botón en Wokwi..."):
            msgs = leer_hardware_wokwi()
            if msgs:
                for m in msgs:
                    if m.startswith("STOCK:"):
                        porcentaje = int(m.split(":")[1])
                        # 100% del frasco = 200 gramos de mostacillas
                        st.session_state["gramos_mostacilla"] = int((porcentaje / 100) * 200)
                    elif m == "ESTADO:LISTO":
                        st.session_state["estado_fisico"] = "✅ ¡Collar terminado! (Confirmado con botón físico en Wokwi)"
                        if st.session_state["historial_pedidos"]:
                            st.session_state["historial_pedidos"][-1]["estado"] = "✅ Listo para entregar"
                st.toast("¡Datos actualizados desde Wokwi!")
            else:
                st.warning("No hubo movimiento nuevo en Wokwi. Gira el potenciómetro o presiona el botón azul justo antes de sincronizar.")

st.divider()

# --- MÉTRICAS REALES DE INVENTARIO Y CAPACIDAD ---
pedidos = st.session_state["historial_pedidos"]
gramos_descontados_pedidos = len(pedidos) * 10
gramos_disponibles = max(0, st.session_state["gramos_mostacilla"] - gramos_descontados_pedidos)
collares_posibles = gramos_disponibles // 10

m1, m2, m3, m4 = st.columns(4)
m1.metric("Mostacillas en Frasco", f"{gramos_disponibles} g", f"-{gramos_descontados_pedidos}g por pedidos")
m2.metric("Capacidad Restante", f"{collares_posibles} collares", "10g por unidad")
m3.metric("Pedidos Activos", f"{len(pedidos)} / 18", "Techo sano semanal")
m4.metric("Tiempo Estimado Cola", f"{len(pedidos) * 30} min", "30 min/collar")

st.progress(min(1.0, gramos_disponibles / 200))

if collares_posibles <= 4:
    st.error("🚨 **ALERTA DE RESTOCK URGENTE:** Quedan insumos para 4 collares o menos. Comprar crema perlada, vinotinto y negro en **Mega Balsos / Insumos Hag** ($120.000 COP pedido mínimo).")
else:
    st.success("✅ **Inventario saludable:** Material suficiente en taller para cubrir los pedidos activos.")

st.divider()

# --- COLA DE PRODUCCIÓN Y GOBERNANZA FINANCIERA (40/20/COGS/REINVERSIÓN) ---
c_left, c_right = st.columns([1.3, 1])

with c_left:
    st.subheader("📋 Cola de Ensamble en Vivo")
    st.write(f"**Estado del puesto de trabajo:** {st.session_state['estado_fisico']}")
    
    if not pedidos:
        st.caption("Aún no hay pedidos en cola. Ve a la página principal y ordena un collar para verlo aparecer aquí.")
    else:
        for i, p in enumerate(reversed(pedidos), 1):
            with st.container(border=True):
                st.markdown(f"**#{len(pedidos)-i+1} · {p['pieza']}** — *{p['uso']}*")
                st.caption(f"Clienta: {p['clienta']} | Entrega: {p['entrega']} | Estado: {p['estado']}")

with c_right:
    st.subheader("💰 Caja & Gobernanza Financiera")
    ventas_totales = sum(p["precio"] for p in pedidos)
    cogs_total = sum(p["cogs"] for p in pedidos)
    utilidad_mariangel = int(ventas_totales * 0.40)
    comision_strategist = int(ventas_totales * 0.20)
    fondo_reinversion = ventas_totales - cogs_total - utilidad_mariangel - comision_strategist

    st.metric("Ingresos Brutos Sesión", f"${ventas_totales:,} COP")
    st.write(f"• **Tu Utilidad (40% Creadora):** `${utilidad_mariangel:,} COP`")
    st.write(f"• **Insta Strategist (20%):** `${comision_strategist:,} COP`")
    st.write(f"• **Reposición Insumos (COGS):** `${cogs_total:,} COP`")
    st.write(f"• **Fondo Reinversión (Meta $120k Hag):** `${fondo_reinversion:,} COP`")
    
    if st.button("🧪 Simular Restock (+200g Mostacillas)"):
        st.session_state["gramos_mostacilla"] = 200
        st.session_state["historial_pedidos"] = []
        st.rerun()
