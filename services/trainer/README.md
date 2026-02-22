# Trainer Service

This service polls training jobs from the shared API, builds a dataset from uploaded simulator runs, trains a small CNN steering model, and uploads model artifacts back to the API.

## What it does now

- Polls queued training jobs from the API (worker mode) or runs a job by id
- Downloads shared run artifacts (`frames.zip`, `controls.csv`, `run.json`)
- Builds a local dataset snapshot manifest
- Trains a CNN steering regressor (PyTorch CPU)
- Exports ONNX (best-effort; now ONNX-compatible model architecture)
- Uploads `model.pt`, `model.onnx` (when export succeeds), and `config.json`
- Registers a model record and can mark it active

## What it does NOT do yet

- Model quality metrics
- Production-grade background worker supervision/observability
- Physical racer runtime integration

## Install (local)

```bash
cd services/trainer
python -m pip install -r requirements.txt
pip install torch --index-url https://download.pytorch.org/whl/cpu --extra-index-url https://pypi.org/simple
pip install onnx onnxscript
```

## Run a job (manual)

1. Create a training job via API:

```bash
curl -X POST "$API_URL/api/train/jobs" ^
  -H "Content-Type: application/json" ^
  -d "{\"dataset\":{\"modes\":[\"manual\"]},\"hyperparams\":{\"epochs\":1},\"export\":{\"onnx\":true}}"
```

2. Run the trainer job:

```bash
python -m trainer.train_job_runner --api-url "$API_URL" --job-id "<job_id>" --set-active
```

Artifacts are written under `services/trainer/data/` (or the configured `--output-root`).

## Worker mode (poll queued jobs)

```bash
python -m trainer.worker --api-url "$API_URL" --poll-seconds 15 --set-active
```

## Production smoke test (seed run + train)

Use the included script to seed one synthetic run and verify end-to-end training + ONNX upload:

```bash
python services/trainer/scripts/smoke_seed_and_train.py --api-url "$API_URL"
```

This exits non-zero if `model.pt` or `model.onnx` is missing on the resulting model record.

## Notes

- The trainer still supports placeholder pipeline validation when PyTorch is unavailable (`torch_not_installed`), but production should run the torch-enabled image.
