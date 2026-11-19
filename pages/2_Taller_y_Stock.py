import streamlit as st
import paho.mqtt.client as mqtt
import time

st.set_page_config(page_title="Blueberry · Taller & Stock", page_icon="🧵", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #F4F1EA; color: #18222D; }
    h1, h2, h3 { color: #2A375A !important; font-family: Georgia, serif; }
    </style>
""", unsafe_allow_html=True)

TOPIC_STATUS = "eafit2026/mariangel_blueberry_9842/status"
TOPIC_CMD = "eafit2026/mariangel_blueberry_9842/cmd"

if "stock_actual" not in st.session_state:
    st.session_state["stock_actual"] = 80
if "estado_taller" not in st.session_state:
    st.session_state["estado_taller"] = "⏳ Esperando actividad en Wokwi..."

def leer_mensajes_wokwi():
    mensajes_recibidos = []
    def on_message(client, userdata, msg):
        mensajes_recibidos.append(msg.payload.decode())

    client = mqtt.Client(client_id=f"Streamlit_Taller_{int(time.time())}")
    client.on_message = on_message
    client.connect("broker.hivemq.com", 1883, 60)
    client.subscribe(TOPIC_STATUS)
    client.loop_start()
    time.sleep(2.0)  # Escucha durante 2 segundos
    client.loop_stop()
    client.disconnect()
    return mensajes_recibidos

st.title("🧵 ambiente 2: taller de producción & control físico")
st.markdown("Panel operativo de Mariangel conectado bidireccionalmente con **Wokwi** y **MyMQTT**.")
st.divider()

col1, col2 = st.columns(2)

with col1:
    st.subheader("📦 Sensor Físico de Stock (Potenciómetro Wokwi)")
    st.write("Mueve el potenciómetro en Wokwi o presiona el botón azul y haz clic en sincronizar:")
    
    if st.button("🔄 Leer Sensores de Wokwi Ahora", type="primary"):
        with st.spinner("Escuchando señal desde Wokwi..."):
            msgs = leer_mensajes_wokwi()
            if msgs:
                for m in msgs:
                    if m.startswith("STOCK:"):
                        st.session_state["stock_actual"] = int(m.split(":")[1])
                    elif m == "ESTADO:LISTO":
                        st.session_state["estado_taller"] = "✅ ¡Collar terminado! (Botón físico presionado en Wokwi)"
                    elif m.startswith("TALLER_OK:"):
                        st.session_state["estado_taller"] = f"🔨 {m.split(':')[1]}"
            else:
                st.toast("No llegaron cambios nuevos en los últimos 2 segundos. Mueve el potenciómetro en Wokwi y vuelve a intentar.")

    nivel = st.session_state["stock_actual"]
    st.metric("Nivel de Mostacillas y Perlas", f"{nivel}%")
    st.progress(nivel / 100)

    if nivel < 25:
        st.error("🚨 ALERTA DE RESTOCK: Nivel crítico (<25%). Programar compra mínima de $120.000 COP en Insumos Hag.")
    else:
        st.success("✅ Inventario saludable para cubrir la meta de 16–18 collares/semana.")

with col2:
    st.subheader("🔔 Control de Producción y Entrega")
    st.info(st.session_state["estado_taller"])
    
    st.markdown("""
    **Gobernanza Operativa Blueberry:**
    * **Tiempo estándar de ensamble:** 30 min / collar.
    * **Costo directo (COGS):** $6.000 COP / unidad.
    * **Entrega local:** Portería Universidad EAFIT.
    """)
    
    if st.button("🧪 Enviar Prueba de Alerta al Hardware"):
        client = mqtt.Client(client_id=f"Streamlit_Test_{int(time.time())}")
        client.connect("broker.hivemq.com", 1883, 60)
        client.publish(TOPIC_CMD, "PEDIDO:Prueba Taller:180")
        client.disconnect()
        st.success("Señal de prueba enviada a Wokwi y MyMQTT.")
