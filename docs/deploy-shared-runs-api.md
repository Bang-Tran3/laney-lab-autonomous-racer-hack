# Shared Data + Training Deploy (Railway)

This setup lets multiple students upload simulator runs into one shared dataset and process training jobs into shared model artifacts.

## What is live now

- Shared Runs API:
  - `POST /api/runs`
  - `POST /api/runs/{run_id}/frames`
  - `POST /api/runs/{run_id}/controls`
  - `POST /api/runs/{run_id}/finalize`
  - `GET /api/runs`, `GET /api/runs/{run_id}`
  - `GET /api/runs/{run_id}/artifacts/{frames|controls|run-json}`
- Models API:
  - `GET/POST /api/models`
  - `GET/POST /api/models/active`
  - `GET /api/models/{model_version}`
  - `POST /api/models/{model_version}/artifacts/{pytorch|onnx|config}`
- Training jobs API:
  - `POST /api/train/jobs`
  - `GET /api/train/jobs`
  - `GET /api/train/jobs/{job_id}`
  - `POST /api/train/jobs/{job_id}/update`
- Trainer worker (`services/trainer`) that polls queued jobs and uploads model artifacts back to the API

## Railway services (recommended)

Use one Railway project with three services:
- simulator (`laney-lab-autonomous-racer-hack`)
- shared API (`shared-runs-api`)
- trainer worker (`trainer-worker`)

Link/deploy from each service root:
- `services/api` uses `services/api/railway.json`
- `services/trainer` uses `services/trainer/railway.json`
- repo root `railway.json` remains the simulator deploy config

## Shared Runs API config (`shared-runs-api`)

### Required environment variables
- `DEEPRACER_API_DB_PATH=/data/app.db`
- `DEEPRACER_API_STORAGE_ROOT=/data/storage`
- `DEEPRACER_API_CORS_ORIGINS=https://<your-simulator-domain>`

### Persistent storage
Attach a persistent volume and mount it to:
- `/data`

At minimum, the service needs persistent storage for:
- SQLite database (`/data/app.db`)
- uploaded artifacts (`/data/storage/runs/...`, `/data/storage/models/...`)

## Trainer worker config (`trainer-worker`)

### Required environment variables
- `TRAINER_API_URL=https://<your-api-domain>`
- `TRAINER_POLL_SECONDS=15` (or similar)
- `TRAINER_OUTPUT_ROOT=/tmp/trainer-data`

The current trainer Docker image installs:
- `torch` CPU wheels
- `onnx`
- `onnxscript`

## Simulator configuration (`laney-lab-autonomous-racer-hack`)

In the simulator deployment, set:

- `NEXT_PUBLIC_API_URL=https://<your-api-domain>`

The simulator will:
- save locally first (localStorage + IndexedDB)
- queue runs for sync
- retry sync in the background when online

## Team workflow (today)

1. Team drives in the deployed simulator
2. Runs save locally first, then background sync uploads to the shared API
3. Create training jobs via `POST /api/train/jobs`
4. `trainer-worker` processes queued jobs and registers models
5. Fetch the active model via `/api/models/active` and `/api/models/{version}`

## Notes

- Real model training + ONNX export is working in production (verified on Feb 22, 2026).
- Simulator ONNX inference and physical racer runtime integration are still separate next steps.
