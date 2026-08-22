class SignalProcessor:
    """
    Industrial signal-processing layer.

    Converts 4-20 mA transmitter signals into engineering
    values used by the control and safety systems.
    """

    def __init__(self):
        self.transmitter_ranges = {
            "temperature": {
                "min": 0.0,
                "max": 300.0,
                "unit": "°C",
            },
            "pressure": {
                "min": 0.0,
                "max": 16.0,
                "unit": "bar",
            },
            "level": {
                "min": 0.0,
                "max": 100.0,
                "unit": "%",
            },
            "flow": {
                "min": 0.0,
                "max": 100.0,
                "unit": "L/min",
            },
        }

    def current_to_value(
        self,
        current_mA,
        minimum,
        maximum,
    ):
        """
        Convert a 4-20 mA signal into an engineering value.
        """

        current_mA = float(current_mA)

        if current_mA < 3.8:
            raise ValueError(
                "Transmitter signal too low."
            )

        if current_mA > 20.5:
            raise ValueError(
                "Transmitter signal too high."
            )

        current_mA = max(
            4.0,
            min(current_mA, 20.0),
        )

        percentage = (
            (current_mA - 4.0) / 16.0
        )

        value = (
            minimum
            + percentage
            * (maximum - minimum)
        )

        return round(value, 3)

    def process(self, transmitter_data):
        """
        Process all transmitter signals.

        Expected input:

        temperature_mA
        pressure_mA
        level_mA
        flow_mA
        """

        temperature = self.current_to_value(
            transmitter_data["temperature_mA"],
            self.transmitter_ranges[
                "temperature"
            ]["min"],
            self.transmitter_ranges[
                "temperature"
            ]["max"],
        )

        pressure = self.current_to_value(
            transmitter_data["pressure_mA"],
            self.transmitter_ranges[
                "pressure"
            ]["min"],
            self.transmitter_ranges[
                "pressure"
            ]["max"],
        )

        level = self.current_to_value(
            transmitter_data["level_mA"],
            self.transmitter_ranges[
                "level"
            ]["min"],
            self.transmitter_ranges[
                "level"
            ]["max"],
        )

        flow = self.current_to_value(
            transmitter_data["flow_mA"],
            self.transmitter_ranges[
                "flow"
            ]["min"],
            self.transmitter_ranges[
                "flow"
            ]["max"],
        )

        return {
            "temperature": temperature,
            "pressure": pressure,
            "level": level,
            "flow": flow,
        }


if __name__ == "__main__":
    from instrumentation.sensors import (
        BoilerInstrumentation,
    )

    instrumentation = BoilerInstrumentation()
    processor = SignalProcessor()

    process_data = {
        "temperature": 165.0,
        "pressure": 6.0,
        "level": 65.0,
        "flow": 38.0,
    }

    transmitter_data = instrumentation.read(
        process_data
    )

    processed_data = processor.process(
        transmitter_data
    )

    print("INDUSTRIAL SIGNAL PROCESSING TEST")
    print("=" * 60)

    print("TRANSMITTER SIGNALS")
    print(
        f"Temperature: "
        f"{transmitter_data['temperature_mA']} mA"
    )
    print(
        f"Pressure: "
        f"{transmitter_data['pressure_mA']} mA"
    )
    print(
        f"Level: "
        f"{transmitter_data['level_mA']} mA"
    )
    print(
        f"Flow: "
        f"{transmitter_data['flow_mA']} mA"
    )

    print()
    print("PROCESSED ENGINEERING VALUES")
    print(
        f"Temperature: "
        f"{processed_data['temperature']} °C"
    )
    print(
        f"Pressure: "
        f"{processed_data['pressure']} bar"
    )
    print(
        f"Level: "
        f"{processed_data['level']} %"
    )
    print(
        f"Flow: "
        f"{processed_data['flow']} L/min"
    )
