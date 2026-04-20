"""
LiveMirror 实时流测试脚本
测试 WebSocket 连接、流式转写、实时分析延迟、断线重连
"""

import asyncio
import json
import time
import sys
from pathlib import Path

# 添加父目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent / 'backend'))

from services.realtime_analysis import get_analysis_service, AnalysisResult


class RealtimeTestSuite:
    """实时流测试套件"""
    
    def __init__(self):
        self.results = {
            'websocket_connection': None,
            'streaming_transcription': None,
            'realtime_analysis_latency': None,
            'suggestion_push': None,
            'reconnection': None
        }
        self.latencies = []
        self.suggestions_received = []
    
    async def test_websocket_connection(self, base_url: str = 'ws://localhost:8000'):
        """测试 1: WebSocket 连接"""
        print("\n" + "="*60)
        print("测试 1: WebSocket 连接")
        print("="*60)
        
        try:
            import websockets
            
            session_id = f"test_session_{int(time.time())}"
            url = f"{base_url}/ws/stream/text/{session_id}"
            
            start_time = time.time()
            async with websockets.connect(url) as websocket:
                connect_time = (time.time() - start_time) * 1000
                
                # 等待连接确认
                response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                data = json.loads(response)
                
                if data.get('type') == 'connected':
                    print(f"✅ 连接成功")
                    print(f"   会话 ID: {session_id}")
                    print(f"   连接耗时：{connect_time:.2f}ms")
                    print(f"   模式：{data.get('mode', 'N/A')}")
                    
                    self.results['websocket_connection'] = {
                        'status': 'PASS',
                        'connect_time_ms': round(connect_time, 2),
                        'session_id': session_id
                    }
                    return True
                else:
                    print(f"❌ 连接失败： unexpected response {data}")
                    self.results['websocket_connection'] = {
                        'status': 'FAIL',
                        'error': f'Unexpected response: {data}'
                    }
                    return False
        
        except ImportError:
            print("⚠️  缺少 websockets 库，跳过 WebSocket 测试")
            print("   安装：pip install websockets")
            self.results['websocket_connection'] = {
                'status': 'SKIP',
                'reason': 'websockets library not installed'
            }
            return False
        
        except Exception as e:
            print(f"❌ 连接失败：{e}")
            self.results['websocket_connection'] = {
                'status': 'FAIL',
                'error': str(e)
            }
            return False
    
    async def test_streaming_transcription(self, base_url: str = 'ws://localhost:8000'):
        """测试 2: 流式转写"""
        print("\n" + "="*60)
        print("测试 2: 流式转写")
        print("="*60)
        
        try:
            import websockets
            
            session_id = f"test_stream_{int(time.time())}"
            url = f"{base_url}/ws/stream/text/{session_id}"
            
            test_texts = [
                "大家好，欢迎来到直播间！",
                "今天给大家带来超值福利。",
                "这个产品非常好用，价格也很优惠。",
                "限时限量，赶紧下单不要错过！"
            ]
            
            async with websockets.connect(url) as websocket:
                # 等待连接确认
                await websocket.recv()
                
                results = []
                for i, text in enumerate(test_texts):
                    # 发送文本
                    message = {
                        'type': 'text',
                        'content': text
                    }
                    send_time = time.time()
                    await websocket.send(json.dumps(message))
                    
                    # 接收分析结果
                    response = await asyncio.wait_for(websocket.recv(), timeout=10.0)
                    data = json.loads(response)
                    recv_time = time.time()
                    
                    latency = (recv_time - send_time) * 1000
                    self.latencies.append(latency)
                    
                    result = {
                        'index': i,
                        'text': text,
                        'latency_ms': round(latency, 2),
                        'received': data.get('type') == 'analysis_result'
                    }
                    results.append(result)
                    
                    print(f"片段 {i+1}: 延迟 {latency:.2f}ms - {'✅' if result['received'] else '❌'}")
                
                # 计算统计
                avg_latency = sum(self.latencies) / len(self.latencies)
                min_latency = min(self.latencies)
                max_latency = max(self.latencies)
                
                print(f"\n性能统计:")
                print(f"   平均延迟：{avg_latency:.2f}ms")
                print(f"   最小延迟：{min_latency:.2f}ms")
                print(f"   最大延迟：{max_latency:.2f}ms")
                
                all_received = all(r['received'] for r in results)
                passed = all_received and avg_latency < 3000
                
                self.results['streaming_transcription'] = {
                    'status': 'PASS' if passed else 'FAIL',
                    'segments_tested': len(results),
                    'all_received': all_received,
                    'avg_latency_ms': round(avg_latency, 2),
                    'min_latency_ms': round(min_latency, 2),
                    'max_latency_ms': round(max_latency, 2)
                }
                
                return passed
        
        except ImportError:
            print("⚠️  缺少 websockets 库，跳过测试")
            self.results['streaming_transcription'] = {
                'status': 'SKIP',
                'reason': 'websockets library not installed'
            }
            return False
        
        except Exception as e:
            print(f"❌ 测试失败：{e}")
            self.results['streaming_transcription'] = {
                'status': 'FAIL',
                'error': str(e)
            }
            return False
    
    async def test_realtime_analysis_latency(self):
        """测试 3: 实时分析延迟"""
        print("\n" + "="*60)
        print("测试 3: 实时分析延迟")
        print("="*60)
        
        service = get_analysis_service()
        session_id = "latency_test_session"
        
        test_texts = [
            "这个产品真的很好用，推荐给大家！",
            "价格有点贵，但是质量不错。",
            "限时优惠，最后 10 单，赶紧下单！",
            "我们的产品是市面上最好的，效果 100% 保证。"
        ]
        
        latencies = []
        
        for i, text in enumerate(test_texts):
            start_time = time.time()
            result = service.analyze_segment(session_id, text, audio_duration_ms=2000)
            latency = (time.time() - start_time) * 1000
            latencies.append(latency)
            
            print(f"片段 {i+1}: 分析延迟 {latency:.2f}ms (总延迟 {result.latency_ms}ms)")
            
            # 验证结果完整性
            assert result.sentiment in ['positive', 'neutral', 'negative'], "情绪分类错误"
            assert 0 <= result.sentiment_score <= 1, "情绪分数超出范围"
            assert isinstance(result.keywords, list), "关键词应为列表"
            assert isinstance(result.suggestions, list), "建议应为列表"
        
        avg_latency = sum(latencies) / len(latencies)
        max_latency = max(latencies)
        
        print(f"\n性能统计:")
        print(f"   平均分析延迟：{avg_latency:.2f}ms")
        print(f"   最大分析延迟：{max_latency:.2f}ms")
        print(f"   延迟要求：<3000ms")
        
        # 检查是否满足延迟要求
        total_latency_ok = all(lat < 3000 for lat in latencies)
        
        self.results['realtime_analysis_latency'] = {
            'status': 'PASS' if total_latency_ok else 'FAIL',
            'segments_tested': len(latencies),
            'avg_latency_ms': round(avg_latency, 2),
            'max_latency_ms': round(max_latency, 2),
            'requirement_ms': 3000,
            'all_within_requirement': total_latency_ok
        }
        
        if total_latency_ok:
            print(f"✅ 所有片段延迟满足要求 (<3000ms)")
        else:
            print(f"❌ 部分片段延迟超出要求")
        
        return total_latency_ok
    
    async def test_suggestion_push(self):
        """测试 4: 建议推送"""
        print("\n" + "="*60)
        print("测试 4: 建议推送")
        print("="*60)
        
        service = get_analysis_service()
        session_id = "suggestion_test_session"
        
        # 测试用例：文本 -> 期望的建议类型
        test_cases = [
            ("这个产品很好", "general"),
            ("只要 99 块钱", "price"),
            ("赶紧下单", "action"),
            ("可能是最好的", "uncertainty"),
            ("100% 保证", "risk")
        ]
        
        suggestions_found = 0
        risks_found = 0
        
        for text, expected_type in test_cases:
            result = service.analyze_segment(session_id, text)
            
            has_suggestion = len(result.suggestions) > 0
            has_risk = len(result.risks) > 0
            
            if has_suggestion:
                suggestions_found += 1
                print(f"✅ '{text}' -> 建议：{result.suggestions[0]}")
            elif has_risk:
                risks_found += 1
                print(f"⚠️  '{text}' -> 风险：{result.risks[0]}")
            else:
                print(f"➡️  '{text}' -> 无建议")
        
        print(f"\n统计:")
        print(f"   触发建议：{suggestions_found}/{len(test_cases)}")
        print(f"   触发风险：{risks_found}/{len(test_cases)}")
        
        # 至少 60% 的测试用例应该触发建议或风险
        triggered = suggestions_found + risks_found
        passed = triggered >= len(test_cases) * 0.6
        
        self.results['suggestion_push'] = {
            'status': 'PASS' if passed else 'FAIL',
            'test_cases': len(test_cases),
            'suggestions_triggered': suggestions_found,
            'risks_triggered': risks_found,
            'total_triggered': triggered,
            'trigger_rate': round(triggered / len(test_cases) * 100, 1)
        }
        
        if passed:
            print(f"✅ 建议推送功能正常 (触发率 {triggered / len(test_cases) * 100:.1f}%)")
        else:
            print(f"❌ 建议推送触发率过低")
        
        return passed
    
    async def test_reconnection(self, base_url: str = 'ws://localhost:8000'):
        """测试 5: 断线重连"""
        print("\n" + "="*60)
        print("测试 5: 断线重连")
        print("="*60)
        
        try:
            import websockets
            
            session_id = f"reconnect_test_{int(time.time())}"
            url = f"{base_url}/ws/stream/text/{session_id}"
            
            reconnect_success = 0
            reconnect_attempts = 3
            
            for i in range(reconnect_attempts):
                try:
                    print(f"重连尝试 {i+1}/{reconnect_attempts}...")
                    async with websockets.connect(url) as websocket:
                        # 等待连接确认
                        response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                        data = json.loads(response)
                        
                        if data.get('type') == 'connected':
                            print(f"  ✅ 连接成功")
                            reconnect_success += 1
                            
                            # 发送测试消息
                            await websocket.send(json.dumps({
                                'type': 'text',
                                'content': f'重连测试消息 {i+1}'
                            }))
                            
                            # 接收响应
                            response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                            data = json.loads(response)
                            if data.get('type') == 'analysis_result':
                                print(f"  ✅ 消息处理正常")
                        
                        # 主动断开
                        await websocket.close()
                    
                    # 等待一小段时间再重连
                    await asyncio.sleep(0.5)
                
                except Exception as e:
                    print(f"  ❌ 连接失败：{e}")
            
            print(f"\n统计:")
            print(f"   重连成功：{reconnect_success}/{reconnect_attempts}")
            
            passed = reconnect_success >= reconnect_attempts * 0.8
            
            self.results['reconnection'] = {
                'status': 'PASS' if passed else 'FAIL',
                'attempts': reconnect_attempts,
                'successes': reconnect_success,
                'success_rate': round(reconnect_success / reconnect_attempts * 100, 1)
            }
            
            if passed:
                print(f"✅ 断线重连功能正常 (成功率 {reconnect_success / reconnect_attempts * 100:.1f}%)")
            else:
                print(f"❌ 重连成功率过低")
            
            return passed
        
        except ImportError:
            print("⚠️  缺少 websockets 库，跳过测试")
            self.results['reconnection'] = {
                'status': 'SKIP',
                'reason': 'websockets library not installed'
            }
            return False
        
        except Exception as e:
            print(f"❌ 测试失败：{e}")
            self.results['reconnection'] = {
                'status': 'FAIL',
                'error': str(e)
            }
            return False
    
    def print_summary(self):
        """打印测试总结"""
        print("\n" + "="*60)
        print("测试总结")
        print("="*60)
        
        total_tests = len(self.results)
        passed = sum(1 for r in self.results.values() if r.get('status') == 'PASS')
        failed = sum(1 for r in self.results.values() if r.get('status') == 'FAIL')
        skipped = sum(1 for r in self.results.values() if r.get('status') == 'SKIP')
        
        print(f"\n总测试数：{total_tests}")
        print(f"✅ 通过：{passed}")
        print(f"❌ 失败：{failed}")
        print(f"⚠️  跳过：{skipped}")
        print(f"通过率：{passed / (passed + failed) * 100:.1f}% (不计跳过)" if (passed + failed) > 0 else "")
        
        print("\n详细结果:")
        for test_name, result in self.results.items():
            status = result.get('status', 'UNKNOWN')
            status_icon = {'PASS': '✅', 'FAIL': '❌', 'SKIP': '⚠️'}.get(status, '❓')
            print(f"  {status_icon} {test_name}: {status}")
            
            # 打印额外信息
            if 'avg_latency_ms' in result:
                print(f"      平均延迟：{result['avg_latency_ms']}ms")
            if 'success_rate' in result:
                print(f"      成功率：{result['success_rate']}%")
        
        # 保存结果
        self.save_results()
        
        return passed, failed, skipped
    
    def save_results(self, path: str = "test_realtime_results.json"):
        """保存测试结果"""
        import json
        
        results_data = {
            'timestamp': time.time(),
            'tests': self.results,
            'summary': {
                'total': len(self.results),
                'passed': sum(1 for r in self.results.values() if r.get('status') == 'PASS'),
                'failed': sum(1 for r in self.results.values() if r.get('status') == 'FAIL'),
                'skipped': sum(1 for r in self.results.values() if r.get('status') == 'SKIP')
            }
        }
        
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(results_data, f, ensure_ascii=False, indent=2)
        
        print(f"\n📄 测试结果已保存到：{path}")


