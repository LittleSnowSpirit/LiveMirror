"""通知 WebSocket 端点。"""

from __future__ import annotations

import logging

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from config import settings
from database import SessionLocal
from models import User
from routes.core_auth import ALGORITHM
from services.notification_service import emitter, get_unread_count, mark_all_read, mark_notifications_read
from services.websocket_manager import manager

logger = logging.getLogger(__name__)

router = APIRouter(tags=["ws-notifications"])


async def _authenticate_ws(websocket: WebSocket) -> tuple[User, Session] | None:
    """从 query param 中的 token 认证 WebSocket。失败返回 None。"""
    token = websocket.query_params.get("token")
    if not token:
        await websocket.close(code=4001, reason="Missing token")
        return None
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if not username or payload.get("type") != "access":
            await websocket.close(code=4001, reason="Invalid token")
            return None
    except JWTError:
        await websocket.close(code=4001, reason="Invalid token")
        return None

    db = SessionLocal()
    try:
        user = db.query(User).filter(User.username == username).first()
        if not user or not user.is_active:
            db.close()
            await websocket.close(code=4001, reason="User not found")
            return None
        return user, db
    except Exception:
        db.close()
        await websocket.close(code=4001, reason="Auth error")
        return None


@router.websocket("/ws/notifications")
async def ws_notifications(websocket: WebSocket):
    auth_result = await _authenticate_ws(websocket)
    if not auth_result:
        return

    user, db = auth_result
    user_id = user.id

    try:
        await manager.connect(user_id, websocket)

        # 发送初始化消息
        unread = get_unread_count(db, user_id)
        await websocket.send_json({"type": "init", "unread_count": unread})

        # 注册 emitter 回调
        async def on_notification(payload: dict) -> None:
            try:
                await websocket.send_json(payload)
            except Exception:
                pass

        emitter.subscribe(user_id, on_notification)

        try:
            while True:
                data = await websocket.receive_json()
                action = data.get("type") or data.get("action")

                if action == "ping":
                    await websocket.send_json({"type": "pong"})
                elif action == "mark_read":
                    ids = data.get("ids", [])
                    if ids:
                        mark_notifications_read(db, ids, user_id)
                    unread = get_unread_count(db, user_id)
                    await websocket.send_json({"type": "unread_count", "count": unread})
                elif action == "mark_all_read":
                    mark_all_read(db, user_id)
                    await websocket.send_json({"type": "unread_count", "count": 0})
        except WebSocketDisconnect:
            pass
    finally:
        emitter.unsubscribe(user_id, on_notification)
        manager.disconnect(user_id, websocket)
        db.close()
