"""弹幕批量存储服务 — 文件解析入库、批次管理、弹幕查询。"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy.orm import Session

from models import Danmu, DanmuBatch
from services.danmu_parser import parse_danmu_file


def batch_insert_danmus(
    db: Session,
    user_id: int,
    file_path: str,
    file_format: str,
    filename: str,
) -> DanmuBatch:
    """解析弹幕文件并批量入库。

    创建 DanmuBatch 记录，逐条插入 Danmu（跳过同批次重复），更新统计字段。

    Returns:
        创建完成的 DanmuBatch 对象
    """
    batch = DanmuBatch(
        user_id=user_id,
        batch_id=uuid.uuid4().hex[:16],
        source_type="upload",
        filename=filename,
        file_format=file_format,
        status="processing",
    )
    db.add(batch)
    db.flush()

    try:
        items = parse_danmu_file(file_path, file_format)
    except Exception as exc:
        batch.status = "failed"
        batch.error_message = str(exc)
        db.flush()
        return batch

    total = len(items)
    success = 0
    failed = 0
    seen: set[tuple[float, str]] = set()
    min_ts: Optional[float] = None
    max_ts: Optional[float] = None

    for item in items:
        ts = item["timestamp"]
        content = item["content"]

        # 同批次去重
        dedup_key = (ts, content)
        if dedup_key in seen:
            continue
        seen.add(dedup_key)

        danmu = Danmu(
            user_id=user_id,
            batch_id=batch.batch_id,
            content=content,
            timestamp=ts,
            username=item.get("username", "anonymous"),
        )
        db.add(danmu)
        success += 1

        if min_ts is None or ts < min_ts:
            min_ts = ts
        if max_ts is None or ts > max_ts:
            max_ts = ts

    batch.total_count = total
    batch.success_count = success
    batch.failed_count = failed
    batch.start_timestamp = min_ts
    batch.end_timestamp = max_ts
    batch.status = "completed"
    batch.completed_at = datetime.now(timezone.utc)
    db.flush()

    return batch


def get_danmu_batches(db: Session, user_id: int) -> list[DanmuBatch]:
    """获取用户的弹幕批次列表，按创建时间倒序。"""
    return (
        db.query(DanmuBatch)
        .filter(DanmuBatch.user_id == user_id)
        .order_by(DanmuBatch.created_at.desc())
        .all()
    )


def get_danmu_batch_detail(db: Session, batch_id: str) -> Optional[DanmuBatch]:
    """获取单个批次详情。"""
    return db.query(DanmuBatch).filter(DanmuBatch.batch_id == batch_id).first()


def get_danmu_by_batch(
    db: Session, batch_id: str, limit: int = 1000
) -> list[Danmu]:
    """获取指定批次的弹幕列表。"""
    return (
        db.query(Danmu)
        .filter(Danmu.batch_id == batch_id)
        .order_by(Danmu.timestamp)
        .limit(limit)
        .all()
    )
