from simulation.boiler import BoilerSimulator
from control.controller import BoilerController
from safety.safety_system import SafetySystem
from logs.data_logger import DataLogger


def print_status(cycle, sensor_data, safety_result, outputs):
    """Display the current boiler process state."""

    print("-" * 90)

    print(
        f"Cycle {cycle:02d} | "
        f"Temperature: {sensor_data['temperature']:6.2f} °C | "
        f"Pressure: {sensor_data['pressure']:5.2f} bar | "
        f"Level: {sensor_data['level']:5.2f}% | "
        f"Flow: {sensor_data['flow']:5.2f} L/min"
    )

    if safety_result["status"] == "NORMAL":

        print("Status: 🟢 NORMAL")

        print(
            f"Heater: {'ON' if outputs['heater_on'] else 'OFF'} | "
            f"Pump: {'ON' if outputs['pump_on'] else 'OFF'} | "
            f"Valve: {outputs['valve_position']:.1f}% | "
            f"Buzzer: OFF"
        )

    else:

        print("Status: 🔴 EMERGENCY")

        for alarm in safety_result["alarms"]:
            print(f"🚨 ALARM: {alarm}")

        print("🛑 SAFETY TRIP ACTIVE")

        print(
            f"Heater: {'ON' if outputs['heater_on'] else 'OFF'} | "
            f"Pump: {'ON' if outputs['pump_on'] else 'OFF'} | "
            f"Valve: OPEN | "
            f"Buzzer: ON"
        )


def run_process():
    """
    End-to-end industrial boiler monitoring demonstration.

    Demonstrates:

    1. Normal operation
    2. High-pressure fault injection
    3. Automatic safety trip
    4. Latched emergency condition
    5. Manual operator reset
    6. CSV data logging
    """

    boiler = BoilerSimulator()
    controller = BoilerController()
    safety = SafetySystem()

    # Create data logger
    logger = DataLogger("logs/boiler_data.csv")

    print()
    print("=" * 90)
    print("        INDUSTRIAL BOILER MONITORING & SAFETY SYSTEM")
    print("=" * 90)
    print()

    fault_cycle = 10
    reset_cycle = 16

    for cycle in range(1, 21):

        # -------------------------------------------------
        # HIGH PRESSURE FAULT
        # -------------------------------------------------

        if cycle == fault_cycle:

            print()
            print("!" * 90)
            print("              ⚠️  FAULT INJECTION ACTIVATED")
            print("              HIGH PRESSURE FAULT")
            print("              PRESSURE FORCED TO 11 BAR")
            print("!" * 90)
            print()

            boiler.inject_fault("high_pressure")

        # -------------------------------------------------
        # READ SENSOR DATA
        # -------------------------------------------------

        sensor_data = boiler.get_sensor_data()

        # -------------------------------------------------
        # SAFETY EVALUATION
        # -------------------------------------------------

        safety_result = safety.evaluate(sensor_data)

        # -------------------------------------------------
        # CONTROLLER
        # -------------------------------------------------

        outputs = controller.control(
            sensor_data,
            safety_result["status"]
        )

        # -------------------------------------------------
        # APPLY ACTUATOR COMMANDS
        # -------------------------------------------------

        boiler.heater_on = outputs["heater_on"]
        boiler.pump_on = outputs["pump_on"]
        boiler.valve_position = outputs["valve_position"]

        # -------------------------------------------------
        # LOG DATA
        # -------------------------------------------------

        logger.log(
            sensor_data,
            safety_result,
            outputs
        )

        # -------------------------------------------------
        # DISPLAY
        # -------------------------------------------------

        print_status(
            cycle,
            sensor_data,
            safety_result,
            outputs
        )

        # -------------------------------------------------
        # OPERATOR RESET
        # -------------------------------------------------

        if cycle == reset_cycle:

            print()
            print("+" * 90)
            print("              👷 OPERATOR RESET REQUEST")
            print("+" * 90)

            reset_result = safety.reset(sensor_data)

            if reset_result:
                print("✅ RESET ACCEPTED")
                print("Safety interlock cleared.")
            else:
                print("❌ RESET REJECTED")
                print("Process conditions are not safe.")

            print("+" * 90)
            print()

        # -------------------------------------------------
        # ADVANCE PROCESS
        # -------------------------------------------------

        boiler.update()

    print()
    print("=" * 90)
    print("                  SIMULATION COMPLETE")
    print("=" * 90)
    print()

    print("📁 Process data saved to:")
    print("   logs/boiler_data.csv")
    print()


if __name__ == "__main__":
    run_process()
