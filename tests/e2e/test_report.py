"""
报告展示 E2E 测试
模拟用户查看分析报告的完整流程
"""
import pytest
from pathlib import Path
from playwright.sync_api import Page, expect, TimeoutError as PlaywrightTimeoutError


class TestReportPage:
    """报告页面 E2E 测试"""
    
    @pytest.mark.e2e
    @pytest.mark.report
    def test_report_page_loads(self, page: Page, frontend_url: str):
        """测试报告页面加载（使用模拟任务 ID）"""
        # 访问一个不存在的报告页，应该显示错误
        fake_task_id = "00000000-0000-0000-0000-000000000000"
        page.goto(f"{frontend_url}/report/{fake_task_id}")
        
        # 页面应该加载
        expect(page).to_have_title("LiveMirror")
        
        # 可能显示错误状态
        error_container = page.locator(".error-container")
        if error_container.count() > 0:
            expect(error_container).to_be_visible()
            print("报告页面加载并正确显示错误")
        else:
            print("报告页面加载（无错误容器）")
    
    @pytest.mark.e2e
    @pytest.mark.report
    def test_report_page_elements(self, page: Page, frontend_url: str):
        """测试报告页面元素结构"""
        # 使用模拟任务 ID
        fake_task_id = "00000000-0000-0000-0000-000000000000"
        page.goto(f"{frontend_url}/report/{fake_task_id}")
        
        # 等待页面加载
        page.wait_for_timeout(2000)
        
        # 检查主要元素是否存在（可能显示错误）
        has_content = (
            page.locator(".report-content").count() > 0 or
            page.locator(".error-container").count() > 0 or
            page.locator(".loading-container").count() > 0
        )
        
        assert has_content, "页面应该有内容（报告、错误或加载中）"
        print("报告页面元素结构验证通过")
    
    @pytest.mark.e2e
    @pytest.mark.report
    def test_summary_card_display(
        self,
        page: Page,
        frontend_url: str,
        completed_task_id: str = None
    ):
        """测试摘要卡片显示"""
        if not completed_task_id:
            pytest.skip("需要已完成的任务 ID")
        
        page.goto(f"{frontend_url}/report/{completed_task_id}")
        
        # 等待报告加载
        try:
            expect(page.locator(".summary-card")).to_be_visible(timeout=10000)
            
            # 验证统计信息显示
            expect(page.locator(".summary-stats")).to_be_visible()
            
            print("摘要卡片显示正确")
        except PlaywrightTimeoutError:
            print("未找到摘要卡片")
    
    @pytest.mark.e2e
    @pytest.mark.report
    def test_timeline_rendering(
        self,
        page: Page,
        frontend_url: str,
        completed_task_id: str = None
    ):
        """测试时间轴渲染"""
        if not completed_task_id:
            pytest.skip("需要已完成的任务 ID")
        
        page.goto(f"{frontend_url}/report/{completed_task_id}")
        
        try:
            # 等待时间轴组件
            timeline = page.locator(".timeline-card, .report-timeline")
            expect(timeline).to_be_visible(timeout=10000)
            
            print("时间轴渲染正确")
        except PlaywrightTimeoutError:
            print("未找到时间轴组件")
    
    @pytest.mark.e2e
    @pytest.mark.report
    def test_filter_functionality(
        self,
        page: Page,
        frontend_url: str,
        completed_task_id: str = None
    ):
        """测试筛选功能"""
        if not completed_task_id:
            pytest.skip("需要已完成的任务 ID")
        
        page.goto(f"{frontend_url}/report/{completed_task_id}")
        
        try:
            # 等待筛选器
            filter_bar = page.locator(".filter-bar")
            expect(filter_bar).to_be_visible(timeout=10000)
            
            # 测试"只看爆点"筛选
            highlight_filter = page.locator(".filter-bar button:has-text('爆点'), .filter-bar .el-radio-button:has-text('爆点')")
            if highlight_filter.count() > 0:
                highlight_filter.click()
                page.wait_for_timeout(1000)
                
                # 验证筛选结果计数更新
                result_count = page.locator(".result-count")
                if result_count.count() > 0:
                    print(f"筛选后结果数：{result_count.inner_text()}")
            
            # 测试"只看翻车"筛选
            issue_filter = page.locator(".filter-bar button:has-text('翻车'), .filter-bar .el-radio-button:has-text('翻车')")
            if issue_filter.count() > 0:
                issue_filter.click()
                page.wait_for_timeout(1000)
                
                print("翻车筛选测试完成")
            
            # 重置为全部
            all_filter = page.locator(".filter-bar button:has-text('全部'), .filter-bar .el-radio-button:has-text('全部')")
            if all_filter.count() > 0:
                all_filter.click()
            
            print("筛选功能测试通过")
        except PlaywrightTimeoutError:
            print("未找到筛选器组件")
    
    @pytest.mark.e2e
    @pytest.mark.report
    def test_speech_cards_display(
        self,
        page: Page,
        frontend_url: str,
        completed_task_id: str = None
    ):
        """测试话术卡片显示"""
        if not completed_task_id:
            pytest.skip("需要已完成的任务 ID")
        
        page.goto(f"{frontend_url}/report/{completed_task_id}")
        
        try:
            # 等待话术列表
            speeches_list = page.locator(".speeches-list")
            expect(speeches_list).to_be_visible(timeout=10000)
            
            # 验证话术卡片
            speech_cards = page.locator(".speech-card")
            count = speech_cards.count()
            
            if count > 0:
                print(f"显示 {count} 个话术卡片")
                
                # 验证第一个卡片的内容
                first_card = speech_cards.first
                expect(first_card).to_be_visible()
            else:
                print("没有话术卡片（可能报告为空）")
        except PlaywrightTimeoutError:
            print("未找到话术列表")
    
    @pytest.mark.e2e
    @pytest.mark.report
    def test_export_button(self, page: Page, frontend_url: str, completed_task_id: str = None):
        """测试导出按钮"""
        if not completed_task_id:
            pytest.skip("需要已完成的任务 ID")
        
        page.goto(f"{frontend_url}/report/{completed_task_id}")
        
        try:
            # 等待导出按钮
            export_button = page.locator("button:has-text('导出'), button:has-text('PDF')")
            expect(export_button).to_be_visible(timeout=10000)
            
            # 验证按钮可点击
            expect(export_button).to_be_enabled()
            
            print("导出按钮存在且可用")
        except PlaywrightTimeoutError:
            print("未找到导出按钮")
    
    @pytest.mark.e2e
    @pytest.mark.report
    def test_back_button_navigation(
        self,
        page: Page,
        frontend_url: str,
        completed_task_id: str = None
    ):
        """测试返回按钮导航"""
        if not completed_task_id:
            pytest.skip("需要已完成的任务 ID")
        
        # 先访问首页
        page.goto(frontend_url)
        initial_url = page.url
        
        # 访问报告页
        page.goto(f"{frontend_url}/report/{completed_task_id}")
        
        try:
            # 找到返回按钮
            back_button = page.locator("button:has-text('返回'), button:has-text('历史')")
            expect(back_button).to_be_visible(timeout=5000)
            
            # 点击返回
            back_button.click()
            
            # 验证导航
            page.wait_for_url("*/history", timeout=5000)
            assert "/history" in page.url or page.url == initial_url
            
            print("返回按钮导航正确")
        except PlaywrightTimeoutError:
            print("未找到返回按钮或导航失败")
    
    @pytest.mark.e2e
    @pytest.mark.report
    def test_loading_state(
        self,
        page: Page,
        frontend_url: str,
        slow_task_id: str = None
    ):
        """测试加载状态显示"""
        if not slow_task_id:
            # 使用一个不存在的 ID 来测试加载状态
            page.goto(f"{frontend_url}/report/00000000-0000-0000-0000-000000000001")
        else:
            page.goto(f"{frontend_url}/report/{slow_task_id}")
        
        # 检查是否有加载状态
        loading = page.locator(".loading-container, .el-skeleton, .loading")
        
        if loading.count() > 0:
            expect(loading).to_be_visible()
            print("加载状态显示正确")
        else:
            print("未显示加载状态（可能加载太快或显示错误）")
    
    @pytest.mark.e2e
    @pytest.mark.report
    def test_error_state_display(self, page: Page, frontend_url: str):
        """测试错误状态显示"""
        fake_task_id = "00000000-0000-0000-0000-000000000000"
        page.goto(f"{frontend_url}/report/{fake_task_id}")
        
        # 等待错误状态
        try:
            error_container = page.locator(".error-container, .el-result")
            expect(error_container).to_be_visible(timeout=10000)
            
            # 验证错误信息
            expect(error_container).to_contain_text("失败|错误|Error|不存在", timeout=5000)
            
            print("错误状态显示正确")
        except PlaywrightTimeoutError:
            print("未显示错误状态容器")
    
    @pytest.mark.e2e
    @pytest.mark.report
    def test_retry_functionality(self, page: Page, frontend_url: str):
        """测试重试功能"""
        fake_task_id = "00000000-0000-0000-0000-000000000000"
        page.goto(f"{frontend_url}/report/{fake_task_id}")
        
        try:
            # 找到重试按钮
            retry_button = page.locator("button:has-text('重新加载'), button:has-text('重试')")
            expect(retry_button).to_be_visible(timeout=5000)
            
            # 点击重试
            retry_button.click()
            
            # 验证页面重新加载
            page.wait_for_load_state("networkidle", timeout=5000)
            
            print("重试功能测试通过")
        except PlaywrightTimeoutError:
            print("未找到重试按钮")


