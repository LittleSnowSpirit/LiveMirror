"""
Frontend Diagnosis Script
Uses Playwright to check frontend page issues
"""

import asyncio
from playwright.async_api import async_playwright
import json


async def diagnose_frontend():
    """Diagnose frontend page"""
    
    frontend_url = "http://localhost:5174"
    results = {
        "url": frontend_url,
        "page_loaded": False,
        "console_errors": [],
        "network_errors": [],
        "javascript_errors": [],
        "screenshot": None,
    }
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            viewport={"width": 1920, "height": 1080}
        )
        page = await context.new_page()
        
        page.on("console", lambda msg: results["console_errors"].append({
            "type": msg.type,
            "text": msg.text,
        }))
        
        page.on("pageerror", lambda error: results["javascript_errors"].append(str(error)))
        
        page.on("requestfailed", lambda request: results["network_errors"].append({
            "url": request.url,
            "error": request.failure.get("errorText", "Unknown") if request.failure else "Unknown",
        }))
        
        try:
            print(f"Visiting: {frontend_url}")
            response = await page.goto(frontend_url, wait_until="networkidle", timeout=10000)
            
            results["page_loaded"] = True
            results["status_code"] = response.status
            results["title"] = await page.title()
            
            await asyncio.sleep(2)
            
            screenshot_path = "D:\\project\\LiveMirror\\tests\\screenshots\\frontend_diagnosis.png"
            await page.screenshot(path=screenshot_path, full_page=True)
            results["screenshot"] = screenshot_path
            
            body_content = await page.content()
            results["body_length"] = len(body_content)
            
            has_app = await page.query_selector("#app")
            results["has_app_element"] = has_app is not None
            
            results["current_url"] = page.url
            
        except Exception as e:
            results["error"] = str(e)
        
        finally:
            await browser.close()
    
    print("\n" + "="*60)
    print("Frontend Diagnosis Results")
    print("="*60)
    print(f"Page Loaded: {'OK' if results['page_loaded'] else 'FAILED'}")
    print(f"Status Code: {results.get('status_code', 'N/A')}")
    print(f"Page Title: {results.get('title', 'N/A')}")
    print(f"Current URL: {results.get('current_url', 'N/A')}")
    print(f"HTML Length: {results.get('body_length', 0)} bytes")
    print(f"#app Element: {'OK' if results.get('has_app_element') else 'MISSING'}")
    
    if results["console_errors"]:
        print(f"\nConsole Errors ({len(results['console_errors'])}):")
        for err in results["console_errors"][:5]:
            print(f"  [{err['type']}] {err['text']}")
    
    if results["javascript_errors"]:
        print(f"\nJS Errors ({len(results['javascript_errors'])}):")
        for err in results["javascript_errors"][:5]:
            print(f"  - {err}")
    
    if results["network_errors"]:
        print(f"\nNetwork Errors ({len(results['network_errors'])}):")
        for err in results["network_errors"][:5]:
            print(f"  - {err['url']}: {err['error']}")
    
    if results.get("screenshot"):
        print(f"\nScreenshot: {results['screenshot']}")
    
    report_path = "D:\\project\\LiveMirror\\tests\\frontend_diagnosis.json"
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print(f"\nFull Report: {report_path}")
    
    return results


if __name__ == "__main__":
    asyncio.run(diagnose_frontend())
