import streamlit as st
import pandas as pd
import time
from datetime import datetime
from streamlit_geolocation import streamlit_geolocation

st.title("GPS Logger")

# Stato sessione
if "tracking" not in st.session_state:
    st.session_state.tracking = False

if "data" not in st.session_state:
    st.session_state.data = []

# Intervallo
interval = st.number_input(
    "Intervallo acquisizione (secondi)",
    min_value=5,
    value=60
)

col1, col2 = st.columns(2)

with col1:
    if st.button("START"):
        st.session_state.tracking = True

with col2:
    if st.button("STOP"):
        st.session_state.tracking = False

# GPS
location = streamlit_geolocation()

# Tracking
if st.session_state.tracking:

    if location and location["latitude"] is not None:

        row = {
            "timestamp": datetime.now().isoformat(),
            "latitude": location["latitude"],
            "longitude": location["longitude"],
            "accuracy": location.get("accuracy")
        }

        # Evita duplicati consecutivi
        if (
            len(st.session_state.data) == 0
            or st.session_state.data[-1] != row
        ):
            st.session_state.data.append(row)

        st.success(f"Posizione registrata: {row}")

    time.sleep(interval)
    st.rerun()

# Tabella
df = pd.DataFrame(st.session_state.data)

st.dataframe(df)

# Download CSV
if not df.empty:
    csv = df.to_csv(index=False).encode("utf-8")

    st.download_button(
        "Scarica CSV",
        csv,
        file_name="gps_log.csv",
        mime="text/csv"
    )
