from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Protocol


@dataclass(slots=True)
class ControlCommand:
    steering: float
    throttle: float


class Actuator(Protocol):
    def send(self, command: ControlCommand) -> None: ...
    def stop(self) -> None: ...
    def close(self) -> None: ...


@dataclass(slots=True)
class MockActuator:
    history: list[ControlCommand] = field(default_factory=list)

    def send(self, command: ControlCommand) -> None:
        self.history.append(command)

    def stop(self) -> None:
        self.history.append(ControlCommand(steering=0.0, throttle=0.0))

    def close(self) -> None:
        return None


class StdoutActuator:
    def send(self, command: ControlCommand) -> None:  # pragma: no cover - io
        print(f"[actuator] steering={command.steering:+.3f} throttle={command.throttle:.3f}")

    def stop(self) -> None:  # pragma: no cover - io
        print("[actuator] STOP")

    def close(self) -> None:  # pragma: no cover - io
        return None


class SerialLineActuator:
    """Sends newline-delimited JSON commands to a serial-connected controller.

    The controller firmware can parse lines like:
      {"type":"control","steering":0.12,"throttle":0.30}
      {"type":"stop"}
    """

    def __init__(
        self,
        *,
        port: str,
        baudrate: int = 115200,
        serial_factory=None,
        neutral_on_connect: bool = True,
    ):
        if not port:
            raise ValueError("Serial actuator port is required")
        if serial_factory is None:
            try:
                import serial  # type: ignore
            except Exception as exc:  # pragma: no cover - env dependent
                raise RuntimeError("pyserial is required for serial actuator backend.") from exc
            serial_factory = serial.Serial
        self._ser = serial_factory(port=port, baudrate=baudrate, timeout=1)
        if neutral_on_connect:
            self.stop()

    def _write_json_line(self, payload: dict) -> None:
        line = (json.dumps(payload, separators=(",", ":")) + "\n").encode("utf-8")
        self._ser.write(line)
        flush = getattr(self._ser, "flush", None)
        if callable(flush):
            flush()

    def send(self, command: ControlCommand) -> None:
        self._write_json_line({
            "type": "control",
            "steering": round(float(command.steering), 6),
            "throttle": round(float(command.throttle), 6),
        })

    def stop(self) -> None:
        self._write_json_line({"type": "stop"})

    def close(self) -> None:
        close = getattr(self._ser, "close", None)
        if callable(close):
            close()


def build_actuator(
    *,
    backend: str,
    serial_port: str | None = None,
    serial_baudrate: int = 115200,
) -> Actuator:
    if backend == "mock":
        return MockActuator()
    if backend == "stdout":
        return StdoutActuator()
    if backend == "serial":
        return SerialLineActuator(port=serial_port or "", baudrate=serial_baudrate)
    raise ValueError(f"Unsupported actuator backend: {backend}")
