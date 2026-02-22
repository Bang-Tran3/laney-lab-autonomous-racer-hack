from __future__ import annotations

import json
import sqlite3
import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Request

from app.schemas import (
    ListTrainingJobsResponse,
    StartTrainingJobRequest,
    StartTrainingJobResponse,
    TrainingJobRecord,
    UpdateTrainingJobRequest,
)


router = APIRouter(prefix="/api/train/jobs", tags=["training"])


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def get_conn(request: Request) -> sqlite3.Connection:
    return request.app.state.db


def row_to_job(row: sqlite3.Row) -> TrainingJobRecord:
    return TrainingJobRecord(
        job_id=row["job_id"],
        status=row["status"],
        created_at=row["created_at"],
        config=json.loads(row["config_json"] or "{}"),
        progress=json.loads(row["progress_json"] or "{}"),
        outputs={"model_version": row["output_model_version"]},
        logs_uri=row["logs_uri"],
    )


@router.post("", response_model=StartTrainingJobResponse)
def start_training_job(payload: StartTrainingJobRequest, conn: sqlite3.Connection = Depends(get_conn)) -> StartTrainingJobResponse:
    job_id = str(uuid.uuid4())
    now = utc_now_iso()
    config = {
        "dataset": payload.dataset,
        "hyperparams": payload.hyperparams,
        "export": payload.export,
    }
    conn.execute(
        """
        INSERT INTO training_jobs(job_id, status, created_at, config_json, progress_json)
        VALUES (?, 'queued', ?, ?, ?)
        """,
        (job_id, now, json.dumps(config), json.dumps({"epoch": 0})),
    )
    conn.commit()
    return StartTrainingJobResponse(job_id=job_id, status="queued")


@router.get("", response_model=ListTrainingJobsResponse)
def list_training_jobs(
    conn: sqlite3.Connection = Depends(get_conn),
    status: str | None = None,
    limit: int = 50,
) -> ListTrainingJobsResponse:
    params: list[object] = []
    where = ""
    if status:
        where = "WHERE status = ?"
        params.append(status)
    params.append(limit)
    rows = conn.execute(
        f"SELECT * FROM training_jobs {where} ORDER BY created_at DESC LIMIT ?",
        params,
    ).fetchall()
    return ListTrainingJobsResponse(items=[row_to_job(r) for r in rows], next_cursor=None)


@router.get("/{job_id}", response_model=TrainingJobRecord)
def get_training_job(job_id: str, conn: sqlite3.Connection = Depends(get_conn)) -> TrainingJobRecord:
    row = conn.execute("SELECT * FROM training_jobs WHERE job_id = ?", (job_id,)).fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Training job not found")
    return row_to_job(row)


@router.post("/{job_id}/update", response_model=TrainingJobRecord)
def update_training_job(job_id: str, payload: UpdateTrainingJobRequest, conn: sqlite3.Connection = Depends(get_conn)) -> TrainingJobRecord:
    row = conn.execute("SELECT * FROM training_jobs WHERE job_id = ?", (job_id,)).fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Training job not found")

    status = payload.status or row["status"]
    progress = payload.progress if payload.progress is not None else json.loads(row["progress_json"] or "{}")
    output_model_version = payload.output_model_version if payload.output_model_version is not None else row["output_model_version"]
    logs_uri = payload.logs_uri if payload.logs_uri is not None else row["logs_uri"]

    conn.execute(
        """
        UPDATE training_jobs
        SET status = ?, progress_json = ?, output_model_version = ?, logs_uri = ?
        WHERE job_id = ?
        """,
        (status, json.dumps(progress), output_model_version, logs_uri, job_id),
    )
    conn.commit()
    updated = conn.execute("SELECT * FROM training_jobs WHERE job_id = ?", (job_id,)).fetchone()
    assert updated is not None
    return row_to_job(updated)
