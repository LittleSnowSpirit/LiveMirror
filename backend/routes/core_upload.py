"""Core media upload API."""

from __future__ import annotations

import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from config import settings
from database import get_db
from routes.core_auth import get_current_user
from services.core_analysis import build_core_analysis, build_report_data
from services.database import (
    create_task,
    get_task,
    update_task_analysis,
    update_task_duration,
    update_task_status,
    update_task_transcription,
)
from services.task_queue import get_task_queue
from services.transcription import get_transcription_service

router = APIRouter(prefix="/api/upload", tags=["core-upload"])
_CHUNK_SIZE = 1024 * 1024


@router.post("")
async def upload_media(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    _current_user=Depends(get_current_user),
):
    if not file.filename:
        raise HTTPException(status_code=400, detail="Missing filename.")

    extension = Path(file.filename).suffix.lower().lstrip(".")
    if extension not in settings.allowed_extension_set:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type. Allowed: {', '.join(sorted(settings.allowed_extension_set))}",
        )

    task_id = str(uuid.uuid4())
    safe_name = Path(file.filename).name
    save_path = Path(settings.upload_dir) / f"{task_id}_{safe_name}"

    file_size = 0
    try:
        with save_path.open("wb") as buffer:
            while True:
                chunk = file.file.read(_CHUNK_SIZE)
                if not chunk:
                    break

                file_size += len(chunk)
                if file_size > settings.max_file_size:
                    raise HTTPException(status_code=400, detail="File is larger than MAX_FILE_SIZE.")

                buffer.write(chunk)
    except HTTPException:
        save_path.unlink(missing_ok=True)
        raise
    except Exception as exc:
        save_path.unlink(missing_ok=True)
        raise HTTPException(status_code=500, detail="Failed to save uploaded file.") from exc
    finally:
        file.file.close()

    if file_size == 0:
        save_path.unlink(missing_ok=True)
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")

    create_task(db, task_id, safe_name, str(save_path), file_size)

    get_task_queue().submit(task_id, _process_upload_task, task_id)

    return {
        "task_id": task_id,
        "filename": safe_name,
        "file_size": file_size,
        "status": "pending",
        "message": "Upload accepted. Processing has started.",
    }


def _process_upload_task(task_id: str) -> None:
    db = next(get_db())
    try:
        task = get_task(db, task_id)
        if task is None:
            return

        update_task_status(db, task, "transcribing", 20)
        service = get_transcription_service()
        result = service.transcribe(task.file_path)

        task = get_task(db, task_id)
        if task is None:
            return

        update_task_duration(db, task, result.duration or 0.0)
        update_task_transcription(db, task, result.text, result.segments)
        task.language = result.language

        # Data quality scoring
        quality_score = 1.0
        text = result.text or ""
        if not text.strip():
            quality_score = 0.0
        elif len(text.strip()) < 10:
            quality_score = 0.3
        task.data_quality_score = quality_score
        db.commit()

        update_task_status(db, task, "analyzing", 75)
        analysis = build_core_analysis(result.text, result.segments, result.duration)
        report = build_report_data(
            task_id=task.task_id,
            filename=task.filename,
            transcription=result.text,
            segments=result.segments,
            duration=result.duration,
            language=result.language,
            analysis=analysis,
        )
        update_task_analysis(db, task, analysis, report)
    except Exception as exc:
        task = get_task(db, task_id)
        if task is not None:
            update_task_status(db, task, "failed", 0, str(exc))
    finally:
        db.close()
