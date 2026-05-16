# =========================================================
# GPX.py
# Streamlit GPS Tracker
# Compatible with Streamlit Cloud
# =========================================================

import streamlit as st
import pandas as pd
from datetime import datetime
import time
import random

# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="GPS Tracker",
    page_icon="📍",
    layout="wide"
)

# =========================================================
# GPS FUNCTION
# =========================================================
# SOSTITUISCI questa funzione con il tuo GPS reale
# se usi hardware GPS o API esterne.
# Questa versione genera coordinate simulate.

def get_position():

    base_lat = 41.9028
    base_lon = 12.4964

    lat = base_lat + random.uniform(-0.0005, 0.0005)
    lon = base_lon + random.uniform(-0.0005, 0.0005)

    return lat, lon


# =========================================================
# SESSION STATE INIT
# =========================================================

if "tracking" not in st.session_state:
    st.session_state.tracking = False

if "gps_data" not in st.session_state:
    st.session_state.gps_data = []

if "refresh_rate" not in st.session_state:
    st.session_state.refresh_rate = 1


# =========================================================
# HEADER
# =========================================================

st.title("📍 GPS Tracker")
st.markdown("Tracking continuo posizione con export CSV")


# =========================================================
# SIDEBAR
# =========================================================

st.sidebar.header("⚙️ Configurazione")

refresh_rate = st.sidebar.slider(
    "Intervallo aggiornamento (secondi)",
    min_value=1,
    max_value=10,
    value=1
)

st.session_state.refresh_rate = refresh_rate


# =========================================================
# BUTTONS
# =========================================================

col1, col2, col3 = st.columns(3)

with col1:

    if st.button("▶️ START TRACKING", use_container_width=True):
        st.session_state.tracking = True

with col2:

    if st.button("⏹️ STOP TRACKING", use_container_width=True):
        st.session_state.tracking = False

with col3:

    if st.button("🗑️ CLEAR DATA", use_container_width=True):
        st.session_state.gps_data = []


# =========================================================
# STATUS
# =========================================================

if st.session_state.tracking:
    st.success("🟢 Tracking ATTIVO")
else:
    st.warning("🔴 Tracking FERMO")


# =========================================================
# TRACKING LOOP
# =========================================================

if st.session_state.tracking:

    lat, lon = get_position()

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    row = {
        "timestamp": timestamp,
        "latitude": lat,
        "longitude": lon
    }

    st.session_state.gps_data.append(row)

    # Limite sicurezza memoria
    MAX_POINTS = 10000

    if len(st.session_state.gps_data) > MAX_POINTS:
        st.session_state.gps_data.pop(0)

    # Attesa
    time.sleep(st.session_state.refresh_rate)

    # Refresh automatico
    st.rerun()


# =========================================================
# DATAFRAME
# =========================================================

df = pd.DataFrame(st.session_state.gps_data)

st.subheader("📋 Posizioni Registrate")

st.dataframe(
    df,
    use_container_width=True,
    height=500
)


# =========================================================
# METRICS
# =========================================================

if not df.empty:

    latest = df.iloc[-1]

    m1, m2, m3 = st.columns(3)

    with m1:
        st.metric("Ultima Latitudine", f"{latest['latitude']:.6f}")

    with m2:
        st.metric("Ultima Longitudine", f"{latest['longitude']:.6f}")

    with m3:
        st.metric("Punti Registrati", len(df))


# =========================================================
# MAPPA
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
# FOOTER
# =========================================================

st.markdown("---")
st.caption("Streamlit GPS Tracker • Ready for Streamlit Cloud")
