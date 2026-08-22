from simulation.boiler import BoilerSimulator
from control.controller import BoilerController
from safety.safety_system import SafetySystem
from logs.data_logger import DataLogger


def test_complete_boiler_integration():
    boiler = BoilerSimulator()
    controller = BoilerController()
    safety = SafetySystem()

    logger = DataLogger("logs/test_boiler_data.csv")

    normal_cycles = 9
    fault_cycle = 10
    reset_cycle = 16

    emergency_detected = False
    trip_latched = False
    reset_successful = False

    for cycle in range(1, 21):

        if cycle == fault_cycle:
            boiler.inject_fault("high_pressure")

        sensor_data = boiler.get_sensor_data()

        safety_result = safety.evaluate(sensor_data)

        outputs = controller.control(
            sensor_data,
            safety_result["status"]
        )

        boiler.heater_on = outputs["heater_on"]
        boiler.pump_on = outputs["pump_on"]
        boiler.valve_position = outputs["valve_position"]

        logger.log(
            sensor_data,
            safety_result,
            outputs
        )

        if cycle < fault_cycle:
            assert safety_result["status"] == "NORMAL"
            assert outputs["heater_on"] is True
            assert outputs["pump_on"] is True

        if cycle == fault_cycle:
            assert safety_result["status"] == "EMERGENCY"
            assert outputs["heater_on"] is False
            assert outputs["pump_on"] is False
            assert outputs["valve_position"] == 100.0

            emergency_detected = True

        if safety_result["status"] == "EMERGENCY":
            emergency_detected = True

        if "SAFETY TRIP LATCHED" in safety_result["alarms"]:
            trip_latched = True

        if cycle == reset_cycle:
            if sensor_data["pressure"] < 10.0:
                reset_successful = safety.reset(sensor_data)

        boiler.update()

    assert emergency_detected is True
    assert trip_latched is True
    assert reset_successful is True
    assert safety.status == "NORMAL"