async def main():
    """主测试函数"""
    print("="*60)
    print("LiveMirror 实时流测试套件")
    print("="*60)
    
    suite = RealtimeTestSuite()
    
    # 检查服务器是否运行
    print("\n检查服务器状态...")
    try:
        import aiohttp
        async with aiohttp.ClientSession() as session:
            async with session.get('http://localhost:8000/stream/stats') as response:
                if response.status == 200:
                    print("✅ 服务器运行正常")
                else:
                    print(f"⚠️  服务器响应异常：{response.status}")
    except ImportError:
        print("⚠️  无法检查服务器状态 (缺少 aiohttp)")
    except Exception as e:
        print(f"❌ 服务器可能未运行：{e}")
        print("\n请先启动后端服务器:")
        print("  cd backend")
        print("  uvicorn main:app --reload")
        return
    
    # 运行测试
    base_url = 'ws://localhost:8000'
    
    # 测试 1: WebSocket 连接
    await suite.test_websocket_connection(base_url)
    
    # 测试 2: 流式转写
    await suite.test_streaming_transcription(base_url)
    
    # 测试 3: 实时分析延迟 (不需要 WebSocket)
    await suite.test_realtime_analysis_latency()
    
    # 测试 4: 建议推送
    await suite.test_suggestion_push()
    
    # 测试 5: 断线重连
    await suite.test_reconnection(base_url)
    
    # 打印总结
    suite.print_summary()


if __name__ == "__main__":
    asyncio.run(main())
