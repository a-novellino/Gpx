import streamlit as st
import pandas as pd
import time
import json
import streamlit.components.v1 as components
from datetime import datetime

# =========================================================
# CONFIG
# =========================================================

st.set_page_config(page_title="GPS Tracker", page_icon="📍", layout="wide")

# =========================================================
# STATE
# =========================================================

if "data" not in st.session_state:
    st.session_state.data = []

if "tracking" not in st.session_state:
    st.session_state.tracking = False

if "last_time" not in st.session_state:
    st.session_state.last_time = 0

# =========================================================
# TITLE
# =========================================================

st.title("📍 GPS Tracker semplice")

st.markdown("Apri da smartphone e consenti posizione")

# =========================================================
# CONTROLS
# =========================================================

col1, col2, col3 = st.columns(3)

with col1:
    if st.button("START"):
        st.session_state.tracking = True

with col2:
    if st.button("STOP"):
        st.session_state.tracking = False

with col3:
    if st.button("CLEAR"):
        st.session_state.data = []

interval = st.slider("Campionamento (sec)", 5, 60, 20)

st.write("Stato:", "🟢 ON" if st.session_state.tracking else "🔴 OFF")

# =========================================================
# GPS JS (scrive in localStorage)
# =========================================================

components.html(
"""
<script>
function savePosition(pos) {
    const data = {
        lat: pos.coords.latitude,
        lon: pos.coords.longitude,
        acc: pos.coords.accuracy,
        time: new Date().toISOString()
    };
    localStorage.setItem("gps", JSON.stringify(data));
}

navigator.geolocation.watchPosition(
    savePosition,
    (err) => console.log(err),
    { enableHighAccuracy: true }
);
</script>
""",
height=0
)

# =========================================================
# READ GPS FROM localStorage (simple input bridge)
# =========================================================

gps_raw = st.text_input("gps_bridge", label_visibility="collapsed")

gps = None

if gps_raw:
    try:
        gps = json.loads(gps_raw)
    except:
        pass

# =========================================================
# SAVE DATA
# =========================================================

now = time.time()

if st.session_state.tracking and gps:

    if now - st.session_state.last_time >= interval:

        st.session_state.data.append({
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "latitude": gps["lat"],
            "longitude": gps["lon"],
            "accuracy": gps["acc"]
        })

        st.session_state.last_time = now

# =========================================================
# TABLE LIVE
# =========================================================

df = pd.DataFrame(st.session_state.data)

st.subheader("📋 Posizioni salvate")

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
    time.sleep(2)
    st.rerun()
