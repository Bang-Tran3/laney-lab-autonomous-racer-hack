from __future__ import annotations

from typing import Literal

from pydantic import BaseModel


class HealthResponse(BaseModel):
    status: Literal["ok"]
    service: str = "vehicle-runtime"


class StatusResponse(BaseModel):
    running: bool
    estop: bool
    control_mode: Literal["learned", "safe_stop", "manual_override"]
    target_model_version: str | None
    loaded_model_version: str | None
    last_error: str | None
    last_steering: float | None
    last_throttle: float | None
    loop_count: int
    battery_percent: float | None
    battery_voltage_v: float | None
    battery_state: str
    session_active: bool
    session_id: str | None
    last_session_artifacts_dir: str | None
    manual_override_active: bool
    manual_override_remaining_ms: int | None


class ActionResponse(BaseModel):
    ok: bool
    message: str


class SessionStopResponse(BaseModel):
    ok: bool
    message: str
    session_id: str | None = None
    artifacts_dir: str | None = None
    uploaded: bool = False


class ControlCommandPayload(BaseModel):
    steering: float
    throttle: float


class ManualOverrideRequest(BaseModel):
    steering: float
    throttle: float
    duration_ms: int = 1000
