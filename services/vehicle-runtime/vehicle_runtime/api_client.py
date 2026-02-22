from __future__ import annotations

from pathlib import Path
from typing import Any

import requests


class VehicleApiClient:
    def __init__(self, base_url: str, timeout_s: float = 15.0):
        self.base_url = base_url.rstrip("/")
        self.timeout_s = timeout_s
        self.session = requests.Session()

    def _url(self, path: str) -> str:
        return f"{self.base_url}{path}"

    def _json(self, method: str, path: str, **kwargs) -> dict[str, Any]:
        resp = self.session.request(method, self._url(path), timeout=self.timeout_s, **kwargs)
        resp.raise_for_status()
        return resp.json()

    def get_active_model_version(self) -> str | None:
        payload = self._json("GET", "/api/models/active")
        return payload.get("active_model_version")

    def get_model(self, model_version: str) -> dict[str, Any]:
        return self._json("GET", f"/api/models/{model_version}")

    def download_model_onnx(self, model_version: str, out_path: Path) -> Path:
        out_path.parent.mkdir(parents=True, exist_ok=True)
        resp = self.session.get(self._url(f"/api/models/{model_version}/artifacts/onnx"), timeout=self.timeout_s)
        resp.raise_for_status()
        out_path.write_bytes(resp.content)
        return out_path

    def create_run(self, payload: dict[str, Any]) -> dict[str, Any]:
        return self._json("POST", "/api/runs", json=payload)

    def upload_run_frames(self, run_id: str, frames_zip_path: Path) -> dict[str, Any]:
        with frames_zip_path.open("rb") as f:
            files = {"file": (frames_zip_path.name, f, "application/zip")}
            resp = self.session.post(self._url(f"/api/runs/{run_id}/frames"), files=files, timeout=self.timeout_s)
        resp.raise_for_status()
        return resp.json()

    def upload_run_controls(self, run_id: str, controls_csv_path: Path) -> dict[str, Any]:
        with controls_csv_path.open("rb") as f:
            files = {"file": (controls_csv_path.name, f, "text/csv")}
            resp = self.session.post(self._url(f"/api/runs/{run_id}/controls"), files=files, timeout=self.timeout_s)
        resp.raise_for_status()
        return resp.json()

    def finalize_run(self, run_id: str, payload: dict[str, Any]) -> dict[str, Any]:
        return self._json("POST", f"/api/runs/{run_id}/finalize", json=payload)
