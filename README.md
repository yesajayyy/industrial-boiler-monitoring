# Industrial Boiler Monitoring, Control and Safety System

An industrial boiler monitoring, control and safety system designed to continuously monitor temperature, pressure, water level, and flow; process instrumentation signals; automatically control boiler actuators; detect abnormal operating conditions; initiate emergency shutdown; log process data; and provide a real-time monitoring dashboard.

The project combines process simulation, industrial-style instrumentation, automatic control, safety interlocks, fault detection, data logging, an ATmega328P embedded implementation, Wokwi simulation, automated testing, and a Streamlit-based monitoring dashboard.

---

## Project Overview

Industrial boilers operate under continuously changing temperature, pressure, water-level, and flow conditions. Failure to detect abnormal conditions can result in equipment damage or unsafe operation.

This project demonstrates a complete monitoring and control architecture in which process variables are measured, converted into instrumentation signals, processed into engineering values, evaluated by the safety system, and used by the controller to operate actuators.

The system also provides a monitoring dashboard for observing the simulated boiler process in real time.

---

## Main Features

- Real-time temperature monitoring
- Pressure monitoring
- Water-level monitoring
- Flow monitoring
- 4–20 mA instrumentation simulation
- Signal processing and engineering-unit conversion
- Automatic heater control
- Automatic feed-pump control
- Control-valve operation
- Safety interlocks
- High-pressure emergency shutdown
- Low-level emergency protection
- Safety-trip latching
- Fault injection and recovery
- Sensor fault detection
- Anomaly detection
- Process-data logging
- Alarm logging
- Real-time Streamlit dashboard
- ATmega328P embedded implementation
- Wokwi hardware simulation
- Automated software testing

---

## System Architecture

