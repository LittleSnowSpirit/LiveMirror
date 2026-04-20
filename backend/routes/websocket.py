"""
WebSocket 实时进度推送
"""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import Dict, Set
import asyncio
from loguru import logger

router = APIRouter()

# 连接管理
class ConnectionManager:
    def __init__(self):
        self.active_connections: Set[WebSocket] = set()
        self.task_subscribers: Dict[str, Set[WebSocket]] = {}
    
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.add(websocket)
        logger.info(f"WebSocket 连接建立，当前连接数：{len(self.active_connections)}")
    
    def disconnect(self, websocket: WebSocket):
        self.active_connections.discard(websocket)
        # 清理任务订阅
        for task_id, subscribers in self.task_subscribers.items():
            subscribers.discard(websocket)
        logger.info(f"WebSocket 连接断开，当前连接数：{len(self.active_connections)}")
    
    def subscribe_task(self, task_id: str, websocket: WebSocket):
        if task_id not in self.task_subscribers:
            self.task_subscribers[task_id] = set()
        self.task_subscribers[task_id].add(websocket)
        logger.info(f"订阅任务：{task_id}，订阅者：{len(self.task_subscribers[task_id])}")
    
    def unsubscribe_task(self, task_id: str, websocket: WebSocket):
        if task_id in self.task_subscribers:
            self.task_subscribers[task_id].discard(websocket)
    
    async def broadcast_task_update(self, task_id: str, message: dict):
        """广播任务更新"""
        if task_id not in self.task_subscribers:
            return
        
        disconnected = set()
        for websocket in self.task_subscribers[task_id]:
            try:
                await websocket.send_json(message)
            except Exception as e:
                logger.error(f"发送消息失败：{e}")
                disconnected.add(websocket)
        
        # 清理断开的连接
        for websocket in disconnected:
            self.unsubscribe_task(task_id, websocket)
            self.disconnect(websocket)


# 全局连接管理器
manager = ConnectionManager()


@router.websocket("/ws/task/{task_id}")
async def task_websocket(websocket: WebSocket, task_id: str):
    """任务进度 WebSocket"""
    await manager.connect(websocket)
    manager.subscribe_task(task_id, websocket)
    
    try:
        while True:
            # 接收客户端消息（心跳等）
            data = await websocket.receive_text()
            
            # 可以处理客户端请求
            if data == "ping":
                await websocket.send_text("pong")
    
    except WebSocketDisconnect:
        logger.info(f"客户端断开：{task_id}")
    except Exception as e:
        logger.error(f"WebSocket 异常：{e}")
    finally:
        manager.unsubscribe_task(task_id, websocket)
        manager.disconnect(websocket)


async def notify_task_update(task_id: str, status: str, progress: int, **extra):
    """通知任务更新"""
    message = {
        "task_id": task_id,
        "status": status,
        "progress": progress,
        **extra
    }
    await manager.broadcast_task_update(task_id, message)
