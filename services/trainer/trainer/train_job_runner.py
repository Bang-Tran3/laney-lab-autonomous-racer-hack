from __future__ import annotations

import argparse
import json
from pathlib import Path

from trainer.api_client import TrainerApiClient
from trainer.dataset import build_dataset_snapshot
from trainer.train import train_from_dataset_snapshot


def _next_model_version(existing_versions: list[str]) -> str:
    nums = []
    for version in existing_versions:
        if version.startswith("v") and version[1:].isdigit():
            nums.append(int(version[1:]))
    next_num = (max(nums) + 1) if nums else 1
    return f"v{next_num:04d}"


def run_job(api_url: str, job_id: str, output_root: Path, set_active: bool = False) -> None:
    api = TrainerApiClient(api_url)
    job = api.get_training_job(job_id)
    config = job.get("config", {})
    dataset_cfg = config.get("dataset", {})
    run_ids = dataset_cfg.get("run_ids") or None

    api.update_training_job(job_id, {"status": "running", "progress": {"stage": "dataset", "epoch": 0}})

    dataset_result = build_dataset_snapshot(
        api,
        output_root=output_root,
        run_ids=run_ids,
        manual_only=not bool(run_ids),
        max_runs=int(dataset_cfg.get("max_runs", 200)),
    )

    # Placeholder "training" artifact: write a training summary for now.
    models_root = output_root / "models"
    models_root.mkdir(parents=True, exist_ok=True)

    model_list = api.list_models(limit=200)
    next_version = _next_model_version([m["model_version"] for m in model_list])

    model_dir = models_root / next_version
    model_dir.mkdir(parents=True, exist_ok=True)
    hyperparams = config.get("hyperparams", {})
    api.update_training_job(job_id, {"status": "running", "progress": {"stage": "training", "epoch": 0}})
    training_outputs = train_from_dataset_snapshot(
        dataset_result.root_dir,
        model_dir,
        epochs=int(hyperparams.get("epochs", 3)),
        batch_size=int(hyperparams.get("batch_size", 32)),
        learning_rate=float(hyperparams.get("learning_rate", 3e-4)),
    )

    summary_path = model_dir / "training-summary.json"
    summary_payload = {
        "model_version": next_version,
        "dataset_id": dataset_result.dataset_id,
        "run_count": dataset_result.run_count,
        "frame_count": dataset_result.frame_count,
        "trainer_mode": training_outputs.mode,
        "metrics": training_outputs.metrics,
    }
    summary_path.write_text(json.dumps(summary_payload, indent=2), encoding="utf-8")

    model_record = api.create_model(
        {
            "model_version": next_version,
            "status": "ready",
            "architecture": {
                "type": "cnn_regression",
                "input": {"width": 160, "height": 120, "channels": 3},
                "output": {"steering": "float[-1,1]"},
            },
            "training": {
                "dataset_id": dataset_result.dataset_id,
                "run_ids": run_ids or [],
                "frames_total": dataset_result.frame_count,
                "metrics": training_outputs.metrics,
            },
            "artifacts": {
                "pytorch_uri": None,
                "onnx_uri": None,
                "openvino_uri": None,
            },
        }
    )
    _ = model_record

    if training_outputs.pytorch_path and training_outputs.pytorch_path.exists():
        api.upload_model_artifact(next_version, "pytorch", training_outputs.pytorch_path)
    if training_outputs.onnx_path and training_outputs.onnx_path.exists() and training_outputs.onnx_path.suffix.lower() == ".onnx":
        api.upload_model_artifact(next_version, "onnx", training_outputs.onnx_path)
    api.upload_model_artifact(next_version, "config", summary_path)

    if set_active:
        api.set_active_model(next_version)

    api.update_training_job(
        job_id,
        {
            "status": "succeeded",
            "progress": {"stage": "complete", "epoch": int(hyperparams.get("epochs", 1)), "epochs": int(hyperparams.get("epochs", 1))},
            "output_model_version": next_version,
        },
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Training job runner scaffold for shared DeepRacer runs")
    parser.add_argument("--api-url", required=True, help="Base URL for the FastAPI service, e.g. https://...up.railway.app")
    parser.add_argument("--job-id", required=True, help="Training job ID from POST /api/train/jobs")
    parser.add_argument("--output-root", default="services/trainer/data", help="Where dataset snapshots and artifacts are written")
    parser.add_argument("--set-active", action="store_true", help="Set the newly registered model as active")
    args = parser.parse_args()

    run_job(api_url=args.api_url, job_id=args.job_id, output_root=Path(args.output_root), set_active=args.set_active)


if __name__ == "__main__":
    main()
