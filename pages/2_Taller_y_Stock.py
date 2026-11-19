import streamlit as st
import paho.mqtt.client as mqtt
import time

st.set_page_config(page_title="Blueberry · Taller", page_icon="🧵", layout="centered")

BROKER = "broker.hivemq.com"
TOPIC_STATUS = "eafit2026/mariangel_blueberry_9842/status"

if "stock" not in st.session_state:
    st.session_state["stock"] = 70
if "estado_pedido" not in st.session_state:
    st.session_state["estado_pedido"] = "En espera de confirmación en taller"

def sincronizar_wokwi():
    mensajes = []
    def on_message(client, userdata, msg):
        mensajes.append(msg.payload.decode())

    client = mqtt.Client(client_id=f"SB_Taller_{int(time.time())}")
    client.on_message = on_message
    client.connect(BROKER, 1883, 60)
    client.subscribe(TOPIC_STATUS)
    client.loop_start()
    time.sleep(1.5)
    client.loop_stop()
    client.disconnect()
    return mensajes

# --- INTERFAZ LIMPIA ---
st.title("🧵 Taller Blueberry")
st.caption("Ambiente 2 · Control de producción e inventario conectado a Wokwi")
st.markdown("**¿Para qué sirve esta pantalla?** Permite monitorear desde el taller cuántos insumos quedan (potenciómetro en Wokwi) y confirmar cuando un collar está terminado (botón físico en Wokwi).")

st.divider()

# BOTÓN ÚNICO DE SINCRONIZACIÓN
if st.button("🔄 Actualizar datos desde Wokwi", type="primary", use_container_width=True):
    with st.spinner("Leyendo sensores físicos..."):
        recibidos = sincronizar_wokwi()
        if recibidos:
            for m in recibidos:
                if m.startswith("STOCK:"):
                    st.session_state["stock"] = int(m.split(":")[1])
                elif m == "ESTADO:LISTO":
                    st.session_state["estado_pedido"] = "✅ Collar terminado y listo para entregar en EAFIT"
                elif m.startswith("TALLER_OK:"):
                    st.session_state["estado_pedido"] = f"🔨 {m.split(':')[1]}"
        else:
            st.toast("Mueve el potenciómetro o presiona el botón azul en Wokwi y vuelve a darle actualizar.")

st.write("")

col1, col2 = st.columns(2)

with col1:
    st.subheader("📦 Insumos (Mostacillas y Perlas)")
    nivel = st.session_state["stock"]
    st.metric("Nivel actual en taller", f"{nivel}%")
    st.progress(nivel / 100)
    
    if nivel <= 25:
        st.error("⚠️ **Stock bajo:** Hacer pedido mínimo ($120.000 COP) en Insumos Hag.")
    else:
        st.success("✅ Material suficiente para producción semanal.")

with col2:
    st.subheader("🔔 Estado del Pedido")
    ultimo = st.session_state.get("ultimo_pedido", "Ningún pedido enviado aún desde la Vitrina")
    st.write(f"**Última orden:** {ultimo}")
    st.info(st.session_state["estado_pedido"])
