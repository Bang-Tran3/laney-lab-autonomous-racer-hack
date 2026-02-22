from __future__ import annotations

import sqlite3
from pathlib import Path


def connect(db_path: Path) -> sqlite3.Connection:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_schema(conn: sqlite3.Connection) -> None:
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS runs (
            run_id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            track_id TEXT NOT NULL,
            mode TEXT NOT NULL CHECK(mode IN ('manual','autonomous')),
            model_version TEXT,
            sim_build TEXT NOT NULL DEFAULT '',
            client_build TEXT NOT NULL DEFAULT '',
            notes TEXT,
            status TEXT NOT NULL DEFAULT 'uploading' CHECK(status IN ('uploading','complete','failed')),
            started_at TEXT NOT NULL,
            ended_at TEXT,
            duration_s REAL,
            frame_count INTEGER NOT NULL DEFAULT 0,
            lap_count INTEGER NOT NULL DEFAULT 0,
            off_track_count INTEGER NOT NULL DEFAULT 0,
            best_lap_ms REAL,
            local_run_id TEXT,
            frames_uri TEXT,
            controls_uri TEXT,
            run_json_uri TEXT,
            created_at TEXT NOT NULL
        );
        CREATE INDEX IF NOT EXISTS idx_runs_created_at ON runs(created_at DESC);
        CREATE INDEX IF NOT EXISTS idx_runs_track_id ON runs(track_id);
        CREATE INDEX IF NOT EXISTS idx_runs_mode ON runs(mode);
        CREATE INDEX IF NOT EXISTS idx_runs_user_id ON runs(user_id);
        CREATE INDEX IF NOT EXISTS idx_runs_local_run_id ON runs(local_run_id);

        CREATE TABLE IF NOT EXISTS models (
            model_id TEXT PRIMARY KEY,
            model_version TEXT NOT NULL UNIQUE,
            status TEXT NOT NULL CHECK(status IN ('training','ready','failed','archived')),
            created_at TEXT NOT NULL,
            architecture_json TEXT NOT NULL DEFAULT '{}',
            training_json TEXT NOT NULL DEFAULT '{}',
            pytorch_uri TEXT,
            onnx_uri TEXT,
            openvino_uri TEXT
        );

        CREATE TABLE IF NOT EXISTS training_jobs (
            job_id TEXT PRIMARY KEY,
            status TEXT NOT NULL CHECK(status IN ('queued','running','succeeded','failed')),
            created_at TEXT NOT NULL,
            config_json TEXT NOT NULL,
            progress_json TEXT NOT NULL DEFAULT '{}',
            output_model_version TEXT,
            logs_uri TEXT
        );

        CREATE TABLE IF NOT EXISTS app_state (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL
        );
        """
    )
    conn.commit()
