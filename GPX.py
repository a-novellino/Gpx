# =========================================================
# GPX.py
# REAL MOBILE GPS TRACKER
# Streamlit Cloud Compatible
# =========================================================

import streamlit as st
import pandas as pd
import time
from datetime import datetime
from streamlit_js_eval import streamlit_js_eval

# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="GPS Tracker",
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

if "last_sample" not in st.session_state:
    st.session_state.last_sample = 0

# =========================================================
# TITLE
# =========================================================

st.title("📍 Mobile GPS Tracker")

st.markdown("""
Usa il GPS reale del telefono.

### IMPORTANTE
- Apri da smartphone
- Consenti accesso GPS
- Lascia la pagina aperta
""")

# =========================================================
# SIDEBAR
# =========================================================

st.sidebar.header("⚙️ Configurazione")

sample_interval = st.sidebar.slider(
    "Campionamento (secondi)",
    min_value=1,
    max_value=300,
    value=20,
    step=1
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
# GPS READ
# =========================================================

gps = streamlit_js_eval(
    js_expressions="""
    new Promise((resolve, reject) => {
        navigator.geolocation.getCurrentPosition(
            (pos) => resolve({
                latitude: pos.coords.latitude,
                longitude: pos.coords.longitude,
                accuracy: pos.coords.accuracy
            }),
            (err) => resolve(null),
            {
                enableHighAccuracy: true,
                timeout: 10000,
                maximumAge: 0
            }
        );
    })
    """,
    key="gps"
)

# =========================================================
# TRACKING
# =========================================================

if st.session_state.tracking and gps is not None:

    current_time = time.time()

    elapsed = current_time - st.session_state.last_sample

    if elapsed >= sample_interval:

        row = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "latitude": gps["latitude"],
            "longitude": gps["longitude"],
            "accuracy_m": round(gps["accuracy"], 2)
        }

        st.session_state.gps_data.append(row)

        st.session_state.last_sample = current_time

# =========================================================
# DATAFRAME LIVE
# =========================================================

df = pd.DataFrame(st.session_state.gps_data)

st.subheader("📋 Posizioni Registrate")

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

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        st.metric("Latitudine", f"{latest['latitude']:.6f}")

    with c2:
        st.metric("Longitudine", f"{latest['longitude']:.6f}")

    with c3:
        st.metric("Accuratezza", f"{latest['accuracy_m']} m")

    with c4:
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
st.caption("📍 Streamlit Mobile GPS Tracker")
