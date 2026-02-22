from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI

from vehicle_runtime.config import load_config
from vehicle_runtime.runtime import VehicleRuntime
from vehicle_runtime.schemas import (
    ActionResponse,
    ControlCommandPayload,
    HealthResponse,
    ManualOverrideRequest,
    SessionStopResponse,
    StatusResponse,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    cfg = load_config()
    runtime = VehicleRuntime(cfg)
    app.state.runtime = runtime
    if cfg.autostart:
        runtime.start()
    try:
        yield
    finally:
        runtime.close()


app = FastAPI(title="Vehicle Runtime", version="0.1.0", lifespan=lifespan)


@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(status="ok")


@app.get("/status", response_model=StatusResponse)
def status() -> StatusResponse:
    snap = app.state.runtime.snapshot()
    return StatusResponse(
        running=snap.running,
        estop=snap.estop,
        control_mode=snap.control_mode if snap.control_mode in {"learned", "safe_stop", "manual_override"} else "safe_stop",
        target_model_version=snap.target_model_version,
        loaded_model_version=snap.loaded_model_version,
        last_error=snap.last_error,
        last_steering=snap.last_steering,
        last_throttle=snap.last_throttle,
        loop_count=snap.loop_count,
        battery_percent=snap.battery_percent,
        battery_voltage_v=snap.battery_voltage_v,
        battery_state=snap.battery_state,
        session_active=snap.session_active,
        session_id=snap.session_id,
        last_session_artifacts_dir=snap.last_session_artifacts_dir,
        manual_override_active=snap.manual_override_active,
        manual_override_remaining_ms=snap.manual_override_remaining_ms,
    )


@app.post("/control/start", response_model=ActionResponse)
def start_loop() -> ActionResponse:
    app.state.runtime.start()
    return ActionResponse(ok=True, message="control loop started")


@app.post("/control/stop", response_model=ActionResponse)
def stop_loop() -> ActionResponse:
    app.state.runtime.stop()
    return ActionResponse(ok=True, message="control loop stopped")


@app.post("/control/estop", response_model=ActionResponse)
def estop() -> ActionResponse:
    app.state.runtime.set_estop(True)
    return ActionResponse(ok=True, message="emergency stop engaged")


@app.post("/control/release-estop", response_model=ActionResponse)
def release_estop() -> ActionResponse:
    app.state.runtime.set_estop(False)
    return ActionResponse(ok=True, message="emergency stop released")


@app.post("/control/manual-override", response_model=ActionResponse)
def manual_override(payload: ManualOverrideRequest) -> ActionResponse:
    app.state.runtime.set_manual_override(payload.steering, payload.throttle, duration_ms=payload.duration_ms)
    return ActionResponse(ok=True, message=f"manual override active for {payload.duration_ms}ms")


@app.post("/control/manual-override/clear", response_model=ActionResponse)
def clear_manual_override() -> ActionResponse:
    app.state.runtime.clear_manual_override()
    return ActionResponse(ok=True, message="manual override cleared")


@app.post("/control/step", response_model=ControlCommandPayload)
def step_once() -> ControlCommandPayload:
    cmd = app.state.runtime.step_once()
    return ControlCommandPayload(steering=cmd.steering, throttle=cmd.throttle)


@app.post("/model/reload", response_model=ActionResponse)
def reload_model() -> ActionResponse:
    app.state.runtime.reload_model()
    return ActionResponse(ok=True, message="model reload triggered")


@app.post("/session/start", response_model=ActionResponse)
def session_start() -> ActionResponse:
    session_id = app.state.runtime.start_session()
    return ActionResponse(ok=True, message=f"session started: {session_id}")


@app.post("/session/stop", response_model=SessionStopResponse)
def session_stop(upload: bool = False) -> SessionStopResponse:
    artifacts = app.state.runtime.stop_session(upload=upload)
    if not artifacts:
        return SessionStopResponse(ok=True, message="no active session", uploaded=False)
    return SessionStopResponse(
        ok=True,
        message="session stopped",
        session_id=artifacts.session_id,
        artifacts_dir=str(artifacts.root_dir),
        uploaded=upload,
    )


@app.post("/session/upload-latest", response_model=ActionResponse)
def session_upload_latest() -> ActionResponse:
    uploaded = app.state.runtime.upload_latest_session()
    return ActionResponse(ok=True, message="latest session uploaded" if uploaded else "no session artifacts to upload")
