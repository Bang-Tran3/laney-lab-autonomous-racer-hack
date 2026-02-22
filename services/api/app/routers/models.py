from __future__ import annotations

import json
import os
import sqlite3
import uuid
from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, Depends, File, HTTPException, Query, Request, UploadFile
from fastapi.responses import FileResponse

from app.schemas import ActiveModelResponse, CreateModelRequest, ListModelsResponse, ModelRecord, SetActiveModelRequest


router = APIRouter(prefix="/api/models", tags=["models"])


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def get_conn(request: Request) -> sqlite3.Connection:
    return request.app.state.db


def get_storage(request: Request):
    return request.app.state.storage


def row_to_model(row: sqlite3.Row) -> ModelRecord:
    return ModelRecord(
        model_id=row["model_id"],
        model_version=row["model_version"],
        status=row["status"],
        created_at=row["created_at"],
        architecture=json.loads(row["architecture_json"] or "{}"),
        training=json.loads(row["training_json"] or "{}"),
        artifacts={
            "pytorch_uri": row["pytorch_uri"],
            "onnx_uri": row["onnx_uri"],
            "openvino_uri": row["openvino_uri"],
        },
    )


@router.get("", response_model=ListModelsResponse)
def list_models(
    request: Request,
    conn: sqlite3.Connection = Depends(get_conn),
    status: Optional[str] = None,
    limit: int = Query(default=50, ge=1, le=200),
    cursor: Optional[str] = None,
) -> ListModelsResponse:
    clauses: list[str] = []
    params: list[object] = []
    if status:
        clauses.append("status = ?")
        params.append(status)
    if cursor:
        clauses.append("created_at < ?")
        params.append(cursor)

    where = f"WHERE {' AND '.join(clauses)}" if clauses else ""
    query = f"SELECT * FROM models {where} ORDER BY created_at DESC LIMIT ?"
    params.append(limit + 1)
    rows = conn.execute(query, params).fetchall()

    next_cursor = None
    if len(rows) > limit:
        next_cursor = rows[limit - 1]["created_at"]
        rows = rows[:limit]

    return ListModelsResponse(items=[row_to_model(r) for r in rows], next_cursor=next_cursor)


@router.post("", response_model=ModelRecord)
def create_model(payload: CreateModelRequest, conn: sqlite3.Connection = Depends(get_conn)) -> ModelRecord:
    existing = conn.execute("SELECT * FROM models WHERE model_version = ?", (payload.model_version,)).fetchone()
    if existing:
        raise HTTPException(status_code=409, detail="Model version already exists")

    model_id = str(uuid.uuid4())
    created_at = utc_now_iso()
    conn.execute(
        """
        INSERT INTO models(
          model_id, model_version, status, created_at, architecture_json, training_json, pytorch_uri, onnx_uri, openvino_uri
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            model_id,
            payload.model_version,
            payload.status,
            created_at,
            json.dumps(payload.architecture or {}),
            json.dumps(payload.training or {}),
            (payload.artifacts or {}).get("pytorch_uri"),
            (payload.artifacts or {}).get("onnx_uri"),
            (payload.artifacts or {}).get("openvino_uri"),
        ),
    )
    conn.commit()
    row = conn.execute("SELECT * FROM models WHERE model_id = ?", (model_id,)).fetchone()
    assert row is not None
    return row_to_model(row)


@router.get("/active", response_model=ActiveModelResponse)
def get_active_model(conn: sqlite3.Connection = Depends(get_conn)) -> ActiveModelResponse:
    row = conn.execute("SELECT value FROM app_state WHERE key = 'active_model_version'").fetchone()
    return ActiveModelResponse(active_model_version=row["value"] if row else None)


@router.post("/active", response_model=ActiveModelResponse)
def set_active_model(payload: SetActiveModelRequest, conn: sqlite3.Connection = Depends(get_conn)) -> ActiveModelResponse:
    model = conn.execute("SELECT model_version FROM models WHERE model_version = ?", (payload.model_version,)).fetchone()
    if not model:
        raise HTTPException(status_code=404, detail="Model version not found")
    conn.execute(
        "INSERT INTO app_state(key, value) VALUES('active_model_version', ?) "
        "ON CONFLICT(key) DO UPDATE SET value=excluded.value",
        (payload.model_version,),
    )
    conn.commit()
    return ActiveModelResponse(active_model_version=payload.model_version)


@router.get("/{model_version}", response_model=ModelRecord)
def get_model(model_version: str, conn: sqlite3.Connection = Depends(get_conn)) -> ModelRecord:
    row = conn.execute("SELECT * FROM models WHERE model_version = ?", (model_version,)).fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Model not found")
    return row_to_model(row)


@router.post("/{model_version}/artifacts/{artifact_kind}", response_model=ModelRecord)
async def upload_model_artifact(
    model_version: str,
    artifact_kind: str,
    file: UploadFile = File(...),
    conn: sqlite3.Connection = Depends(get_conn),
    storage=Depends(get_storage),
) -> ModelRecord:
    row = conn.execute("SELECT * FROM models WHERE model_version = ?", (model_version,)).fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Model not found")

    file_name_by_kind = {
        "pytorch": "model.pt",
        "onnx": "model.onnx",
        "openvino": "openvino.bin",
        "config": "config.json",
    }
    column_by_kind = {
        "pytorch": "pytorch_uri",
        "onnx": "onnx_uri",
        "openvino": "openvino_uri",
    }
    filename = file_name_by_kind.get(artifact_kind)
    if not filename:
        raise HTTPException(status_code=404, detail="Artifact kind not supported")

    contents = await file.read()
    uri = storage.save_model_artifact(model_version, filename, contents)

    if artifact_kind in column_by_kind:
        conn.execute(
            f"UPDATE models SET {column_by_kind[artifact_kind]} = ? WHERE model_version = ?",
            (uri, model_version),
        )
    elif artifact_kind == "config":
        current_training = json.loads(row["training_json"] or "{}")
        current_training.setdefault("artifacts", {})["config_uri"] = uri
        conn.execute("UPDATE models SET training_json = ? WHERE model_version = ?", (json.dumps(current_training), model_version))
    conn.commit()

    updated = conn.execute("SELECT * FROM models WHERE model_version = ?", (model_version,)).fetchone()
    assert updated is not None
    return row_to_model(updated)


@router.get("/{model_version}/artifacts/{artifact_kind}")
def download_model_artifact(
    model_version: str,
    artifact_kind: str,
    conn: sqlite3.Connection = Depends(get_conn),
) -> FileResponse:
    row = conn.execute("SELECT * FROM models WHERE model_version = ?", (model_version,)).fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Model not found")

    artifact_path = {
        "pytorch": row["pytorch_uri"],
        "onnx": row["onnx_uri"],
        "openvino": row["openvino_uri"],
    }.get(artifact_kind)
    if not artifact_path:
        raise HTTPException(status_code=404, detail="Artifact not found")
    if not os.path.exists(artifact_path):
        raise HTTPException(status_code=404, detail="Artifact file missing on server")

    media_type = {
        "pytorch": "application/octet-stream",
        "onnx": "application/octet-stream",
        "openvino": "application/octet-stream",
    }[artifact_kind]
    return FileResponse(path=artifact_path, media_type=media_type, filename=os.path.basename(artifact_path))
