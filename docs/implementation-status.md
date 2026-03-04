# Implementation Status (Feb 22, 2026)

This replaces the old implementation planning doc with an implementation/status snapshot.

## Implemented Now (Phases A-C baseline)

### Forward-facing AI camera capture
- Added a car-mounted POV camera rendered offscreen at `160x120`
- Capture runs at ~`10 FPS` while driving/autonomous mode is active
- Capture labels each frame with `timestamp_ms`, `steering`, `throttle`, and `speed`

### In-game AI camera preview (PIP)
- Added a top-right HUD overlay showing the low-res camera feed the model will see
- Added a show/hide toggle for the preview
- Capture continues even when the PIP is hidden

### Local image frame storage (IndexedDB)
- Camera image frames are buffered in memory during a run
- On `Run Complete`, buffered image frames are saved into IndexedDB
- Run metadata remains in localStorage for the existing dashboard flow

### Run export (.zip)
- Run Complete overlay now includes `Download Run (.zip)`
- Dashboard header includes `All Runs .zip` bulk export (all runs with image captures)
- Dashboard run table includes per-run capture download buttons
- Zip format contains:
  - `frames/000000.jpg`, `frames/000001.jpg`, ...
  - `controls.csv`
  - `run.json`

### UI / UX preservation
- Existing chase camera and driving UI remain the primary experience
- New camera PIP is additive and toggleable
- Existing run flow, pause/stop controls, and dashboard layout are preserved

## Implemented Now (Phase B - Shared API)

### Shared run collection API (`services/api`)
- FastAPI service with SQLite metadata + filesystem artifact storage
- Run create/upload/finalize/list/get endpoints
- Run artifact download endpoints (`frames`, `controls`, `run-json`)
- Model registry endpoints (`/api/models`, `/api/models/active`)
- Training job endpoints (`/api/train/jobs`, status/update)

### Offline sync queue from simulator to API
- Simulator saves locally first, then enqueues sync jobs
- Background sync retries on load, on interval, and when network returns
- Shared data collection works across multiple users/browsers once `NEXT_PUBLIC_API_URL` is configured

## Implemented Now (Phase C - Initial Training Pipeline)

### Trainer worker (`services/trainer`)
- Polls queued training jobs
- Downloads shared run artifacts and builds dataset snapshots
- Trains a CNN steering regressor (PyTorch CPU)
- Exports ONNX and uploads model artifacts to the API
- Registers model versions and can set the active model

### Production verification (completed)
- Shared API deployed on Railway with persistent volume storage
- Trainer worker deployed on Railway with torch+onnx+onnxscript installed
- Real training job succeeded in production from a valid seeded run
- ONNX artifact upload verified (`model.onnx`)
- Active model endpoint verified (later advanced to `v0007` during simulator inference smoke testing)

## Implemented Now (Phase D - Simulator Inference)

### Browser ONNX inference (`onnxruntime-web`)
- Simulator fetches active model version from `/api/models/active`
- Browser downloads the ONNX artifact from `/api/models/{version}/artifacts/onnx`
- A background inference runner uses the existing `160x120` car POV camera feed
- Autonomous steering uses learned model predictions when fresh; waypoint AI remains automatic fallback
- HUD now shows `Loading model...`, `Model vXXXX`, or waypoint fallback state
- In-game AI Model panel supports:
  - active vs pinned model version selection
  - loaded-model/runtime status display
  - explicit `Learned Model` vs `Waypoint Demo` toggle for A/B testing

### Production verification (completed)
- Deployed simulator loads active model and transitions HUD from `Loading model...` to `Model v0007`
- Autonomous mode runs with browser ONNX inference active (smoke-tested on deployed Railway app)

## Implemented Now (Phase F - Physical Runtime foundation)

### Vehicle runtime service (`services/vehicle-runtime`)
- New FastAPI service for physical racer runtime orchestration
- Shared API model loader (active or pinned model version) with ONNX artifact download
- ONNX inference predictor path (`onnxruntime`) using simulator-matched preprocessing (`160x120 RGB -> NCHW float32`)
- Pluggable frame source adapters:
  - mock frame source (for development/testing)
  - OpenCV camera source (for real camera devices)
- Pluggable actuator adapters:
  - mock actuator (records commands)
  - stdout actuator (debug)
- Safety policy layer:
  - steering/throttle bounds
  - emergency stop override to zero commands
  - fail-safe stop on inference/camera/model load errors
- Deterministic manual override layer:
  - API-triggered operator takeover command
  - timeout-based return to learned inference
  - still bounded by safety clamps and superseded by e-stop
- Control/status endpoints:
  - `/status`, `/control/start`, `/control/stop`, `/control/estop`, `/control/release-estop`, `/control/step`, `/model/reload`

### Vehicle runtime validation
- Unit tests added for safety policy and runtime loop behavior (mock mode)
- `pytest -q services/vehicle-runtime/tests` passes
- Manual override precedence/expiry tests included in `services/vehicle-runtime/tests`
- Hardware bring-up stubs/checklist added for classmate parallel work:
  - `services/vehicle-runtime/HARDWARE_HANDOFF_CHECKLIST.md`
  - `services/vehicle-runtime/hardware-profile.stub.json`
  - `services/vehicle-runtime/SERIAL_BRIDGE_PROTOCOL.md`

## Not Implemented Yet (Remaining Roadmap)

### Phase D - Model inference in simulator (remaining)
- Better confidence/health heuristics and recovery behavior
- Throttle/brake model output support (currently steering-only; throttle is rule-based)

### Phase E - Shared dashboard/metrics
- API-backed dashboard data
- Model timeline and leaderboard views
- Shared class metrics across browsers/users

### Phase F - Physical racer integration (remaining)
- Hardware-specific actuator adapter (servo/ESC or ROS/device bridge)
- Battery telemetry + safety monitoring integration
- Obstacle sensing/safety override layer
- On-vehicle telemetry/run logging back to shared API
- Deployment packaging for target hardware platform(s)

## Validation Performed
- `npm run lint` (passes; warnings cleaned except project defaults before cleanup)
- `npm run build` (passes)
- Browser smoke test for `/` and `/dashboard` on local dev server (page loads and controls render)
- `pytest -q` for `services/api` (passes)
- Trainer smoke training jobs on deployed Railway worker (real `model.pt` + `model.onnx` uploaded)
- `pytest -q services/vehicle-runtime/tests` (passes)

## Notes
- The deleted `docs/implementation-plan.md` described the full multi-phase roadmap.
- Phase D is substantially implemented for simulator use (active/pinned model inference + fallback + A/B toggle).
- Physical racer runtime foundation now exists, but hardware-specific integration and safety subsystems are still pending.
- Photo-based environment planning for lab/quad sim-to-real work is documented in `docs/lab-and-quad-photo-sim-plan.md`.
