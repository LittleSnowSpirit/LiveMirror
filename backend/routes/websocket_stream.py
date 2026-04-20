"""
LiveMirror WebSocket 流处理路由
支持实时音频流传输、流式转写、实时分析推送
"""

import asyncio
import json
import time
import uuid
from typing import Dict, Optional
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query
from pathlib import Path
import sys

# 添加父目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from services.realtime_analysis import (
    get_analysis_service,
    AnalysisResult,
    RealtimeAnalysisService
)
from services.whisper import get_service as get_whisper_service


router = APIRouter()


class ConnectionManager:
    """
    WebSocket 连接管理器
    管理所有活跃的直播流连接
    """
    
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.session_metadata: Dict[str, dict] = {}
    
    async def connect(self, websocket: WebSocket, session_id: str) -> bool:
        """
        接受 WebSocket 连接
        
        Returns:
            bool: 连接是否成功
        """
        try:
            await websocket.accept()
            self.active_connections[session_id] = websocket
            self.session_metadata[session_id] = {
                'connected_at': time.time(),
                'last_activity': time.time(),
                'message_count': 0
            }
            print(f"[WS] 新连接：{session_id}")
            return True
        except Exception as e:
            print(f"[WS ERROR] 连接失败：{e}")
            return False
    
    def disconnect(self, session_id: str):
        """断开连接"""
        if session_id in self.active_connections:
            del self.active_connections[session_id]
        if session_id in self.session_metadata:
            del self.session_metadata[session_id]
        print(f"[WS] 连接断开：{session_id}")
    
    async def send_personal_message(self, message: dict, session_id: str):
        """发送个人消息"""
        if session_id in self.active_connections:
            try:
                websocket = self.active_connections[session_id]
                await websocket.send_json(message)
                if session_id in self.session_metadata:
                    self.session_metadata[session_id]['last_activity'] = time.time()
                    self.session_metadata[session_id]['message_count'] += 1
            except Exception as e:
                print(f"[WS ERROR] 发送失败 {session_id}: {e}")
                await self.disconnect(session_id)
    
    async def broadcast(self, message: dict):
        """广播消息到所有连接"""
        disconnected = []
        for session_id, websocket in self.active_connections.items():
            try:
                await websocket.send_json(message)
            except Exception as e:
                print(f"[WS ERROR] 广播失败 {session_id}: {e}")
                disconnected.append(session_id)
        
        # 清理断开的连接
        for session_id in disconnected:
            await self.disconnect(session_id)
    
    def get_connection_count(self) -> int:
        """获取活跃连接数"""
        return len(self.active_connections)
    
    def get_session_info(self, session_id: str) -> Optional[dict]:
        """获取会话信息"""
        if session_id in self.session_metadata:
            meta = self.session_metadata[session_id]
            return {
                'session_id': session_id,
                'connected': session_id in self.active_connections,
                'connected_at': meta['connected_at'],
                'last_activity': meta['last_activity'],
                'message_count': meta['message_count'],
                'duration_seconds': round(time.time() - meta['connected_at'], 2)
            }
        return None


# 全局连接管理器
manager = ConnectionManager()


