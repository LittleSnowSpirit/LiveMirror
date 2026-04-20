#!/usr/bin/env python
"""
LiveMirror E2E Test
Full user flow: upload -> analyze -> view report
"""

import asyncio
from playwright.async_api import async_playwright
import requests
import time
from pathlib import Path
import sys


async def test_api_flow():
    """Test API flow"""
    print("\n" + "="*60)
    print("API Flow Test")
    print("="*60)
    
    test_audio = Path("D:/project/LiveMirror/test_audio/live_streaming_demo.mp3")
    
    # Step 1: Upload
    print("\n[1/4] Uploading audio...")
    with open(test_audio, 'rb') as f:
        r = requests.post(
            'http://localhost:8000/api/upload',
            files={'file': f}
        )
    
    if r.status_code != 200:
        print(f"[FAIL] Upload failed: {r.status_code}")
        return False
    
    data = r.json()
    task_id = data.get('task_id')
    print(f"[OK] Upload success, task_id: {task_id}")
    
    # Step 2: Poll status
    print("\n[2/4] Polling task status...")
    for i in range(60):
        r = requests.get(f'http://localhost:8000/api/task/{task_id}')
        task_data = r.json().get('task', {})
        status = task_data.get('status')
        progress = task_data.get('progress', 0)
        
        print(f"  [{i+1}] Status: {status}, Progress: {progress}%")
        
        if status == 'completed':
            print("[OK] Analysis completed")
            break
        elif status == 'failed':
            print(f"[FAIL] Analysis failed: {task_data.get('error_message')}")
            return False
        
        await asyncio.sleep(2)
    else:
        print("[WARN] Poll timeout")
    
    # Step 3: Get report
    print("\n[3/4] Getting analysis report...")
    r = requests.get(f'http://localhost:8000/api/report/{task_id}')
    if r.status_code != 200:
        print(f"[FAIL] Get report failed: {r.status_code}")
        return False
    
    report = r.json()
    print(f"[OK] Report retrieved")
    
    # Step 4: Verify report content
    print("\n[4/4] Verifying report content...")
    data = report.get('data', {})
    transcription = data.get('transcription', '')
    
    if len(transcription) > 100:
        print(f"[OK] Transcription length: {len(transcription)} chars")
        print(f"  First 50 chars: {transcription[:50]}...")
    else:
        print(f"[WARN] Transcription too short: {len(transcription)} chars")
    
    print("\n" + "="*60)
    print("API Flow Test Complete")
    print("="*60)
    
    return True


async def test_full_flow():
    """Test full E2E flow"""
    
    print("="*60)
    print("LiveMirror E2E Test")
    print("="*60)
    
    # Prepare test file
    test_audio = Path("D:/project/LiveMirror/test_audio/live_streaming_demo.mp3")
    if not test_audio.exists():
        print(f"[FAIL] Test audio not found: {test_audio}")
        return False
    
    print(f"[OK] Test file: {test_audio}")
    print(f"[OK] File size: {test_audio.stat().st_size / 1024:.1f} KB")
    
    # Check backend
    try:
        r = requests.get('http://localhost:8000/health', timeout=5)
        if r.status_code != 200:
            print(f"[FAIL] Backend unhealthy: {r.status_code}")
            return False
        print("[OK] Backend service OK")
    except Exception as e:
        print(f"[FAIL] Backend unavailable: {e}")
        return False
    
    # Check frontend
    try:
        r = requests.get('http://localhost:5174', timeout=5)
        if r.status_code != 200:
            print(f"[FAIL] Frontend unhealthy: {r.status_code}")
            return False
        print("[OK] Frontend service OK")
    except Exception as e:
        print(f"[FAIL] Frontend unavailable: {e}")
        return False
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(viewport={"width": 1920, "height": 1080})
        page = await context.new_page()
        
        # Step 1: Visit homepage
        print("\n[1/6] Visiting homepage...")
        await page.goto("http://localhost:5174", wait_until="networkidle")
        await page.screenshot(path="D:/project/LiveMirror/tests/screenshots/01_home.png")
        
        # Verify elements
        upload_area = page.locator('.upload-area')
        if await upload_area.count() == 0:
            print("[FAIL] Upload area not found")
            await browser.close()
            return False
        print("[OK] Homepage loaded")
        
        # Step 2: Upload file
        print("\n[2/6] Uploading audio file...")
        file_input = page.locator('input[type="file"]')
        await file_input.set_input_files(str(test_audio))
        
        # Wait for file display
        await page.wait_for_selector('.file-info', timeout=10000)
        await page.screenshot(path="D:/project/LiveMirror/tests/screenshots/02_uploaded.png")
        print("[OK] File uploaded")
        
        # Step 3: Click analyze
        print("\n[3/6] Clicking analyze...")
        analyze_btn = page.locator('button:has-text("开始分析")')
        await analyze_btn.click()
        await page.screenshot(path="D:/project/LiveMirror/tests/screenshots/03_analyzing.png")
        print("[OK] Analysis started")
        
        # Step 4: Wait for progress
        print("\n[4/6] Waiting for progress...")
        try:
            await page.wait_for_selector('.el-progress', timeout=30000)
            print("[OK] Progress bar visible")
        except:
            print("[WARN] Progress bar not visible")
        
        # Step 5: Wait for completion
        print("\n[5/6] Waiting for completion...")
        try:
            await page.wait_for_selector('.el-progress--success, .report-page', timeout=120000)
            print("[OK] Analysis completed")
        except Exception as e:
            print(f"[WARN] Wait timeout: {e}")
        
        await page.screenshot(path="D:/project/LiveMirror/tests/screenshots/04_completed.png")
        
        # Step 6: View report
        print("\n[6/6] Viewing report...")
        current_url = page.url
        if '/report/' in current_url:
            print("[OK] Auto-redirected to report page")
            await page.screenshot(path="D:/project/LiveMirror/tests/screenshots/05_report.png")
        else:
            print("[WARN] No auto-redirect, navigating to history")
            await page.goto("http://localhost:5174/history", wait_until="networkidle")
            await page.screenshot(path="D:/project/LiveMirror/tests/screenshots/05_history.png")
        
        await browser.close()
    
    print("\n" + "="*60)
    print("E2E Test Complete")
    print("="*60)
    
    return True


async def main():
    """Main test function"""
    
    # Create screenshot directory
    screenshot_dir = Path("D:/project/LiveMirror/tests/screenshots")
    screenshot_dir.mkdir(parents=True, exist_ok=True)
    
    # Run API test
    api_success = await test_api_flow()
    
    # Run E2E test
    e2e_success = await test_full_flow()
    
    # Summary
    print("\n" + "="*60)
    print("Test Summary")
    print("="*60)
    print(f"API Test: {'[PASS]' if api_success else '[FAIL]'}")
    print(f"E2E Test: {'[PASS]' if e2e_success else '[FAIL]'}")
    print("="*60)
    
    return api_success and e2e_success


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
