from __future__ import annotations

import csv
import json
import zipfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

from trainer.api_client import TrainerApiClient


@dataclass
class DatasetBuildResult:
    dataset_id: str
    root_dir: Path
    manifest_path: Path
    run_count: int
    frame_count: int


def _safe_dataset_id() -> str:
    from datetime import datetime, timezone

    return "dataset-" + datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def _read_controls_count(csv_path: Path) -> int:
    with csv_path.open("r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return sum(1 for _ in reader)


def build_dataset_snapshot(
    api: TrainerApiClient,
    output_root: Path,
    *,
    run_ids: Iterable[str] | None = None,
    manual_only: bool = True,
    max_runs: int = 200,
) -> DatasetBuildResult:
    dataset_id = _safe_dataset_id()
    dataset_root = output_root / dataset_id
    dataset_root.mkdir(parents=True, exist_ok=True)

    if run_ids is None:
        runs = api.list_runs(mode="manual" if manual_only else None, limit=max_runs)
    else:
        runs = [api.get_run(run_id) for run_id in run_ids]

    selected_runs = [r for r in runs if r.get("status") == "complete" and r.get("artifacts", {}).get("frames_uri") and r.get("artifacts", {}).get("controls_uri")]

    total_frames = 0
    run_manifests: list[dict[str, Any]] = []
    for run in selected_runs:
        run_id = run["run_id"]
        run_dir = dataset_root / "runs" / run_id
        run_dir.mkdir(parents=True, exist_ok=True)

        frames_zip_path = api.download_run_artifact(run_id, "frames", run_dir / "frames.zip")
        controls_csv_path = api.download_run_artifact(run_id, "controls", run_dir / "controls.csv")
        api.download_run_artifact(run_id, "run-json", run_dir / "run.json")

        extracted_frames_dir = run_dir / "frames"
        extracted_frames_dir.mkdir(exist_ok=True)
        with zipfile.ZipFile(frames_zip_path, "r") as zf:
            zf.extractall(extracted_frames_dir)

        frame_count = _read_controls_count(controls_csv_path)
        total_frames += frame_count
        run_manifests.append(
            {
                "run_id": run_id,
                "track_id": run["track_id"],
                "mode": run["mode"],
                "frame_count": frame_count,
                "paths": {
                    "frames_zip": str(frames_zip_path.relative_to(dataset_root).as_posix()),
                    "frames_root": str(extracted_frames_dir.relative_to(dataset_root).as_posix()),
                    "controls_csv": str(controls_csv_path.relative_to(dataset_root).as_posix()),
                    "run_json": str((run_dir / "run.json").relative_to(dataset_root).as_posix()),
                },
            }
        )

    manifest = {
        "dataset_id": dataset_id,
        "created_at": __import__("datetime").datetime.utcnow().isoformat() + "Z",
        "run_count": len(run_manifests),
        "frame_count": total_frames,
        "runs": run_manifests,
    }
    manifest_path = dataset_root / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    return DatasetBuildResult(
        dataset_id=dataset_id,
        root_dir=dataset_root,
        manifest_path=manifest_path,
        run_count=len(run_manifests),
        frame_count=total_frames,
    )

