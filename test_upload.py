#!/usr/bin/env python
"""
Test LiveMirror upload and analysis flow
"""

import requests
import time
from pathlib import Path

BACKEND_URL = "http://localhost:8000"
TEST_AUDIO_PATH = "D:\\project\\LiveMirror\\test_audio\\test_podcast_sample.mp3"


def test_health():
    """Test backend health check"""
    print("Testing backend health...")
    response = requests.get(f"{BACKEND_URL}/health", timeout=5)
    print(f"Health check: {response.json()}")
    if response.status_code == 200:
        print("[OK] Backend is healthy")
    return response.status_code == 200


def test_upload(audio_path: str):
    """Upload audio file"""
    print(f"\nUploading audio: {audio_path}")
    
    with open(audio_path, "rb") as f:
        files = {"file": ("test.mp3", f, "audio/mpeg")}
        data = {"speaker_name": "测试主播", "platform": "抖音"}
        
        print("Sending upload request...")
        response = requests.post(
            f"{BACKEND_URL}/api/upload",
            files=files,
            data=data,
            timeout=30
        )
    
    print(f"Upload response status: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"Task ID: {result.get('task_id')}")
        print(f"Status: {result.get('status')}")
        print("[OK] Upload successful")
        return result.get('task_id')
    else:
        print(f"Upload failed: {response.text}")
        return None


def poll_task_status(task_id: str, max_wait: int = 300):
    """Poll task status until completed"""
    print(f"\nPolling task status: {task_id}")
    
    start_time = time.time()
    
    while time.time() - start_time < max_wait:
        response = requests.get(f"{BACKEND_URL}/api/task/{task_id}", timeout=10)
        
        if response.status_code != 200:
            print(f"Error fetching status: {response.text}")
            break
        
        data = response.json()
        status = data.get('status')
        progress = data.get('progress', 0)
        current_step = data.get('current_step', 'unknown')
        
        print(f"Status: {status} | Progress: {progress}% | Step: {current_step}")
        
        if status == 'completed':
            print("[OK] Analysis completed!")
            return data
        elif status == 'failed':
            print(f"[FAIL] Analysis failed: {data.get('error_message')}")
            return None
        
        # Wait before next poll
        time.sleep(3)
    
    print("⏱️ Timeout waiting for task completion")
    return None


def get_report(task_id: str):
    """Get analysis report"""
    print(f"\nFetching analysis report...")
    
    response = requests.get(f"{BACKEND_URL}/api/report/{task_id}", timeout=30)
    
    if response.status_code == 200:
        report = response.json()
        print("[OK] Report retrieved!")
        
        # Print summary
        if 'analysis' in report:
            analysis = report['analysis']
            print(f"\nSummary: {analysis.get('summary', 'N/A')}")
            print(f"Highlights: {len(analysis.get('highlights', []))}")
            print(f"Issues: {len(analysis.get('issues', []))}")
        
        return report
    else:
        print(f"Error fetching report: {response.status_code}")
        print(response.text)
        return None


def main():
    print("="*60)
    print("LiveMirror Upload & Analysis Test")
    print("="*60)
    
    # Step 1: Health check
    if not test_health():
        print("[FAIL] Backend health check failed!")
        return
    
    print("Backend is healthy\n")
    
    # Step 2: Upload audio
    task_id = test_upload(TEST_AUDIO_PATH)
    
    if not task_id:
        print("[FAIL] Upload failed!")
        return
    
    print("Upload successful\n")
    
    # Step 3: Poll for completion
    result = poll_task_status(task_id)
    
    if not result:
        print("[FAIL] Task did not complete successfully")
        return
    
    # Step 4: Get report
    report = get_report(task_id)
    
    if report:
        print("\n" + "="*60)
        print("[SUCCESS] TEST COMPLETED SUCCESSFULLY!")
        print("="*60)
        print(f"\nTest audio: {TEST_AUDIO_PATH}")
        print(f"Task ID: {task_id}")
        print(f"Report available at: {BACKEND_URL}/api/report/{task_id}")
        print(f"\nView report in frontend:")
        print(f"http://localhost:5174/report/{task_id}")
    else:
        print("\n[FAIL] Failed to retrieve report")


if __name__ == "__main__":
    main()
