from __future__ import annotations

import argparse
import csv
import io
import json
import time
import zipfile
from datetime import datetime, timezone

import requests
from PIL import Image, ImageDraw


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _build_frames_zip_and_controls(frame_count: int = 4) -> tuple[bytes, bytes]:
    frames_zip = io.BytesIO()
    rows: list[dict[str, object]] = []

    with zipfile.ZipFile(frames_zip, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for i in range(frame_count):
            img = Image.new("RGB", (160, 120), color=(30 + i * 25, 70 + i * 15, 120 - i * 10))
            draw = ImageDraw.Draw(img)
            draw.rectangle((10 + i * 4, 10 + i * 3, 65 + i * 4, 55 + i * 3), outline=(255, 255, 255), width=2)
            draw.text((8, 95), f"frame {i}", fill=(255, 255, 0))
            jpg = io.BytesIO()
            img.save(jpg, format="JPEG", quality=85)
            zf.writestr(f"frames/{i:06d}.jpg", jpg.getvalue())

            rows.append(
                {
                    "frame_idx": i,
                    "timestamp_ms": i * 100,
                    "steering": [-0.4, -0.1, 0.1, 0.4][i % 4],
                    "throttle": 0.8,
                    "brake": 0.0,
                    "speed_mps": 2.0 + i * 0.1,
                    "is_off_track": "false",
                    "lap": 1,
                    "position_x": float(i),
                    "position_y": 0.0,
                    "heading_rad": 0.0,
                }
            )

    controls = io.StringIO()
    writer = csv.DictWriter(controls, fieldnames=list(rows[0].keys()))
    writer.writeheader()
    writer.writerows(rows)

    return frames_zip.getvalue(), controls.getvalue().encode("utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Seed one run into the shared API and verify a real training job completes.")
    parser.add_argument("--api-url", required=True, help="Base API URL, e.g. https://shared-runs-api-production.up.railway.app")
    parser.add_argument("--poll-seconds", type=float, default=4.0)
    parser.add_argument("--timeout-seconds", type=float, default=180.0)
    parser.add_argument("--epochs", type=int, default=1)
    args = parser.parse_args()

    api = args.api_url.rstrip("/")
    s = requests.Session()

    create_payload = {
        "user_id": "smoke-test-bot",
        "track_id": "oval",
        "mode": "manual",
        "sim_build": "smoke-script",
        "client_build": "codex",
        "notes": "trainer smoke test seeded run",
        "started_at": _utc_now_iso(),
    }
    create_resp = s.post(f"{api}/api/runs", json=create_payload, timeout=30)
    create_resp.raise_for_status()
    run_id = create_resp.json()["run_id"]

    frames_zip_bytes, controls_csv_bytes = _build_frames_zip_and_controls(frame_count=4)
    s.post(
        f"{api}/api/runs/{run_id}/frames",
        files={"file": ("frames.zip", frames_zip_bytes, "application/zip")},
        timeout=30,
    ).raise_for_status()
    s.post(
        f"{api}/api/runs/{run_id}/controls",
        files={"file": ("controls.csv", controls_csv_bytes, "text/csv")},
        timeout=30,
    ).raise_for_status()
    s.post(
        f"{api}/api/runs/{run_id}/finalize",
        json={
            "ended_at": _utc_now_iso(),
            "duration_s": 0.4,
            "frame_count": 4,
            "lap_count": 1,
            "off_track_count": 0,
            "best_lap_ms": 1234.5,
        },
        timeout=30,
    ).raise_for_status()

    job_resp = s.post(
        f"{api}/api/train/jobs",
        json={
            "dataset": {"run_ids": [run_id]},
            "hyperparams": {"epochs": args.epochs, "batch_size": 2, "learning_rate": 0.001},
            "export": {"set_active": True},
        },
        timeout=30,
    )
    job_resp.raise_for_status()
    job_id = job_resp.json()["job_id"]

    deadline = time.time() + args.timeout_seconds
    final_job: dict | None = None
    while time.time() < deadline:
        time.sleep(args.poll_seconds)
        job = s.get(f"{api}/api/train/jobs/{job_id}", timeout=30).json()
        if job["status"] in {"succeeded", "failed"}:
            final_job = job
            break

    if not final_job:
        raise SystemExit(f"Timed out waiting for training job {job_id}")
    if final_job["status"] != "succeeded":
        raise SystemExit(f"Training job failed: {json.dumps(final_job, indent=2)}")

    model_version = final_job["outputs"].get("model_version")
    if not model_version:
        raise SystemExit(f"Training job succeeded but no model_version was recorded: {json.dumps(final_job, indent=2)}")

    model = s.get(f"{api}/api/models/{model_version}", timeout=30).json()
    artifacts = model.get("artifacts", {})
    metrics = model.get("training", {}).get("metrics", {})
    if not artifacts.get("pytorch_uri"):
        raise SystemExit(f"Missing pytorch model artifact on {model_version}: {json.dumps(model, indent=2)}")
    if not artifacts.get("onnx_uri"):
        raise SystemExit(f"Missing ONNX model artifact on {model_version}: {json.dumps(model, indent=2)}")

    print(
        json.dumps(
            {
                "seed_run_id": run_id,
                "job_id": job_id,
                "model_version": model_version,
                "artifacts": artifacts,
                "metrics": metrics,
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
