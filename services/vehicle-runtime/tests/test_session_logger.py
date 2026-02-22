import json
import zipfile

import numpy as np

from vehicle_runtime.actuators import ControlCommand
from vehicle_runtime.session_logger import RunSessionLogger


def test_session_logger_exports_frames_controls_and_run_json(tmp_path):
    logger = RunSessionLogger(
        cache_dir=tmp_path,
        user_id="tester",
        track_id="track-a",
        sim_build="physical-runtime",
        client_build="vehicle-runtime",
    )
    session_id = logger.start(model_version="v0007")
    frame = np.zeros((120, 160, 3), dtype=np.uint8)
    logger.record(frame_rgb=frame, command=ControlCommand(steering=0.2, throttle=0.3), control_mode="learned")
    logger.record(frame_rgb=frame, command=ControlCommand(steering=0.0, throttle=0.0), control_mode="safe_stop")
    artifacts = logger.stop()

    assert artifacts is not None
    assert artifacts.session_id == session_id
    assert artifacts.frames_zip_path.exists()
    assert artifacts.controls_csv_path.exists()
    assert artifacts.run_json_path.exists()

    with zipfile.ZipFile(artifacts.frames_zip_path, "r") as zf:
        names = zf.namelist()
        assert "frames/000000.jpg" in names
        assert "frames/000001.jpg" in names

    controls_text = artifacts.controls_csv_path.read_text(encoding="utf-8")
    assert "frame_idx,timestamp_ms,steering,throttle,control_mode" in controls_text
    assert "learned" in controls_text
    assert "safe_stop" in controls_text

    run_meta = json.loads(artifacts.run_json_path.read_text(encoding="utf-8"))
    assert run_meta["user_id"] == "tester"
    assert run_meta["track_id"] == "track-a"
    assert run_meta["model_version"] == "v0007"

