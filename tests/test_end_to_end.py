from simulation.boiler import BoilerSimulator
from instrumentation.sensors import BoilerInstrumentation
from instrumentation.signal_processing import SignalProcessor
from control.controller import BoilerController
from safety.safety_system import SafetySystem


def test_end_to_end_control_system():
    boiler = BoilerSimulator()
    instrumentation = BoilerInstrumentation()
    processor = SignalProcessor()
    controller = BoilerController()
    safety = SafetySystem()

    fault_injected = False
    emergency_detected = False
    trip_latched = False
    reset_performed = False

    for cycle in range(1, 21):

        # Inject high-pressure fault
        if cycle == 10 and not fault_injected:
            boiler.inject_fault("high_pressure")
            fault_injected = True

        # Read raw process variables
        raw_process = boiler.get_sensor_data()

        # Convert process variables to transmitter signals
        transmitter_data = instrumentation.read(raw_process)

        # Convert 4–20 mA signals back into engineering units
        process_data = processor.process(transmitter_data)

        # Safety evaluation
        safety_result = safety.evaluate(process_data)

        # Controller
        outputs = controller.control(
            process_data,
            safety_result["status"]
        )

        # Apply actuator commands
        boiler.heater_on = outputs["heater_on"]
        boiler.pump_on = outputs["pump_on"]
        boiler.valve_position = outputs["valve_position"]

        # Verify 4–20 mA instrumentation
        assert 4.0 <= transmitter_data["temperature_mA"] <= 20.0
        assert 4.0 <= transmitter_data["pressure_mA"] <= 20.0
        assert 4.0 <= transmitter_data["level_mA"] <= 20.0
        assert 4.0 <= transmitter_data["flow_mA"] <= 20.0

        # Verify processed values exist
        assert "temperature" in process_data
        assert "pressure" in process_data
        assert "level" in process_data
        assert "flow" in process_data

        # Normal operation
        if cycle < 10:
            assert safety_result["status"] == "NORMAL"

        # Fault condition
        if cycle == 10:
            assert safety_result["status"] == "EMERGENCY"
            assert outputs["heater_on"] is False
            assert outputs["pump_on"] is False
            assert outputs["valve_position"] == 100.0

            emergency_detected = True

        # Track emergency condition
        if safety_result["status"] == "EMERGENCY":
            emergency_detected = True

        # Track latched trip
        if "SAFETY TRIP LATCHED" in safety_result["alarms"]:
            trip_latched = True

        # Operator reset
        if cycle == 15 and fault_injected:
            if process_data["pressure"] < 10.0:
                reset_result = safety.reset(process_data)

                if reset_result:
                    reset_performed = True

        # Advance physical process
        boiler.update()

    # Final system verification
    assert fault_injected is True
    assert emergency_detected is True
    assert trip_latched is True
    assert reset_performed is True
    assert safety.status == "NORMAL"
