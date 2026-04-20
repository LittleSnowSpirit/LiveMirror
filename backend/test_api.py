"""
API 测试脚本
使用方法：python test_api.py
"""
import requests
import time

BASE_URL = "http://localhost:8000"


def test_health():
    """测试健康检查"""
    print("测试健康检查...")
    response = requests.get(f"{BASE_URL}/health")
    print(f"状态：{response.status_code}")
    print(f"响应：{response.json()}")
    print()


def test_root():
    """测试根路径"""
    print("测试根路径...")
    response = requests.get(f"{BASE_URL}/")
    print(f"状态：{response.status_code}")
    print(f"响应：{response.json()}")
    print()


def test_upload(file_path: str):
    """测试文件上传"""
    print(f"测试文件上传：{file_path}")
    
    with open(file_path, 'rb') as f:
        files = {'file': (file_path, f, 'audio/mpeg')}
        response = requests.post(f"{BASE_URL}/api/upload", files=files)
    
    print(f"状态：{response.status_code}")
    print(f"响应：{response.json()}")
    
    if response.status_code == 200:
        task_id = response.json()['task_id']
        print(f"\n任务 ID: {task_id}")
        return task_id
    print()
    return None


def test_task_status(task_id: str):
    """测试任务状态查询"""
    print(f"测试任务状态查询：{task_id}")
    response = requests.get(f"{BASE_URL}/api/task/{task_id}")
    print(f"状态：{response.status_code}")
    print(f"响应：{response.json()}")
    print()


def test_report(task_id: str):
    """测试报告查询"""
    print(f"测试报告查询：{task_id}")
    response = requests.get(f"{BASE_URL}/api/report/{task_id}")
    print(f"状态：{response.status_code}")
    print(f"响应：{response.json()}")
    print()


def main():
    """主测试流程"""
    print("=" * 50)
    print("LiveMirror API 测试")
    print("=" * 50)
    print()
    
    # 测试基础接口
    test_health()
    test_root()
    
    # 如果有测试文件，测试上传流程
    import sys
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
        task_id = test_upload(file_path)
        
        if task_id:
            # 轮询任务状态
            for i in range(30):  # 最多等待 30 次
                time.sleep(2)
                response = requests.get(f"{BASE_URL}/api/task/{task_id}")
                data = response.json()
                status = data.get('task', {}).get('status', 'unknown')
                progress = data.get('task', {}).get('progress', 0)
                print(f"[{i+1}/30] 状态：{status}, 进度：{progress}%")
                
                if status == 'completed':
                    print("\n任务完成！")
                    test_report(task_id)
                    break
                elif status == 'failed':
                    print("\n任务失败！")
                    break
            else:
                print("\n等待超时")
    else:
        print("提示：提供音频文件路径进行完整测试")
        print("用法：python test_api.py path/to/audio.mp3")
    
    print("=" * 50)
    print("测试完成")
    print("=" * 50)


if __name__ == "__main__":
    main()
