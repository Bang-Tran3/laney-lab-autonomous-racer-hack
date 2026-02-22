from __future__ import annotations

from pathlib import Path
from typing import Any

import requests


class TrainerApiClient:
    def __init__(self, base_url: str, timeout_s: float = 30.0) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout_s = timeout_s
        self.session = requests.Session()

    def _url(self, path: str) -> str:
        return f"{self.base_url}{path}"

    def _json(self, method: str, path: str, **kwargs) -> dict[str, Any]:
        resp = self.session.request(method, self._url(path), timeout=self.timeout_s, **kwargs)
        resp.raise_for_status()
        return resp.json()

    def list_runs(self, *, mode: str | None = None, limit: int = 200) -> list[dict[str, Any]]:
        params: dict[str, Any] = {"limit": limit}
        if mode:
            params["mode"] = mode
        payload = self._json("GET", "/api/runs", params=params)
        return payload.get("items", [])

    def list_models(self, *, status: str | None = None, limit: int = 200) -> list[dict[str, Any]]:
        params: dict[str, Any] = {"limit": limit}
        if status:
            params["status"] = status
        payload = self._json("GET", "/api/models", params=params)
        return payload.get("items", [])

    def get_run(self, run_id: str) -> dict[str, Any]:
        return self._json("GET", f"/api/runs/{run_id}")

    def download_run_artifact(self, run_id: str, artifact_kind: str, out_path: Path) -> Path:
        out_path.parent.mkdir(parents=True, exist_ok=True)
        resp = self.session.get(self._url(f"/api/runs/{run_id}/artifacts/{artifact_kind}"), timeout=self.timeout_s)
        resp.raise_for_status()
        out_path.write_bytes(resp.content)
        return out_path

    def get_training_job(self, job_id: str) -> dict[str, Any]:
        return self._json("GET", f"/api/train/jobs/{job_id}")

    def list_training_jobs(self, *, status: str | None = None, limit: int = 50) -> list[dict[str, Any]]:
        params: dict[str, Any] = {"limit": limit}
        if status:
            params["status"] = status
        payload = self._json("GET", "/api/train/jobs", params=params)
        return payload.get("items", [])

    def update_training_job(self, job_id: str, payload: dict[str, Any]) -> dict[str, Any]:
        return self._json("POST", f"/api/train/jobs/{job_id}/update", json=payload)

    def create_model(self, payload: dict[str, Any]) -> dict[str, Any]:
        return self._json("POST", "/api/models", json=payload)

    def upload_model_artifact(self, model_version: str, artifact_kind: str, file_path: Path) -> dict[str, Any]:
        with file_path.open("rb") as f:
            files = {"file": (file_path.name, f)}
            resp = self.session.post(
                self._url(f"/api/models/{model_version}/artifacts/{artifact_kind}"),
                files=files,
                timeout=self.timeout_s,
            )
        resp.raise_for_status()
        return resp.json()

    def set_active_model(self, model_version: str) -> dict[str, Any]:
        return self._json("POST", "/api/models/active", json={"model_version": model_version})
