class SafetySystem:
    """
    Industrial-style safety and interlock system.

    Critical safety trips are latched until a manual reset
    is performed. This prevents automatic restart after a
    dangerous condition temporarily disappears.
    """

    # Safety limits
    MAX_TEMPERATURE = 210.0
    MAX_PRESSURE = 10.0
    MIN_LEVEL = 20.0
    MIN_FLOW = 10.0

    def __init__(self):
        self.status = "NORMAL"
        self.alarms = []
        self.trip_latched = False

    def evaluate(self, sensor_data):
        """
        Evaluate process conditions and generate safety actions.
        """

        temperature = sensor_data["temperature"]
        pressure = sensor_data["pressure"]
        level = sensor_data["level"]
        flow = sensor_data["flow"]

        current_alarms = []

        # ---------------------------------------------
        # HIGH TEMPERATURE
        # ---------------------------------------------

        if temperature >= self.MAX_TEMPERATURE:
            current_alarms.append(
                "CRITICAL: HIGH TEMPERATURE"
            )

        # ---------------------------------------------
        # HIGH PRESSURE
        # ---------------------------------------------

        if pressure >= self.MAX_PRESSURE:
            current_alarms.append(
                "CRITICAL: HIGH PRESSURE"
            )

        # ---------------------------------------------
        # LOW LEVEL
        # ---------------------------------------------

        if level <= self.MIN_LEVEL:
            current_alarms.append(
                "CRITICAL: LOW WATER LEVEL"
            )

        # ---------------------------------------------
        # LOW FLOW
        # ---------------------------------------------

        if flow <= self.MIN_FLOW:
            current_alarms.append(
                "CRITICAL: LOW FLOW"
            )

        # ---------------------------------------------
        # LATCH SAFETY TRIP
        # ---------------------------------------------

        if current_alarms:
            self.trip_latched = True

        # ---------------------------------------------
        # STATUS
        # ---------------------------------------------

        if self.trip_latched:
            self.status = "EMERGENCY"

            if current_alarms:
                self.alarms = current_alarms
            else:
                self.alarms = [
                    "SAFETY TRIP LATCHED"
                ]

        else:
            self.status = "NORMAL"
            self.alarms = []

        # ---------------------------------------------
        # ACTUATOR COMMANDS
        # ---------------------------------------------

        if self.status == "NORMAL":

            actuators = {
                "heater": "ON",
                "pump": "ON",
                "valve": "OPERATING",
                "buzzer": "OFF"
            }

        else:

            actuators = {
                "heater": "OFF",
                "pump": "OFF",
                "valve": "OPEN",
                "buzzer": "ON"
            }

        return {
            "status": self.status,
            "alarms": self.alarms,
            "actuators": actuators,
            "trip_latched": self.trip_latched
        }

    def reset(self, sensor_data):
        """
        Manually reset the safety system.

        Reset is allowed only when all process conditions
        are back inside safe operating limits.
        """

        temperature = sensor_data["temperature"]
        pressure = sensor_data["pressure"]
        level = sensor_data["level"]
        flow = sensor_data["flow"]

        safe_to_reset = (
            temperature < self.MAX_TEMPERATURE
            and pressure < self.MAX_PRESSURE
            and level > self.MIN_LEVEL
            and flow > self.MIN_FLOW
        )

        if safe_to_reset:
            self.trip_latched = False
            self.status = "NORMAL"
            self.alarms = []

            return True

        return False
