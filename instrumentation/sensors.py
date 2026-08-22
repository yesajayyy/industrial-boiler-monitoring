import random


class Transmitter:
    """
    Generic industrial 4-20 mA transmitter.

    Converts an engineering value into a transmitter current
    and converts the current back into an engineering value.
    """

    def __init__(
        self,
        tag,
        unit,
        minimum,
        maximum,
        noise=0.0,
        calibration_offset=0.0,
    ):
        self.tag = tag
        self.unit = unit
        self.minimum = float(minimum)
        self.maximum = float(maximum)
        self.noise = float(noise)
        self.calibration_offset = float(
            calibration_offset
        )

    def clamp(self, value):
        return max(
            self.minimum,
            min(value, self.maximum),
        )

    def engineering_to_current(self, value):
        """
        Convert engineering value to 4-20 mA.
        """

        value = self.clamp(value)

        percentage = (
            (value - self.minimum)
            / (self.maximum - self.minimum)
        )

        current = 4.0 + (
            percentage * 16.0
        )

        if self.noise > 0:
            current += random.uniform(
                -self.noise,
                self.noise,
            )

        return round(
            max(4.0, min(current, 20.0)),
            4,
        )

    def current_to_engineering(self, current):
        """
        Convert 4-20 mA back into engineering units.
        """

        current = max(
            4.0,
            min(float(current), 20.0),
        )

        percentage = (
            (current - 4.0) / 16.0
        )

        value = (
            self.minimum
            + percentage
            * (self.maximum - self.minimum)
        )

        value += self.calibration_offset

        return round(
            self.clamp(value),
            3,
        )

    def measure(self, process_value):
        """
        Simulate a complete transmitter measurement.
        """

        current = self.engineering_to_current(
            process_value
        )

        measured_value = (
            self.current_to_engineering(
                current
            )
        )

        return {
            "tag": self.tag,
            "value": measured_value,
            "unit": self.unit,
            "current_mA": current,
        }


class TemperatureTransmitter(Transmitter):
    """
    TT-101
    Temperature transmitter.

    Range: 0-300 °C
    Output: 4-20 mA
    """

    def __init__(self):
        super().__init__(
            tag="TT-101",
            unit="°C",
            minimum=0.0,
            maximum=300.0,
            noise=0.03,
        )


class PressureTransmitter(Transmitter):
    """
    PT-101
    Pressure transmitter.

    Range: 0-16 bar
    Output: 4-20 mA
    """

    def __init__(self):
        super().__init__(
            tag="PT-101",
            unit="bar",
            minimum=0.0,
            maximum=16.0,
            noise=0.02,
        )


class LevelTransmitter(Transmitter):
    """
    LT-101
    Water level transmitter.

    Range: 0-100 %
    Output: 4-20 mA
    """

    def __init__(self):
        super().__init__(
            tag="LT-101",
            unit="%",
            minimum=0.0,
            maximum=100.0,
            noise=0.03,
        )


class FlowTransmitter(Transmitter):
    """
    FT-101
    Flow transmitter.

    Range: 0-100 L/min
    Output: 4-20 mA
    """

    def __init__(self):
        super().__init__(
            tag="FT-101",
            unit="L/min",
            minimum=0.0,
            maximum=100.0,
            noise=0.04,
        )


class BoilerInstrumentation:
    """
    Complete instrumentation package for the boiler.

    Represents the four primary process transmitters:

    TT-101 -> Temperature
    PT-101 -> Pressure
    LT-101 -> Level
    FT-101 -> Flow
    """

    def __init__(self):
        self.temperature = TemperatureTransmitter()
        self.pressure = PressureTransmitter()
        self.level = LevelTransmitter()
        self.flow = FlowTransmitter()

    def read(self, process_data):
        """
        Read all boiler process variables through their
        respective industrial transmitters.
        """

        temperature = self.temperature.measure(
            process_data["temperature"]
        )

        pressure = self.pressure.measure(
            process_data["pressure"]
        )

        level = self.level.measure(
            process_data["level"]
        )

        flow = self.flow.measure(
            process_data["flow"]
        )

        return {
            "temperature": temperature["value"],
            "pressure": pressure["value"],
            "level": level["value"],
            "flow": flow["value"],
            "temperature_mA": temperature[
                "current_mA"
            ],
            "pressure_mA": pressure[
                "current_mA"
            ],
            "level_mA": level[
                "current_mA"
            ],
            "flow_mA": flow[
                "current_mA"
            ],
        }


if __name__ == "__main__":
    instrumentation = BoilerInstrumentation()

    process_data = {
        "temperature": 165.0,
        "pressure": 6.0,
        "level": 65.0,
        "flow": 38.0,
    }

    measurements = instrumentation.read(
        process_data
    )

    print("BOILER INSTRUMENTATION TEST")
    print("=" * 60)

    print(
        f"TT-101 | "
        f"{measurements['temperature']} °C | "
        f"{measurements['temperature_mA']} mA"
    )

    print(
        f"PT-101 | "
        f"{measurements['pressure']} bar | "
        f"{measurements['pressure_mA']} mA"
    )

    print(
        f"LT-101 | "
        f"{measurements['level']} % | "
        f"{measurements['level_mA']} mA"
    )

    print(
        f"FT-101 | "
        f"{measurements['flow']} L/min | "
        f"{measurements['flow_mA']} mA"
    )

