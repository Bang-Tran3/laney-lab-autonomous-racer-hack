from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


class BatteryMonitor(Protocol):
    def read(self) -> "BatterySnapshot": ...


@dataclass(slots=True)
class BatterySnapshot:
    voltage_v: float | None
    percent: float | None
    state: str


@dataclass(slots=True)
class MockBatteryMonitor:
    percent: float = 100.0
    drain_per_read: float = 0.02

    def read(self) -> BatterySnapshot:
        self.percent = max(0.0, self.percent - self.drain_per_read)
        if self.percent <= 10:
            state = "critical"
        elif self.percent <= 25:
            state = "low"
        else:
            state = "normal"
        voltage = 6.0 + (self.percent / 100.0) * 2.4
        return BatterySnapshot(voltage_v=round(voltage, 2), percent=round(self.percent, 2), state=state)

