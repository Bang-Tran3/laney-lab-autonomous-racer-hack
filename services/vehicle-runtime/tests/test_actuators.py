import json

from vehicle_runtime.actuators import ControlCommand, SerialLineActuator, build_actuator


class FakeSerialPort:
    def __init__(self, **kwargs):
        self.kwargs = kwargs
        self.writes: list[bytes] = []
        self.closed = False

    def write(self, data: bytes):
        self.writes.append(data)
        return len(data)

    def flush(self):
        return None

    def close(self):
        self.closed = True


def test_serial_line_actuator_writes_json_lines():
    created = {}

    def fake_factory(**kwargs):
        created["port"] = FakeSerialPort(**kwargs)
        return created["port"]

    actuator = SerialLineActuator(port="COM7", baudrate=57600, serial_factory=fake_factory, neutral_on_connect=False)
    actuator.send(ControlCommand(steering=0.125, throttle=0.3))
    actuator.stop()
    actuator.close()

    port = created["port"]
    assert port.kwargs["port"] == "COM7"
    assert port.kwargs["baudrate"] == 57600
    first = json.loads(port.writes[0].decode("utf-8"))
    second = json.loads(port.writes[1].decode("utf-8"))
    assert first == {"type": "control", "steering": 0.125, "throttle": 0.3}
    assert second == {"type": "stop"}
    assert port.closed is True


def test_build_actuator_supports_mock_and_stdout():
    assert build_actuator(backend="mock").__class__.__name__ == "MockActuator"
    assert build_actuator(backend="stdout").__class__.__name__ == "StdoutActuator"

