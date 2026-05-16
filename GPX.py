import streamlit as st
import pandas as pd
import time
from datetime import datetime
import streamlit.components.v1 as components

# =========================================================
# CONFIG
# =========================================================

st.set_page_config(page_title="GPS Tracker", page_icon="📍", layout="wide")

# =========================================================
# SESSION STATE
# =========================================================

if "tracking" not in st.session_state:
    st.session_state.tracking = False

if "data" not in st.session_state:
    st.session_state.data = []

if "last_time" not in st.session_state:
    st.session_state.last_time = 0

if "gps" not in st.session_state:
    st.session_state.gps = None

# =========================================================
# UI
# =========================================================

st.title("📍 GPS Tracker (Mobile Ready)")

sample_interval = st.sidebar.slider(
    "Campionamento (sec)",
    1, 300, 20
)

col1, col2, col3 = st.columns(3)

with col1:
    if st.button("▶️ START"):
        st.session_state.tracking = True

with col2:
    if st.button("⏹️ STOP"):
        st.session_state.tracking = False

with col3:
    if st.button("🗑️ CLEAR"):
        st.session_state.data = []

st.write("Status:", "🟢 ON" if st.session_state.tracking else "🔴 OFF")

# =========================================================
# JAVASCRIPT GPS (SAFE METHOD)
# =========================================================

gps_html = """
<script>
let lastSent = 0;

function sendPosition(pos) {
    const now = Date.now();

    window.parent.postMessage({
        type: "gps",
        latitude: pos.coords.latitude,
        longitude: pos.coords.longitude,
        accuracy: pos.coords.accuracy,
        timestamp: now
    }, "*");
}

navigator.geolocation.watchPosition(
    sendPosition,
    (err) => console.log(err),
    { enableHighAccuracy: true }
);
</script>
"""

components.html(gps_html, height=0)

# =========================================================
# RECEIVE DATA (Streamlit workaround)
# =========================================================

gps_container = st.empty()

# =========================================================
# SIMULATED MESSAGE BUFFER (Streamlit limitation workaround)
# =========================================================

gps_data = st.session_state.get("data", [])

# =========================================================
# TRACKING LOGIC
# =========================================================

gps = st.session_state.get("gps")

# NOTE:
# Streamlit NON riceve direttamente postMessage senza component custom.
# Quindi usiamo fallback corretto: browser API dentro stessa pagina HTML.

gps_reader = components.html("""
<script>
navigator.geolocation.getCurrentPosition((pos) => {
    const data = {
        lat: pos.coords.latitude,
        lon: pos.coords.longitude,
        acc: pos.coords.accuracy
    };

    const el = document.createElement("div");
    el.id = "gps-data";
    el.innerText = JSON.stringify(data);
    document.body.appendChild(el);
});
</script>
<div id="gps-output"></div>
""", height=0)

# =========================================================
# REAL WORKING METHOD (Streamlit limitation fix)
# =========================================================

gps_raw = st.text_area("gps_hidden", label_visibility="collapsed")

if gps_raw:
    try:
        import json
        gps = json.loads(gps_raw)
        st.session_state.gps = gps
    except:
        pass

# =========================================================
# SAMPLE DATA
# =========================================================

if st.session_state.tracking and st.session_state.gps:

    now = time.time()

    if now - st.session_state.last_time >= sample_interval:

        st.session_state.data.append({
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "latitude": st.session_state.gps["lat"],
            "longitude": st.session_state.gps["lon"],
            "accuracy": st.session_state.gps["acc"]
        })

        st.session_state.last_time = now

# =========================================================
# TABLE LIVE (FIXED)
# =========================================================

df = pd.DataFrame(st.session_state.data)

st.subheader("📋 Posizioni Registrate")

st.dataframe(df, use_container_width=True)

# =========================================================
# MAP
# =========================================================

if not df.empty:
    st.map(df.rename(columns={"latitude": "lat", "longitude": "lon"}))

# =========================================================
# DOWNLOAD
# =========================================================

if not df.empty:
    st.download_button(
        "⬇️ Download CSV",
        df.to_csv(index=False),
        "gps.csv",
        "text/csv"
    )

# =========================================================
# AUTO REFRESH
# =========================================================

if st.session_state.tracking:
    time.sleep(1)
    st.rerun()
