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
# STATE
# =========================================================

if "tracking" not in st.session_state:
    st.session_state.tracking = False

if "data" not in st.session_state:
    st.session_state.data = []

if "last_sample" not in st.session_state:
    st.session_state.last_sample = 0

# =========================================================
# UI
# =========================================================

st.title("📍 GPS Tracker (Streamlit Cloud Safe)")

interval = st.sidebar.slider("Campionamento (sec)", 1, 120, 20)

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

st.write("Status:", "🟢 RUNNING" if st.session_state.tracking else "🔴 STOPPED")

# =========================================================
# GPS HTML (ONLY SOURCE OF TRUTH)
# =========================================================

gps_html = """
<script>
navigator.geolocation.getCurrentPosition(
    function(pos) {
        const data = {
            lat: pos.coords.latitude,
            lon: pos.coords.longitude,
            acc: pos.coords.accuracy
        };

        // salva in localStorage (Streamlit può leggerlo indirettamente)
        localStorage.setItem("gps_data", JSON.stringify(data));
    },
    function(err) {
        console.log(err);
    },
    { enableHighAccuracy: true }
);
</script>
"""

components.html(gps_html, height=0)

# =========================================================
# READ GPS FROM LOCAL STORAGE VIA HTML POLLING
# =========================================================

gps_reader = components.html("""
<script>
function sendToStreamlit() {
    const data = localStorage.getItem("gps_data");
    if (data) {
        document.title = data; // hack semplice ma stabile
    }
}
setInterval(sendToStreamlit, 1000);
</script>
""", height=0)

# =========================================================
# MANUAL INPUT FALLBACK (WORKING PART)
# =========================================================

gps_raw = st.text_input("GPS RAW (auto fallback / debug)")

gps = None

if gps_raw:
    try:
        import json
        gps = json.loads(gps_raw)
    except:
        pass

# =========================================================
# TRACKING LOGIC
# =========================================================

now = time.time()

if st.session_state.tracking and gps:

    if now - st.session_state.last_sample >= interval:

        st.session_state.data.append({
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "latitude": gps["lat"],
            "longitude": gps["lon"],
            "accuracy": gps["acc"]
        })

        st.session_state.last_sample = now

# =========================================================
# TABLE LIVE (FIXED)
# =========================================================

df = pd.DataFrame(st.session_state.data)

st.subheader("📋 Posizioni Registrate (LIVE)")

st.dataframe(df, use_container_width=True)

# =========================================================
# METRICS
# =========================================================

if not df.empty:
    last = df.iloc[-1]

    c1, c2, c3 = st.columns(3)

    with c1:
        st.metric("Lat", last["latitude"])

    with c2:
        st.metric("Lon", last["longitude"])

    with c3:
        st.metric("Punti", len(df))

# =========================================================
# MAP
# =========================================================

if not df.empty:
    st.map(df.rename(columns={"latitude": "lat", "longitude": "lon"}))

# =========================================================
# DOWNLOAD CSV
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
