from simulation.boiler import BoilerSimulator
from control.controller import BoilerController
from safety.safety_system import SafetySystem


def test_boiler_initialization():
    boiler = BoilerSimulator()

    sensor_data = boiler.get_sensor_data()

    assert "temperature" in sensor_data
    assert "pressure" in sensor_data
    assert "level" in sensor_data
    assert "flow" in sensor_data


def test_controller_initialization():
    controller = BoilerController()

    assert controller is not None


def test_safety_system_initialization():
    safety = SafetySystem()

    assert safety.status == "NORMAL"


def test_normal_operation():
    boiler = BoilerSimulator()
    controller = BoilerController()
    safety = SafetySystem()

    sensor_data = boiler.get_sensor_data()

    safety_result = safety.evaluate(sensor_data)

    outputs = controller.control(
        sensor_data,
        safety_result["status"]
    )

    assert safety_result["status"] == "NORMAL"
    assert outputs["heater_on"] is True
    assert outputs["pump_on"] is True
    assert 0 <= outputs["valve_position"] <= 100


def test_high_pressure_triggers_emergency():
    boiler = BoilerSimulator()
    safety = SafetySystem()

    boiler.inject_fault("high_pressure")

    sensor_data = boiler.get_sensor_data()
    safety_result = safety.evaluate(sensor_data)

    assert sensor_data["pressure"] >= 11.0
    assert safety_result["status"] == "EMERGENCY"
    assert "CRITICAL: HIGH PRESSURE" in safety_result["alarms"]


def test_emergency_trip_shuts_down_actuators():
    boiler = BoilerSimulator()
    controller = BoilerController()
    safety = SafetySystem()

    boiler.inject_fault("high_pressure")

    sensor_data = boiler.get_sensor_data()
    safety_result = safety.evaluate(sensor_data)

    outputs = controller.control(
        sensor_data,
        safety_result["status"]
    )

    assert safety_result["status"] == "EMERGENCY"
    assert outputs["heater_on"] is False
    assert outputs["pump_on"] is False
    assert outputs["valve_position"] == 100.0


def test_safety_trip_latches():
    boiler = BoilerSimulator()
    safety = SafetySystem()

    boiler.inject_fault("high_pressure")

    sensor_data = boiler.get_sensor_data()

    first_result = safety.evaluate(sensor_data)

    assert first_result["status"] == "EMERGENCY"

    latched_result = None

    for _ in range(10):
        boiler.update()
        sensor_data = boiler.get_sensor_data()
        latched_result = safety.evaluate(sensor_data)

        if "SAFETY TRIP LATCHED" in latched_result["alarms"]:
            break

    assert latched_result["status"] == "EMERGENCY"
    assert "SAFETY TRIP LATCHED" in latched_result["alarms"]


def test_operator_reset_after_safe_condition():
    boiler = BoilerSimulator()
    safety = SafetySystem()

    boiler.inject_fault("high_pressure")

    sensor_data = boiler.get_sensor_data()

    safety.evaluate(sensor_data)

    for _ in range(10):
        boiler.update()

    safe_data = boiler.get_sensor_data()

    if safe_data["pressure"] < 10.0:
        reset_result = safety.reset(safe_data)

        assert reset_result is True
        assert safety.status == "NORMAL"