class AudioStreamProcessor:
    """
    音频流处理器
    处理流式音频数据、转写、分析
    """
    
    def __init__(self, session_id: str, manager: ConnectionManager):
        self.session_id = session_id
        self.manager = manager
        self.analysis_service = get_analysis_service()
        self.whisper_service = get_whisper_service()
        
        # 音频缓冲区
        self.audio_buffer = bytearray()
        self.buffer_duration_ms = 3000  # 3 秒缓冲区
        
        # 状态
        self.is_processing = False
        self.total_audio_ms = 0
        self.segment_count = 0
        
        # 性能统计
        self.latencies = []
    
    async def process_audio_chunk(self, audio_data: bytes, sample_rate: int = 16000):
        """
        处理音频数据块
        
        Args:
            audio_data: PCM 音频数据
            sample_rate: 采样率
        """
        chunk_duration_ms = (len(audio_data) / (sample_rate * 2)) * 1000  # 16-bit PCM
        self.audio_buffer.extend(audio_data)
        self.total_audio_ms += chunk_duration_ms
        
        # 检查是否达到处理阈值
        if len(self.audio_buffer) >= self._get_buffer_size(sample_rate):
            await self._process_buffer(sample_rate)
    
    def _get_buffer_size(self, sample_rate: int) -> int:
        """计算缓冲区大小（字节）"""
        # 16-bit PCM, mono
        return int(sample_rate * 2 * (self.buffer_duration_ms / 1000))
    
    async def _process_buffer(self, sample_rate: int):
        """处理缓冲区音频"""
        if self.is_processing:
            return
        
        self.is_processing = True
        start_time = time.time()
        
        try:
            # 保存临时音频文件
            temp_path = Path(f"uploads/temp_{self.session_id}_{self.segment_count}.wav")
            temp_path.parent.mkdir(exist_ok=True)
            
            # 写入 WAV 文件（简化版，实际需要完整的 WAV 头）
            # 这里为了演示，假设是原始 PCM 数据
            with open(temp_path, 'wb') as f:
                f.write(self.audio_buffer)
            
            # 转写
            transcribe_start = time.time()
            result = self.whisper_service.transcribe(
                str(temp_path),
                model_size="tiny",
                language="zh"
            )
            transcribe_time = (time.time() - transcribe_start) * 1000
            
            # 分析
            analyze_start = time.time()
            analysis = self.analysis_service.analyze_segment(
                self.session_id,
                result.text,
                audio_duration_ms=self.buffer_duration_ms
            )
            analyze_time = (time.time() - analyze_start) * 1000
            
            total_latency = (time.time() - start_time) * 1000
            self.latencies.append(total_latency)
            
            # 构建响应
            response = {
                'type': 'transcription_result',
                'session_id': self.session_id,
                'segment_index': self.segment_count,
                'text': result.text,
                'analysis': {
                    'sentiment': analysis.sentiment,
                    'sentiment_score': analysis.sentiment_score,
                    'keywords': analysis.keywords,
                    'suggestions': analysis.suggestions,
                    'risks': analysis.risks,
                    'emotions': analysis.emotion_data
                },
                'performance': {
                    'transcribe_time_ms': round(transcribe_time, 2),
                    'analyze_time_ms': round(analyze_time, 2),
                    'total_latency_ms': round(total_latency, 2),
                    'avg_latency_ms': round(sum(self.latencies) / len(self.latencies), 2) if self.latencies else 0
                },
                'timestamp': time.time()
            }
            
            # 发送结果
            await self.manager.send_personal_message(response, self.session_id)
            
            # 清理
            self.audio_buffer.clear()
            self.segment_count += 1
            
            # 删除临时文件
            try:
                temp_path.unlink()
            except:
                pass
            
            print(f"[STREAM] 片段 {self.segment_count} 处理完成，延迟 {total_latency:.2f}ms")
            
        except Exception as e:
            print(f"[STREAM ERROR] 处理失败：{e}")
            error_response = {
                'type': 'error',
                'session_id': self.session_id,
                'error': str(e),
                'timestamp': time.time()
            }
            await self.manager.send_personal_message(error_response, self.session_id)
        
        finally:
            self.is_processing = False
    
    async def flush(self):
        """刷新剩余缓冲区"""
        if self.audio_buffer:
            await self._process_buffer(16000)
    
    def get_stats(self) -> dict:
        """获取处理统计"""
        return {
            'session_id': self.session_id,
            'total_audio_ms': round(self.total_audio_ms, 2),
            'segment_count': self.segment_count,
            'avg_latency_ms': round(sum(self.latencies) / len(self.latencies), 2) if self.latencies else 0,
            'max_latency_ms': round(max(self.latencies), 2) if self.latencies else 0,
            'min_latency_ms': round(min(self.latencies), 2) if self.latencies else 0
        }


