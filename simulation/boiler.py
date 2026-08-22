import random
import math


class BoilerSimulator:
    """
    Simulates a simplified industrial steam boiler/process.

    The model produces realistic-looking process variables and
    supports controlled fault injection for safety-system testing.
    """

    def __init__(self):
        # Process variables
        self.temperature = 150.0       # °C
        self.pressure = 5.0            # bar
        self.level = 70.0              # %
        self.flow = 35.0               # L/min

        # Actuator states
        self.heater_on = True
        self.pump_on = True
        self.valve_position = 50.0      # %

        # Simulation time
        self.time = 0

    def update(self, dt=1.0):
        """
        Advance the process simulation by dt seconds.
        """

        self.time += dt

        # -------------------------------------------------
        # HEATER EFFECT
        # -------------------------------------------------

        if self.heater_on:
            heating = 0.8
        else:
            heating = -0.35

        # -------------------------------------------------
        # COOLING EFFECT
        # -------------------------------------------------

        ambient_cooling = 0.015 * (self.temperature - 25)

        # Small process disturbance/noise
        temperature_noise = random.uniform(-0.15, 0.15)

        # Temperature dynamics
        self.temperature += (
            heating
            - ambient_cooling
            + temperature_noise
        ) * dt

        # -------------------------------------------------
        # PRESSURE DYNAMICS
        # -------------------------------------------------

        # Pressure approximately follows temperature
        target_pressure = 1.0 + (
            (self.temperature - 100.0) / 20.0
        )

        pressure_change = (
            target_pressure - self.pressure
        ) * 0.08

        # Valve reduces pressure
        valve_effect = (
            (self.valve_position - 50.0) / 100.0
        ) * 0.05

        pressure_noise = random.uniform(-0.03, 0.03)

        self.pressure += (
            pressure_change
            - valve_effect
            + pressure_noise
        ) * dt

        # -------------------------------------------------
        # WATER LEVEL
        # -------------------------------------------------

        if self.pump_on:
            level_increase = 0.25
        else:
            level_increase = -0.10

        # Steam generation consumes water
        steam_consumption = max(
            0.0,
            (self.temperature - 120.0) * 0.002
        )

        level_noise = random.uniform(-0.05, 0.05)

        self.level += (
            level_increase
            - steam_consumption
            + level_noise
        ) * dt

        # -------------------------------------------------
        # FLOW
        # -------------------------------------------------

        target_flow = (
            20.0
            + (self.valve_position * 0.6)
        )

        if not self.pump_on:
            target_flow *= 0.1

        flow_change = (
            target_flow - self.flow
        ) * 0.08

        flow_noise = random.uniform(-0.3, 0.3)

        self.flow += (
            flow_change + flow_noise
        ) * dt

        # -------------------------------------------------
        # LIMIT VALUES
        # -------------------------------------------------

        self.temperature = max(
            20.0,
            min(self.temperature, 300.0)
        )

        self.pressure = max(
            0.0,
            min(self.pressure, 20.0)
        )

        self.level = max(
            0.0,
            min(self.level, 100.0)
        )

        self.flow = max(
            0.0,
            min(self.flow, 100.0)
        )

        return self.get_sensor_data()

    def get_sensor_data(self):
        """
        Return simulated sensor measurements.
        """

        return {
            "temperature": round(self.temperature, 2),
            "pressure": round(self.pressure, 2),
            "level": round(self.level, 2),
            "flow": round(self.flow, 2),
            "heater_on": self.heater_on,
            "pump_on": self.pump_on,
            "valve_position": round(
                self.valve_position, 2
            ),
            "timestamp": self.time,
        }

    def inject_fault(self, fault_type):
        """
        Inject a controlled process fault for testing and demonstration.
        """

        if fault_type == "high_pressure":
            self.pressure = 11.0

        elif fault_type == "high_temperature":
            self.temperature = 220.0

        elif fault_type == "low_level":
            self.level = 15.0

        elif fault_type == "low_flow":
            self.flow = 5.0

        else:
            raise ValueError(
                f"Unknown fault type: {fault_type}"
            )


if __name__ == "__main__":
    boiler = BoilerSimulator()

    print("Industrial Boiler Simulator")
    print("----------------------------")

    for _ in range(20):
        data = boiler.update()

        print(
            f"TEMP: {data['temperature']:6.2f} °C | "
            f"PRESSURE: {data['pressure']:5.2f} bar | "
            f"LEVEL: {data['level']:5.2f} % | "
            f"FLOW: {data['flow']:5.2f} L/min"
        )
