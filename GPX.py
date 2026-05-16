# =========================================================
# GPX.py
# Streamlit Mobile GPS Tracker
# Compatible with Streamlit Cloud
# =========================================================

import streamlit as st
import pandas as pd
from datetime import datetime
import time
import streamlit.components.v1 as components

# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="Mobile GPS Tracker",
    page_icon="📍",
    layout="wide"
)

# =========================================================
# SESSION STATE
# =========================================================

if "tracking" not in st.session_state:
    st.session_state.tracking = False

if "gps_data" not in st.session_state:
    st.session_state.gps_data = []

if "last_sample_time" not in st.session_state:
    st.session_state.last_sample_time = 0

if "latest_position" not in st.session_state:
    st.session_state.latest_position = None


# =========================================================
# TITLE
# =========================================================

st.title("📍 Mobile GPS Tracker")

st.markdown("""
Questa app legge il GPS direttamente dal telefono/browser.

⚠️ IMPORTANTE:
- Apri da smartphone
- Consenti accesso alla posizione
- Tieni aperta la pagina durante il tracking
""")


# =========================================================
# SIDEBAR
# =========================================================

st.sidebar.header("⚙️ Configurazione")

sample_interval = st.sidebar.slider(
    "Campionamento GPS (secondi)",
    min_value=1,
    max_value=300,
    value=20,
    step=1
)

st.sidebar.write(f"Intervallo corrente: {sample_interval} sec")


# =========================================================
# GPS JAVASCRIPT COMPONENT
# =========================================================

gps_component = components.html(
    """
    <script>

    function sendPosition(position) {

        const coords = {
            latitude: position.coords.latitude,
            longitude: position.coords.longitude,
            accuracy: position.coords.accuracy,
            timestamp: new Date().toISOString()
        };

        const streamlitDoc = window.parent.document;

        const textArea = streamlitDoc.querySelector('textarea');

        if (textArea) {
            textArea.value = JSON.stringify(coords);
            textArea.dispatchEvent(new Event("input", { bubbles: true }));
        }
    }

    function errorHandler(error) {
        console.log(error);
    }

    if (navigator.geolocation) {

        navigator.geolocation.watchPosition(
            sendPosition,
            errorHandler,
            {
                enableHighAccuracy: true,
                maximumAge: 0,
                timeout: 10000
            }
        );

    }

    </script>
    """,
    height=0,
)


# =========================================================
# HIDDEN INPUT
# =========================================================

gps_raw = st.text_area(
    "gps_hidden",
    key="gps_hidden",
    label_visibility="collapsed"
)

# =========================================================
# BUTTONS
# =========================================================

col1, col2, col3 = st.columns(3)

with col1:

    if st.button("▶️ START", use_container_width=True):
        st.session_state.tracking = True

with col2:

    if st.button("⏹️ STOP", use_container_width=True):
        st.session_state.tracking = False

with col3:

    if st.button("🗑️ CLEAR", use_container_width=True):
        st.session_state.gps_data = []


# =========================================================
# STATUS
# =========================================================

if st.session_state.tracking:
    st.success("🟢 Tracking attivo")
else:
    st.warning("🔴 Tracking fermo")


# =========================================================
# GPS PARSING
# =========================================================

if gps_raw:

    try:

        import json

        gps = json.loads(gps_raw)

        st.session_state.latest_position = gps

    except:
        pass


# =========================================================
# TRACKING
# =========================================================

if (
    st.session_state.tracking
    and st.session_state.latest_position is not None
):

    current_time = time.time()

    elapsed = current_time - st.session_state.last_sample_time

    if elapsed >= sample_interval:

        gps = st.session_state.latest_position

        row = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "latitude": gps["latitude"],
            "longitude": gps["longitude"],
            "accuracy_m": round(gps["accuracy"], 2)
        }

        st.session_state.gps_data.append(row)

        st.session_state.last_sample_time = current_time


# =========================================================
# DATAFRAME LIVE
# =========================================================

df = pd.DataFrame(st.session_state.gps_data)

st.subheader("📋 Posizioni Registrate")

table_placeholder = st.empty()

with table_placeholder:

    st.dataframe(
        df,
        use_container_width=True,
        height=400
    )


# =========================================================
# LIVE METRICS
# =========================================================

if not df.empty:

    latest = df.iloc[-1]

    m1, m2, m3, m4 = st.columns(4)

    with m1:
        st.metric("Latitudine", f"{latest['latitude']:.6f}")

    with m2:
        st.metric("Longitudine", f"{latest['longitude']:.6f}")

    with m3:
        st.metric("Accuratezza", f"{latest['accuracy_m']} m")

    with m4:
        st.metric("Punti", len(df))


# =========================================================
# MAP
# =========================================================

if not df.empty:

    st.subheader("🗺️ Mappa")

    map_df = df.rename(
        columns={
            "latitude": "lat",
            "longitude": "lon"
        }
    )

    st.map(map_df)


# =========================================================
# DOWNLOAD CSV
# =========================================================

if not df.empty:

    csv = df.to_csv(index=False).encode("utf-8")

    st.download_button(
        label="⬇️ Download CSV",
        data=csv,
        file_name=f"gps_tracking_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
        mime="text/csv",
        use_container_width=True
    )


# =========================================================
# AUTO REFRESH
# =========================================================

if st.session_state.tracking:
    time.sleep(1)
    st.rerun()


# =========================================================
# FOOTER
# =========================================================

st.markdown("---")

st.caption("📱 Mobile GPS Tracker • Streamlit Cloud Ready")
