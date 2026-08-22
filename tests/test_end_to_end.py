from simulation.boiler import BoilerSimulator
from instrumentation.sensors import BoilerInstrumentation
from instrumentation.signal_processing import SignalProcessor
from control.controller import BoilerController
from safety.safety_system import SafetySystem


def print_separator():
    print("-" * 90)


def run_system():

    boiler = BoilerSimulator()
    instrumentation = BoilerInstrumentation()
    processor = SignalProcessor()
    controller = BoilerController()
    safety = SafetySystem()

    print("=" * 90)
    print("INDUSTRIAL BOILER END-TO-END CONTROL SYSTEM")
    print("=" * 90)

    print()
    print("SYSTEM ARCHITECTURE")
    print(
        "Boiler -> Sensors -> 4-20 mA -> Signal Processing"
    )
    print(
        "-> Safety System -> Controller -> Actuators"
    )
    print()

    fault_injected = False
    reset_performed = False

    for cycle in range(1, 21):

        if cycle == 10 and not fault_injected:

            boiler.inject_fault(
                "high_pressure"
            )

            fault_injected = True

            print()
            print("!" * 90)
            print("HIGH PRESSURE FAULT INJECTED")
            print("PRESSURE FORCED TO 11 BAR")
            print("!" * 90)
            print()

        raw_process = boiler.get_sensor_data()

        transmitter_data = instrumentation.read(
            raw_process
        )

        process_data = processor.process(
            transmitter_data
        )

        safety_result = safety.evaluate(
            process_data
        )

        outputs = controller.control(
            process_data,
            safety_result["status"]
        )

        boiler.heater_on = outputs[
            "heater_on"
        ]

        boiler.pump_on = outputs[
            "pump_on"
        ]

        boiler.valve_position = outputs[
            "valve_position"
        ]

        print_separator()

        print(
            f"Cycle {cycle:02d}"
        )

        print(
            f"Temperature: "
            f"{process_data['temperature']:7.2f} °C"
        )

        print(
            f"Pressure:    "
            f"{process_data['pressure']:7.2f} bar"
        )

        print(
            f"Level:       "
            f"{process_data['level']:7.2f} %"
        )

        print(
            f"Flow:        "
            f"{process_data['flow']:7.2f} L/min"
        )

        print()

        print(
            f"TT-101: "
            f"{transmitter_data['temperature_mA']:.3f} mA"
        )

        print(
            f"PT-101: "
            f"{transmitter_data['pressure_mA']:.3f} mA"
        )

        print(
            f"LT-101: "
            f"{transmitter_data['level_mA']:.3f} mA"
        )

        print(
            f"FT-101: "
            f"{transmitter_data['flow_mA']:.3f} mA"
        )

        print()

        if safety_result["status"] == "EMERGENCY":

            print(
                "STATUS: EMERGENCY"
            )

            for alarm in safety_result[
                "alarms"
            ]:
                print(
                    f"ALARM: {alarm}"
                )

            print(
                "SAFETY TRIP: ACTIVE"
            )

        else:

            print(
                "STATUS: NORMAL"
            )

        print()

        print(
            f"Heater: "
            f"{'ON' if outputs['heater_on'] else 'OFF'}"
        )

        print(
            f"Pump:   "
            f"{'ON' if outputs['pump_on'] else 'OFF'}"
        )

        if safety_result["status"] == "EMERGENCY":
            valve_status = "OPEN"
        else:
            valve_status = (
                f"{outputs['valve_position']:.1f}%"
            )

        print(
            f"Valve:  {valve_status}"
        )

        print_separator()

        if (
            cycle == 15
            and fault_injected
            and not reset_performed
        ):

            print()
            print("OPERATOR RESET REQUEST")
            print()

            safe_process = {
                "temperature": process_data[
                    "temperature"
                ],
                "pressure": process_data[
                    "pressure"
                ],
                "level": process_data[
                    "level"
                ],
                "flow": process_data[
                    "flow"
                ],
            }

            if safe_process["pressure"] < 10.0:

                reset_result = safety.reset(
                    safe_process
                )

                if reset_result:

                    print(
                        "SAFETY RESET ACCEPTED"
                    )

                    reset_performed = True

                else:

                    print(
                        "SAFETY RESET REJECTED"
                    )

            else:

                print(
                    "RESET REJECTED: "
                    "PROCESS IS NOT SAFE"
                )

        boiler.update()

    print()
    print("=" * 90)
    print("END-TO-END SIMULATION COMPLETE")
    print("=" * 90)


if __name__ == "__main__":
    run_system()
