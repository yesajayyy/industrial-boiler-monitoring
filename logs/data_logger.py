import csv
import os
from datetime import datetime


class DataLogger:
    """
    Logs industrial boiler process data to a CSV file.
    """

    def __init__(self, filename="logs/boiler_data.csv"):
        self.filename = filename

        directory = os.path.dirname(self.filename)

        if directory:
            os.makedirs(directory, exist_ok=True)

        # Create CSV with headers if it doesn't exist
        if not os.path.exists(self.filename):
            with open(self.filename, "w", newline="") as file:
                writer = csv.writer(file)

                writer.writerow([
                    "timestamp",
                    "temperature",
                    "pressure",
                    "level",
                    "flow",
                    "heater",
                    "pump",
                    "valve",
                    "safety_status",
                    "alarm"
                ])

    def log(self, sensor_data, safety_result, outputs):
        """
        Store one process cycle in the CSV file.
        """

        alarms = safety_result.get("alarms", [])

        alarm_text = "; ".join(alarms) if alarms else ""

        with open(self.filename, "a", newline="") as file:
            writer = csv.writer(file)

            writer.writerow([
                datetime.now().isoformat(),
                sensor_data["temperature"],
                sensor_data["pressure"],
                sensor_data["level"],
                sensor_data["flow"],
                int(outputs["heater_on"]),
                int(outputs["pump_on"]),
                outputs["valve_position"],
                safety_result["status"],
                alarm_text
            ])
