from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Settings:
    app_name: str = "Laney DeepRacer API"
    database_path: Path = Path("services/api/data/app.db")
    storage_root: Path = Path("services/api/storage")
    cors_origins: tuple[str, ...] = ("http://localhost:3000",)

    @staticmethod
    def from_env() -> "Settings":
      db_path = Path(os.getenv("DEEPRACER_API_DB_PATH", "services/api/data/app.db"))
      storage_root = Path(os.getenv("DEEPRACER_API_STORAGE_ROOT", "services/api/storage"))
      cors_raw = os.getenv("DEEPRACER_API_CORS_ORIGINS", "http://localhost:3000")
      cors = tuple(origin.strip() for origin in cors_raw.split(",") if origin.strip())
      return Settings(database_path=db_path, storage_root=storage_root, cors_origins=cors or ("http://localhost:3000",))

