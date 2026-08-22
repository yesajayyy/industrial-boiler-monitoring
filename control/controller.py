class BoilerController:
    """
    PLC-style automatic controller for the boiler.
    """

    def __init__(self):
        self.heater_on = True
        self.pump_on = True
        self.valve_position = 50.0

    def control(self, sensor_data, safety_status="NORMAL"):

        temperature = sensor_data["temperature"]
        pressure = sensor_data["pressure"]
        level = sensor_data["level"]
        flow = sensor_data["flow"]

        # ---------------------------------------------
        # EMERGENCY CONDITION
        # ---------------------------------------------

        if safety_status == "EMERGENCY":

            self.heater_on = False
            self.pump_on = False
            self.valve_position = 100.0

            return self.get_outputs()

        # ---------------------------------------------
        # TEMPERATURE CONTROL
        # ---------------------------------------------

        if temperature >= 190:
            self.heater_on = False

        elif temperature <= 170:
            self.heater_on = True

        # ---------------------------------------------
        # PRESSURE CONTROL
        # ---------------------------------------------

        if pressure >= 8:
            self.valve_position = min(
                100.0,
                self.valve_position + 10
            )

        elif pressure <= 6:
            self.valve_position = max(
                20.0,
                self.valve_position - 5
            )

        # ---------------------------------------------
        # LEVEL CONTROL
        # ---------------------------------------------

        if level < 35:
            self.pump_on = True

        elif level > 85:
            self.pump_on = False

        # ---------------------------------------------
        # LOW FLOW PROTECTION
        # ---------------------------------------------

        if flow < 15:
            self.pump_on = True

        return self.get_outputs()

    def get_outputs(self):

        return {
            "heater_on": self.heater_on,
            "pump_on": self.pump_on,
            "valve_position": self.valve_position,
        }