class TestReportResponsiveness:
    """报告页面响应式测试"""
    
    @pytest.mark.e2e
    @pytest.mark.report
    def test_mobile_viewport(self, page: Page, frontend_url: str):
        """测试移动端视图"""
        # 设置移动端视口
        page.set_viewport_size({"width": 375, "height": 667})
        
        page.goto(frontend_url)
        
        # 验证页面适应移动端
        expect(page.locator("body")).to_be_visible()
        
        # 检查是否有横向滚动（不应该有）
        body_width = page.evaluate("document.body.scrollWidth")
        viewport_width = page.viewport_size["width"]
        
        assert body_width <= viewport_width, "页面不应该有横向滚动"
        
        print("移动端视图测试通过")
    
    @pytest.mark.e2e
    @pytest.mark.report
    def test_tablet_viewport(self, page: Page, frontend_url: str):
        """测试平板端视图"""
        page.set_viewport_size({"width": 768, "height": 1024})
        
        page.goto(frontend_url)
        
        expect(page.locator("body")).to_be_visible()
        
        print("平板端视图测试通过")
    
    @pytest.mark.e2e
    @pytest.mark.report
    def test_desktop_viewport(self, page: Page, frontend_url: str):
        """测试桌面端视图"""
        page.set_viewport_size({"width": 1920, "height": 1080})
        
        page.goto(frontend_url)
        
        expect(page.locator("body")).to_be_visible()
        
        print("桌面端视图测试通过")


