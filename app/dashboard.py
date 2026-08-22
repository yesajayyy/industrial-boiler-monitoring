import sys
import os

PROJECT_ROOT = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import time
from datetime import datetime

import pandas as pd
import streamlit as st
import plotly.graph_objects as go

from simulation.boiler import BoilerSimulator
from control.controller import BoilerController
from safety.safety_system import SafetySystem


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Industrial Boiler Monitoring System",
    layout="wide"
)


# ============================================================
# CONSTANTS
# ============================================================

DATA_DIR = os.path.join(PROJECT_ROOT, "data")
LOG_DIR = os.path.join(PROJECT_ROOT, "logs")

DATA_FILE = os.path.join(DATA_DIR, "process_data.csv")
ALARM_FILE = os.path.join(LOG_DIR, "alarms.csv")

os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(LOG_DIR, exist_ok=True)


# ============================================================
# SESSION STATE INITIALIZATION
# ============================================================

if "boiler" not in st.session_state:
    st.session_state.boiler = BoilerSimulator()

if "controller" not in st.session_state:
    st.session_state.controller = BoilerController()

if "safety" not in st.session_state:
    st.session_state.safety = SafetySystem()

if "running" not in st.session_state:
    st.session_state.running = True

if "history" not in st.session_state:
    st.session_state.history = []

if "cycle" not in st.session_state:
    st.session_state.cycle = 0


boiler = st.session_state.boiler
controller = st.session_state.controller
safety = st.session_state.safety


# ============================================================
# DATA LOGGING
# ============================================================

def save_process_data(sensor_data, safety_result, outputs):

    row = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "cycle": st.session_state.cycle,
        "temperature": sensor_data["temperature"],
        "pressure": sensor_data["pressure"],
        "level": sensor_data["level"],
        "flow": sensor_data["flow"],
        "heater_on": outputs["heater_on"],
        "pump_on": outputs["pump_on"],
        "valve_position": outputs["valve_position"],
        "safety_status": safety_result["status"],
    }

    df = pd.DataFrame([row])

    if os.path.exists(DATA_FILE):
        df.to_csv(
            DATA_FILE,
            mode="a",
            header=False,
            index=False
        )
    else:
        df.to_csv(
            DATA_FILE,
            index=False
        )


def save_alarm(alarm):

    row = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "cycle": st.session_state.cycle,
        "alarm": alarm,
    }

    df = pd.DataFrame([row])

    if os.path.exists(ALARM_FILE):
        df.to_csv(
            ALARM_FILE,
            mode="a",
            header=False,
            index=False
        )
    else:
        df.to_csv(
            ALARM_FILE,
            index=False
        )


# ============================================================
# CHART CREATION
# ============================================================

def create_chart(history, column, title, y_title):

    if not history:
        return

    df = pd.DataFrame(history)

    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=df["cycle"],
            y=df[column],
            mode="lines+markers",
            name=column.capitalize()
        )
    )

    fig.update_layout(
        title=title,
        xaxis_title="Simulation Cycle",
        yaxis_title=y_title,
        height=300,
        margin=dict(
            l=20,
            r=20,
            t=50,
            b=20
        )
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )


# ============================================================
# PROCESS UPDATE
# ============================================================

sensor_data = boiler.get_sensor_data()

safety_result = safety.evaluate(sensor_data)

outputs = controller.control(
    sensor_data,
    safety_result["status"]
)


# ============================================================
# APPLY CONTROLLER OUTPUTS
# ============================================================

boiler.heater_on = outputs["heater_on"]
boiler.pump_on = outputs["pump_on"]
boiler.valve_position = outputs["valve_position"]


# ============================================================
# UPDATE SIMULATION
# ============================================================

if st.session_state.running:

    st.session_state.cycle += 1

    history_row = {
        "cycle": st.session_state.cycle,
        "temperature": sensor_data["temperature"],
        "pressure": sensor_data["pressure"],
        "level": sensor_data["level"],
        "flow": sensor_data["flow"],
    }

    st.session_state.history.append(history_row)

    if len(st.session_state.history) > 60:
        st.session_state.history.pop(0)

    save_process_data(
        sensor_data,
        safety_result,
        outputs
    )

    for alarm in safety_result["alarms"]:
        save_alarm(alarm)

    boiler.update()


