from __future__ import annotations

from pathlib import Path


class LocalArtifactStorage:
    def __init__(self, root: Path) -> None:
        self.root = root
        self.root.mkdir(parents=True, exist_ok=True)

    def run_dir(self, run_id: str) -> Path:
        path = self.root / "runs" / run_id
        path.mkdir(parents=True, exist_ok=True)
        return path

    def model_dir(self, model_version: str) -> Path:
        path = self.root / "models" / model_version
        path.mkdir(parents=True, exist_ok=True)
        return path

    def save_run_artifact(self, run_id: str, filename: str, content: bytes) -> str:
        path = self.run_dir(run_id) / filename
        path.write_bytes(content)
        return str(path.as_posix())

    def save_model_artifact(self, model_version: str, filename: str, content: bytes) -> str:
        path = self.model_dir(model_version) / filename
        path.write_bytes(content)
        return str(path.as_posix())