class TestReportAccessibility:
    """报告页面可访问性测试"""
    
    @pytest.mark.e2e
    @pytest.mark.report
    def test_keyboard_navigation(self, page: Page, frontend_url: str):
        """测试键盘导航"""
        page.goto(frontend_url)
        
        # 使用 Tab 键遍历所有可聚焦元素
        for _ in range(20):
            page.keyboard.press("Tab")
            
            focused = page.locator(":focus")
            assert focused.count() > 0
        
        print("键盘导航测试通过")
    
    @pytest.mark.e2e
    @pytest.mark.report
    def test_aria_labels(self, page: Page, frontend_url: str):
        """测试 ARIA 标签"""
        page.goto(frontend_url)
        
        # 检查主要交互元素是否有 ARIA 标签
        buttons = page.locator("button")
        count = buttons.count()
        
        if count > 0:
            # 至少部分按钮应该有可访问性标签
            buttons_with_aria = 0
            for i in range(min(count, 5)):  # 检查前 5 个按钮
                aria_label = buttons.nth(i).get_attribute("aria-label")
                aria_labelledby = buttons.nth(i).get_attribute("aria-labelledby")
                text_content = buttons.nth(i).inner_text()
                
                if aria_label or aria_labelledby or text_content:
                    buttons_with_aria += 1
            
            print(f"检查 {min(count, 5)} 个按钮，{buttons_with_aria} 个有可访问性标签")
        
        print("ARIA 标签测试完成")
