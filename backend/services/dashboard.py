"""
LiveMirror Dashboard Service
实时直播数据大屏服务 - 提供 WebSocket 实时数据推送
"""

import asyncio
import json
import random
from datetime import datetime
from typing import Set, Dict, Any
from fastapi import WebSocket


class DashboardService:
    """大屏数据服务 - 管理 WebSocket 连接和实时数据推送"""
    
    def __init__(self):
        self.active_connections: Set[WebSocket] = set()
        self.current_data: Dict[str, Any] = {
            "gmv": 0,
            "viewers": 0,
            "likes": 0,
            "comments": 0,
            "shares": 0,
            "orders": 0,
            "conversion_rate": 0.0,
            "avg_watch_time": 0.0,
            "peak_viewers": 0,
            "start_time": datetime.now().isoformat()
        }
        self._running = False
        self._update_task = None
    
    async def connect(self, websocket: WebSocket):
        """接受 WebSocket 连接"""
        await websocket.accept()
        self.active_connections.add(websocket)
        print(f"[Dashboard] New connection. Total: {len(self.active_connections)}")
        # 发送当前数据
        await self.send_data(websocket, self.current_data)
    
    def disconnect(self, websocket: WebSocket):
        """断开 WebSocket 连接"""
        self.active_connections.discard(websocket)
        print(f"[Dashboard] Connection closed. Total: {len(self.active_connections)}")
    
    async def send_data(self, websocket: WebSocket, data: Dict[str, Any]):
        """向特定连接发送数据"""
        try:
            await websocket.send_json(data)
        except Exception as e:
            print(f"[Dashboard] Send error: {e}")
            self.disconnect(websocket)
    
    async def broadcast(self, data: Dict[str, Any]):
        """向所有连接广播数据"""
        if not self.active_connections:
            return
        
        disconnected = set()
        for connection in self.active_connections:
            try:
                await connection.send_json(data)
            except Exception as e:
                print(f"[Dashboard] Broadcast error: {e}")
                disconnected.add(connection)
        
        # 清理断开的连接
        for conn in disconnected:
            self.disconnect(conn)
    
    def update_data(self, **kwargs):
        """更新当前数据"""
        for key, value in kwargs.items():
            if key in self.current_data:
                self.current_data[key] = value
        
        # 更新峰值观看人数
        if self.current_data["viewers"] > self.current_data["peak_viewers"]:
            self.current_data["peak_viewers"] = self.current_data["viewers"]
        
        # 重新计算转化率
        if self.current_data["viewers"] > 0:
            self.current_data["conversion_rate"] = round(
                (self.current_data["orders"] / self.current_data["viewers"]) * 100, 2
            )
    
    async def start_auto_update(self, interval: float = 3.0):
        """启动自动数据更新（模拟实时数据）"""
        self._running = True
        
        while self._running:
            # 模拟数据变化
            self._simulate_live_data()
            
            # 广播更新
            await self.broadcast({
                "type": "update",
                "timestamp": datetime.now().isoformat(),
                "data": self.current_data
            })
            
            await asyncio.sleep(interval)
    
    def _simulate_live_data(self):
        """模拟直播数据变化"""
        # GMV 增长
        gmv_increase = random.uniform(100, 5000)
        self.current_data["gmv"] = round(self.current_data["gmv"] + gmv_increase, 2)
        
        # 观看人数波动
        viewer_change = random.randint(-50, 100)
        self.current_data["viewers"] = max(0, self.current_data["viewers"] + viewer_change)
        if self.current_data["viewers"] == 0:
            self.current_data["viewers"] = random.randint(100, 500)
        
        # 互动数据
        self.current_data["likes"] += random.randint(10, 100)
        self.current_data["comments"] += random.randint(1, 20)
        self.current_data["shares"] += random.randint(0, 10)
        self.current_data["orders"] += random.randint(0, 5)
        
        # 计算转化率
        if self.current_data["viewers"] > 0:
            self.current_data["conversion_rate"] = round(
                (self.current_data["orders"] / self.current_data["viewers"]) * 100, 2
            )
        
        # 平均观看时长（秒）
        self.current_data["avg_watch_time"] = round(random.uniform(60, 300), 1)
    
    def stop_auto_update(self):
        """停止自动更新"""
        self._running = False
    
    def get_current_data(self) -> Dict[str, Any]:
        """获取当前数据"""
        return self.current_data.copy()
    
    def reset_data(self):
        """重置数据"""
        self.current_data = {
            "gmv": 0,
            "viewers": 0,
            "likes": 0,
            "comments": 0,
            "shares": 0,
            "orders": 0,
            "conversion_rate": 0.0,
            "avg_watch_time": 0.0,
            "peak_viewers": 0,
            "start_time": datetime.now().isoformat()
        }


# 全局服务实例
dashboard_service = DashboardService()