@router.websocket("/ws/stream/{session_id}")
async def websocket_stream_endpoint(
    websocket: WebSocket,
    session_id: str,
    sample_rate: int = Query(default=16000, description="音频采样率"),
    buffer_duration: int = Query(default=3000, description="缓冲区时长 (ms)")
):
    """
    WebSocket 音频流端点
    
    消息格式:
    - 客户端 -> 服务端: {"type": "audio", "data": "<base64>", "duration_ms": 3000}
    - 服务端 -> 客户端: {"type": "transcription_result", ...}
    """
    
    # 连接
    connected = await manager.connect(websocket, session_id)
    if not connected:
        return
    
    # 创建流处理器
    processor = AudioStreamProcessor(session_id, manager)
    processor.buffer_duration_ms = buffer_duration
    
    # 发送连接确认
    await manager.send_personal_message({
        'type': 'connected',
        'session_id': session_id,
        'sample_rate': sample_rate,
        'buffer_duration_ms': buffer_duration,
        'timestamp': time.time()
    }, session_id)
    
    try:
        while True:
            # 接收消息
            data = await websocket.receive_text()
            message = json.loads(data)
            
            msg_type = message.get('type')
            
            if msg_type == 'audio':
                # 处理音频数据（base64 编码）
                import base64
                audio_data = base64.b64decode(message.get('data', ''))
                duration_ms = message.get('duration_ms', 3000)
                
                await processor.process_audio_chunk(audio_data, sample_rate)
            
            elif msg_type == 'ping':
                # 心跳
                await manager.send_personal_message({
                    'type': 'pong',
                    'timestamp': time.time()
                }, session_id)
            
            elif msg_type == 'get_stats':
                # 获取统计
                stats = processor.get_stats()
                session_info = manager.get_session_info(session_id)
                await manager.send_personal_message({
                    'type': 'stats',
                    'processor': stats,
                    'session': session_info,
                    'timestamp': time.time()
                }, session_id)
            
            elif msg_type == 'stop':
                # 停止流处理
                await processor.flush()
                await manager.send_personal_message({
                    'type': 'stopped',
                    'session_id': session_id,
                    'final_stats': processor.get_stats(),
                    'timestamp': time.time()
                }, session_id)
                break
    
    except WebSocketDisconnect:
        print(f"[WS] 客户端断开：{session_id}")
    except Exception as e:
        print(f"[WS ERROR] {session_id}: {e}")
        try:
            await manager.send_personal_message({
                'type': 'error',
                'error': str(e),
                'timestamp': time.time()
            }, session_id)
        except:
            pass
    finally:
        # 清理
        await processor.flush()
        manager.disconnect(session_id)


@router.websocket("/ws/stream/text/{session_id}")
async def websocket_text_stream_endpoint(
    websocket: WebSocket,
    session_id: str
):
    """
    WebSocket 文本流端点（用于测试）
    直接发送文本进行实时分析
    """
    
    connected = await manager.connect(websocket, session_id)
    if not connected:
        return
    
    analysis_service = get_analysis_service()
    
    # 发送连接确认
    await manager.send_personal_message({
        'type': 'connected',
        'session_id': session_id,
        'mode': 'text',
        'timestamp': time.time()
    }, session_id)
    
    segment_count = 0
    latencies = []
    
    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            
            if message.get('type') == 'text':
                text = message.get('content', '')
                start_time = time.time()
                
                # 分析
                result = analysis_service.analyze_segment(session_id, text)
                latency = (time.time() - start_time) * 1000
                latencies.append(latency)
                segment_count += 1
                
                # 发送结果
                await manager.send_personal_message({
                    'type': 'analysis_result',
                    'session_id': session_id,
                    'segment_index': segment_count,
                    'text': text,
                    'analysis': {
                        'sentiment': result.sentiment,
                        'sentiment_score': result.sentiment_score,
                        'keywords': result.keywords,
                        'suggestions': result.suggestions,
                        'risks': result.risks,
                        'emotions': result.emotion_data
                    },
                    'performance': {
                        'latency_ms': round(latency, 2),
                        'avg_latency_ms': round(sum(latencies) / len(latencies), 2)
                    },
                    'timestamp': time.time()
                }, session_id)
            
            elif message.get('type') == 'ping':
                await manager.send_personal_message({
                    'type': 'pong',
                    'timestamp': time.time()
                }, session_id)
            
            elif message.get('type') == 'get_stats':
                session_info = manager.get_session_info(session_id)
                analysis_stats = analysis_service.get_performance_stats()
                await manager.send_personal_message({
                    'type': 'stats',
                    'session': session_info,
                    'analysis': analysis_stats,
                    'segment_count': segment_count,
                    'avg_latency_ms': round(sum(latencies) / len(latencies), 2) if latencies else 0,
                    'timestamp': time.time()
                }, session_id)
    
    except WebSocketDisconnect:
        print(f"[WS TEXT] 客户端断开：{session_id}")
    finally:
        manager.disconnect(session_id)


@router.get("/stream/stats")
async def get_stream_stats():
    """获取流处理统计"""
    return {
        'active_connections': manager.get_connection_count(),
        'sessions': [
            manager.get_session_info(sid)
            for sid in list(manager.active_connections.keys())
        ]
    }


@router.get("/stream/session/{session_id}")
async def get_session_info(session_id: str):
    """获取特定会话信息"""
    info = manager.get_session_info(session_id)
    if info:
        return info
    return {'error': 'Session not found', 'session_id': session_id}
