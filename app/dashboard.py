import sys
import os

PROJECT_ROOT = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
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


st.set_page_config(
    page_title="Industrial Boiler Monitoring System",
    layout="wide"
)


DATA_DIR = "data"
LOG_DIR = "logs"

DATA_FILE = os.path.join(
    DATA_DIR,
    "process_data.csv"
)

ALARM_FILE = os.path.join(
    LOG_DIR,
    "alarms.csv"
)

os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(LOG_DIR, exist_ok=True)


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

if "last_safety_result" not in st.session_state:
    st.session_state.last_safety_result = {
        "status": "NORMAL",
        "alarms": [],
        "trip_latched": False
    }


boiler = st.session_state.boiler
controller = st.session_state.controller
safety = st.session_state.safety


def save_process_data(
    sensor_data,
    safety_result,
    outputs
):

    row = {
        "timestamp": datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        ),
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
        "timestamp": datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        ),
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


def create_chart(
    history,
    column,
    title,
    y_title
):

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


def inject_fault(fault_type):

    boiler.inject_fault(fault_type)

    st.session_state.running = True

    st.rerun()


def reset_safety_system():

    sensor_data = boiler.get_sensor_data()

    reset_success = safety.reset(
        sensor_data
    )

    if reset_success:

        boiler.heater_on = True
        boiler.pump_on = True
        boiler.valve_position = 50.0

        st.session_state.last_safety_result = {
            "status": "NORMAL",
            "alarms": [],
            "trip_latched": False
        }

        return True

    return False


# ============================================================
# PROCESS UPDATE
# ============================================================

if st.session_state.running:

    sensor_data = boiler.get_sensor_data()

    safety_result = safety.evaluate(
        sensor_data
    )

    outputs = controller.control(
        sensor_data,
        safety_result["status"]
    )

    boiler.heater_on = outputs["heater_on"]
    boiler.pump_on = outputs["pump_on"]
    boiler.valve_position = outputs["valve_position"]

    st.session_state.cycle += 1

    history_row = {
        "cycle": st.session_state.cycle,
        "temperature": sensor_data["temperature"],
        "pressure": sensor_data["pressure"],
        "level": sensor_data["level"],
        "flow": sensor_data["flow"],
    }

    st.session_state.history.append(
        history_row
    )

    if len(st.session_state.history) > 60:
        st.session_state.history.pop(0)

    save_process_data(
        sensor_data,
        safety_result,
        outputs
    )

    for alarm in safety_result["alarms"]:

        save_alarm(alarm)

    st.session_state.last_safety_result = (
        safety_result
    )

    boiler.update()


sensor_data = boiler.get_sensor_data()

safety_result = (
    st.session_state.last_safety_result
)

outputs = {
    "heater_on": boiler.heater_on,
    "pump_on": boiler.pump_on,
    "valve_position": boiler.valve_position
}


# ============================================================
# HEADER
# ============================================================

st.title(
    "Industrial Boiler Monitoring System"
)

st.caption(
    "Real-Time Process Simulation | "
    "Automatic Control | Safety Interlocks | "
    "Fault Detection | Data Logging"
)


# ============================================================
# SYSTEM CONTROLS
# ============================================================

st.subheader("System Controls")

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
        "Reset Safety System",
        use_container_width=True
    ):

        if reset_safety_system():

            st.success(
                "Safety system reset successfully."
            )

            st.rerun()

        else:

            st.error(
                "Reset rejected. "
                "Process conditions are not safe."
            )


# ============================================================
# FAULT INJECTION
# ============================================================

st.subheader("Fault Injection")

f1, f2, f3, f4 = st.columns(4)

with f1:

    if st.button(
        "Inject High Pressure",
        use_container_width=True
    ):

        inject_fault(
            "high_pressure"
        )


with f2:

    if st.button(
        "Inject High Temperature",
        use_container_width=True
    ):

        inject_fault(
            "high_temperature"
        )


with f3:

    if st.button(
        "Inject Low Water Level",
        use_container_width=True
    ):

        inject_fault(
            "low_level"
        )


with f4:

    if st.button(
        "Inject Low Flow",
        use_container_width=True
    ):

        inject_fault(
            "low_flow"
        )


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
        "ON"
        if outputs["heater_on"]
        else "OFF"
    )

with a2:

    st.metric(
        "Feed Pump",
        "ON"
        if outputs["pump_on"]
        else "OFF"
    )

with a3:

    st.metric(
        "Control Valve",
        f"{outputs['valve_position']:.1f} %"
    )


# ============================================================
# PROCESS TRENDS
# ============================================================

st.subheader(
    "Real-Time Process Trends"
)

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

        st.error(alarm)

else:

    st.info(
        "No active alarms."
    )


# ============================================================
# SYSTEM INFORMATION
# ============================================================

st.subheader(
    "System Information"
)

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
        safety.status
    )


# ============================================================
# DATA LOGGING
# ============================================================

st.subheader(
    "Data Logging"
)

st.write(
    f"Process data: `{DATA_FILE}`"
)

st.write(
    f"Alarm log: `{ALARM_FILE}`"
)


# ============================================================
# AUTO REFRESH
# ============================================================

if st.session_state.running:

    time.sleep(1)

    st.rerun()