```text
                    INDUSTRIAL BOILER SYSTEM
                              |
                              v
                    +-------------------+
                    | Boiler Simulation |
                    +-------------------+
                              |
                              v
                    +-------------------+
                    | Process Sensors   |
                    | T / P / Level / F |
                    +-------------------+
                              |
                              v
                    +-------------------+
                    | 4–20 mA           |
                    | Instrumentation   |
                    +-------------------+
                              |
                              v
                    +-------------------+
                    | Signal Processing |
                    +-------------------+
                              |
                              v
                    +-------------------+
                    | Safety System     |
                    | Interlocks        |
                    +-------------------+
                              |
                     +--------+--------+
                     |                 |
                     v                 v
              +------------+    +-------------+
              | Controller |    | Fault       |
              |            |    | Detection   |
              +------------+    +-------------+
                     |
                     v
              +-------------+
              | Actuators   |
              | Heater      |
              | Pump        |
              | Valve       |
              +-------------+
                     |
                     v
              +-------------+
              | Data Logger |
              +-------------+
                     |
                     v
              +-------------+
              | Dashboard   |
              | Streamlit   |
              +-------------+


Process Variables
The system monitors four primary process variables.
Variable	Unit	Purpose
Temperature	°C	Monitors boiler thermal condition
Pressure	bar	Detects pressure buildup and unsafe conditions
Water Level	%	Maintains safe boiler water level
Flow	L/min	Monitors process/feed flow
Instrumentation
The project includes an industrial-style instrumentation layer.
The simulated sensor values are converted into transmitter signals using a 4–20 mA representation.

Process Variable
       |
       v
Sensor Measurement
       |
       v
4–20 mA Transmitter
       |
       v
Signal Processing
       |
       v
Engineering Units

This provides a simplified representation of how industrial process instrumentation interfaces with control systems.

Automatic Control
The boiler controller automatically determines actuator operation based on the measured process conditions and safety state.
Controlled Actuators
* Heater
* Feed pump
* Control valve
Example control flow:

Process Measurements
        |
        v
Controller
        |
        +------> Heater
        |
        +------> Feed Pump
        |
        +------> Control Valve

The controller operates normally only when the safety system permits operation.

Safety System
Safety is given priority over normal process control.
The safety system continuously evaluates process conditions and can override normal controller operation.
Safety Functions
* High-pressure detection
* Low-level detection
* Emergency shutdown
* Safety-trip latching
* Alarm generation
* Recovery/reset handling
Example:

Normal Operation
       |
       v
Abnormal Condition
       |
       v
Safety Evaluation
       |
       v
Emergency Trip
       |
       +----> Heater OFF
       |
       +----> Safety State = EMERGENCY
       |
       +----> Alarm
       |
       v
Safety Trip Latched
       |
       v
Manual/Controlled Reset
       |
       v
Normal Operation


Fault Detection
The project includes fault injection and abnormal-condition detection.
Examples include:
* High-pressure fault
* Low-water-level condition
* Sensor-related abnormal conditions
* Safety-trip conditions
The system records abnormal conditions and prevents unsafe actuator operation when required.

Data Logging
Process data is continuously recorded during simulation.
The project uses CSV-based logging for process and alarm information.
Process Data

data/process_data.csv

Alarm Data

logs/alarms.csv

Logged information includes process measurements, actuator states, safety state, timestamps, and alarm information.
Generated runtime data is excluded from version control where appropriate.

Real-Time Monitoring Dashboard
The project includes a Streamlit dashboard located at:

app/dashboard.py

The dashboard displays:
* Temperature
* Pressure
* Water level
* Flow
* Heater status
* Feed-pump status
* Control-valve position
* Safety status
* Safety alarms
* Simulation cycle
* Real-time process trends
* Data logging information
The dashboard uses the same boiler simulation, controller, and safety-system modules as the software test environment.

Dashboard Architecture

BoilerSimulator
       |
       v
SafetySystem
       |
       v
BoilerController
       |
       +----------------+
       |                |
       v                v
Process State       Actuator State
       |                |
       +-------+--------+
               |
               v
          Data Logging
               |
               v
        Streamlit Dashboard


Embedded Implementation
The project also includes an ATmega328P-based embedded implementation.
Main embedded files:

sketch.ino
diagram.json

The embedded implementation represents the transition from software process simulation toward a microcontroller-based industrial monitoring and safety system.
The design can be extended to physical sensors, signal-conditioning circuits, relays, actuators, displays, and alarms.

Wokwi Simulation
The ATmega328P implementation can be simulated using Wokwi.
The simulation demonstrates the embedded control concept without requiring physical hardware.
The project includes:

sketch.ino
diagram.json

These files define the embedded program and simulated hardware configuration.

Software Structure

industrial-boiler-monitoring/
|
├── app/
│   └── dashboard.py
|
├── control/
│   ├── __init__.py
│   └── controller.py
|
├── data/
│   ├── boiler_training_dataset.csv
│   ├── generate_dataset.py
│   └── process_data.csv
|
├── fault_detection/
│   ├── __init__.py
│   └── anomaly_detector.py
|
├── instrumentation/
│   ├── __init__.py
│   ├── sensors.py
│   └── signal_processing.py
|
├── logs/
│   ├── boiler_data.csv
│   └── data_logger.py
|
├── models/
│   └── boiler_anomaly_model.pkl
|
├── safety/
│   ├── __init__.py
│   └── safety_system.py
|
├── simulation/
│   ├── __init__.py
│   └── boiler.py
|
├── tests/
│   ├── __init__.py
│   ├── test_end_to_end.py
│   ├── test_integration.py
│   └── test_system.py
|
├── diagram.json
├── requirements.txt
├── README.md
└── sketch.ino


Technologies Used
Hardware / Embedded
* ATmega328P
* Simulated process sensors
* Wokwi simulation
Programming
* Python
* C/C++ for embedded implementation
Python Libraries
* Pandas
* Streamlit
* Plotly
* Scikit-learn
* Joblib
* Pytest
Development Tools
* Git
* GitHub
* Wokwi
* Virtual Environment

Testing
The project includes automated unit, integration, and end-to-end tests.
Tests cover:
* Boiler simulation
* Sensor behavior
* Instrumentation
* Signal processing
* Controller behavior
* Safety system
* Emergency trip
* Safety-trip latching
* Fault handling
* End-to-end operation
The current test suite passes successfully.

10 passed

Example command:

pytest -q

Expected result:

.......... [100%]
10 passed


End-to-End Control Sequence
The complete control sequence is:

Boiler Process
      |
      v
Sensor Measurement
      |
      v
Instrumentation
      |
      v
Signal Processing
      |
      v
Safety Evaluation
      |
      +------> Emergency?
      |            |
      |            +---- YES ----> Safety Trip
      |            |
      |            +---- NO
      |
      v
Automatic Controller
      |
      v
Actuators
      |
      v
Boiler Process
      |
      v
Data Logger
      |
      v
Monitoring Dashboard


Emergency Shutdown Sequence
Under a critical abnormal condition:

Abnormal Process Condition
          |
          v
Safety Limit Exceeded
          |
          v
Emergency Status
          |
          v
Safety Trip
          |
          +----> Heater OFF
          |
          +----> Actuators placed in safe state
          |
          +----> Alarm Generated
          |
          v
Safety Trip Latched

The system prevents normal control logic from overriding the emergency safety state.

Running the Project
1. Clone the repository

git clone https://github.com/yesajayyy/industrial-boiler-monitoring.git
cd industrial-boiler-monitoring

2. Create a virtual environment

python3 -m venv venv

3. Activate the environment
macOS/Linux:

source venv/bin/activate

4. Install dependencies

pip install -r requirements.txt

5. Run the automated tests

pytest -q

6. Run the monitoring dashboard

streamlit run app/dashboard.py

The Streamlit application will display the real-time simulated boiler monitoring interface.

Project Validation
The project has been validated through:
* Automated software tests
* End-to-end control testing
* Safety-trip testing
* Fault-injection testing
* ATmega328P simulation
* Wokwi embedded simulation
* Real-time dashboard execution
* Process-data logging
Current automated test result:

10 passed


Engineering Concepts Demonstrated
This project demonstrates practical concepts from Electronics and Instrumentation Engineering and embedded systems, including:
* Process instrumentation
* Industrial sensors
* 4–20 mA transmitters
* Signal conditioning
* Engineering-unit conversion
* Process monitoring
* Automatic control
* Safety interlocks
* Emergency shutdown systems
* Fault detection
* Embedded systems
* Microcontroller programming
* Data acquisition
* Data logging
* Industrial process visualization
* Software testing

Future Hardware Implementation
The simulation can be extended into a physical prototype using:
* ATmega328P development board
* Temperature sensor
* Pressure sensor/transmitter
* Water-level sensor
* Flow sensor
* 4–20 mA receiver circuits
* ADC signal conditioning
* Relay or MOSFET actuator drivers
* Heater/load representation
* Pump
* Solenoid/control valve
* LCD display
* Buzzer
* Emergency-stop circuit
For an actual industrial installation, appropriate certified safety hardware, isolation, protection circuits, and engineering validation would be required.

Project Status

Core Simulation              COMPLETE
Instrumentation              COMPLETE
Signal Processing            COMPLETE
Automatic Control            COMPLETE
Safety System                COMPLETE
Fault Detection              COMPLETE
Data Logging                 COMPLETE
ATmega328P Implementation    COMPLETE
Wokwi Simulation             COMPLETE
Streamlit Dashboard          COMPLETE
Automated Testing            COMPLETE
GitHub Integration           COMPLETE
Documentation                IN PROGRESS


Author
Guguloth Ajay
B.Tech — Electronics and Instrumentation Engineering National Institute of Technology Nagaland