# ============================================================
# HEADER
# ============================================================

st.title("Industrial Boiler Monitoring System")

st.caption(
    "Real-Time Process Simulation | PLC-Style Control | "
    "Safety Interlocks | Data Logging"
)


# ============================================================
# CONTROL BUTTONS
# ============================================================

col1, col2, col3 = st.columns(3)

with col1:

    if st.button(
        "Start System",
        use_container_width=True
    ):
        st.session_state.running = True
        st.rerun()


with col2:

    if st.button(
        "Stop System",
        use_container_width=True
    ):
        st.session_state.running = False
        st.rerun()


with col3:

    if st.button(
        "Reset System",
        use_container_width=True
    ):

        st.session_state.boiler = BoilerSimulator()
        st.session_state.controller = BoilerController()
        st.session_state.safety = SafetySystem()

        st.session_state.history = []
        st.session_state.cycle = 0
        st.session_state.running = True

        st.rerun()


# ============================================================
# SAFETY STATUS
# ============================================================

st.subheader("Safety Status")

if safety_result["status"] == "NORMAL":

    st.success(
        "SAFETY STATUS: NORMAL"
    )

else:

    st.error(
        "SAFETY STATUS: EMERGENCY"
    )


# ============================================================
# PROCESS MEASUREMENTS
# ============================================================

st.subheader("Process Measurements")

c1, c2, c3, c4 = st.columns(4)

with c1:

    st.metric(
        "Temperature",
        f"{sensor_data['temperature']:.2f} °C"
    )

with c2:

    st.metric(
        "Pressure",
        f"{sensor_data['pressure']:.2f} bar"
    )

with c3:

    st.metric(
        "Water Level",
        f"{sensor_data['level']:.2f} %"
    )

with c4:

    st.metric(
        "Flow",
        f"{sensor_data['flow']:.2f} L/min"
    )


# ============================================================
# ACTUATOR STATUS
# ============================================================

st.subheader("Actuator Status")

a1, a2, a3 = st.columns(3)

with a1:

    st.metric(
        "Heater",
        "ON" if outputs["heater_on"] else "OFF"
    )

with a2:

    st.metric(
        "Feed Pump",
        "ON" if outputs["pump_on"] else "OFF"
    )

with a3:

    st.metric(
        "Control Valve",
        f"{outputs['valve_position']:.1f} %"
    )


# ============================================================
# REAL-TIME PROCESS TRENDS
# ============================================================

st.subheader("Real-Time Process Trends")

chart1, chart2 = st.columns(2)

with chart1:

    create_chart(
        st.session_state.history,
        "temperature",
        "Temperature Trend",
        "Temperature (°C)"
    )

with chart2:

    create_chart(
        st.session_state.history,
        "pressure",
        "Pressure Trend",
        "Pressure (bar)"
    )


chart3, chart4 = st.columns(2)

with chart3:

    create_chart(
        st.session_state.history,
        "level",
        "Water Level Trend",
        "Level (%)"
    )

with chart4:

    create_chart(
        st.session_state.history,
        "flow",
        "Flow Trend",
        "Flow (L/min)"
    )


# ============================================================
# SAFETY ALARMS
# ============================================================

st.subheader("Safety Alarms")

if safety_result["alarms"]:

    for alarm in safety_result["alarms"]:

        st.error(
            f"ALARM: {alarm}"
        )

else:

    st.info(
        "No active alarms."
    )


# ============================================================
# SYSTEM INFORMATION
# ============================================================

st.subheader("System Information")

i1, i2, i3 = st.columns(3)

with i1:

    st.metric(
        "Simulation Cycle",
        st.session_state.cycle
    )

with i2:

    st.metric(
        "System State",
        "RUNNING"
        if st.session_state.running
        else "STOPPED"
    )

with i3:

    st.metric(
        "Safety State",
        safety_result["status"]
    )


# ============================================================
# DATA LOGGING
# ============================================================

st.subheader("Data Logging")

st.write(
    f"Process data: `{DATA_FILE}`"
)

st.write(
    f"Alarm log: `{ALARM_FILE}`"
)


# ============================================================
# AUTOMATIC REFRESH
# ============================================================

if st.session_state.running:

    time.sleep(1)

    st.rerun()
