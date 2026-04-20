"""
LiveMirror 完整集成测试脚本
Integration Test Suite for LiveMirror

测试范围:
1. 环境检查
2. 后端服务测试
3. API 端点测试
4. 功能流程测试
5. 前端组件验证

运行方式:
    python integration_test.py -v

依赖:
    pip install pytest fastapi uvicorn httpx pytest-asyncio pytest-httpx
"""

import pytest
import sys
import os
import json
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any

# 添加项目根目录到路径
ROOT_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT_DIR))

from backend.services.ad_creative import (
    AdCreativeService,
    AdCreative,
    CreativeStatus,
    ABTestStatus,
    CreativeMetrics,
    creative_service
)


# ==================== 测试结果记录 ====================

class IntegrationTestResult:
    """测试结果记录"""
    def __init__(self):
        self.results = []
        self.start_time = datetime.now()
    
    def add_result(self, category: str, test_name: str, passed: bool, details: str = ""):
        self.results.append({
            'category': category,
            'test_name': test_name,
            'passed': passed,
            'details': details,
            'timestamp': datetime.now().isoformat()
        })
    
    def generate_report(self) -> str:
        """生成测试报告"""
        total = len(self.results)
        passed = sum(1 for r in self.results if r['passed'])
        failed = total - passed
        
        report = []
        report.append("# LiveMirror 集成测试报告")
        report.append("")
        report.append(f"**测试时间**: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"**完成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"**总测试数**: {total}")
        report.append(f"**通过**: {passed} ✅")
        report.append(f"**失败**: {failed} ❌")
        report.append(f"**通过率**: {(passed/total*100):.1f}%" if total > 0 else "**通过率**: N/A")
        report.append("")
        
        # 按类别分组
        categories = {}
        for r in self.results:
            cat = r['category']
            if cat not in categories:
                categories[cat] = []
            categories[cat].append(r)
        
        for cat, results in categories.items():
            report.append(f"## {cat}")
            report.append("")
            for r in results:
                status = "✅" if r['passed'] else "❌"
                report.append(f"- {status} **{r['test_name']}**: {r['details']}")
            report.append("")
        
        # 失败总结
        failed_tests = [r for r in self.results if not r['passed']]
        if failed_tests:
            report.append("## 失败测试详情")
            report.append("")
            for r in failed_tests:
                report.append(f"### {r['test_name']}")
                report.append(f"- 类别：{r['category']}")
                report.append(f"- 详情：{r['details']}")
                report.append("")
        
        return "\n".join(report)


# 全局测试结果
test_result = IntegrationTestResult()


# ==================== 第一部分：环境检查 ====================

class TestEnvironment:
    """环境检查测试"""
    
    def test_python_version(self):
        """检查 Python 版本"""
        import sys
        version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
        passed = sys.version_info >= (3, 8)
        test_result.add_result(
            "环境检查",
            "Python 版本检查",
            passed,
            f"Python {version}"
        )
        assert passed, f"Python 版本过低：{version}"
    
    def test_python_dependencies(self):
        """检查 Python 依赖"""
        required_packages = ['fastapi', 'uvicorn', 'pydantic', 'pytest']
        missing = []
        
        for pkg in required_packages:
            try:
                __import__(pkg)
            except ImportError:
                missing.append(pkg)
        
        passed = len(missing) == 0
        test_result.add_result(
            "环境检查",
            "Python 依赖检查",
            passed,
            f"缺少依赖：{missing}" if missing else "所有依赖已安装"
        )
        assert passed, f"缺少依赖：{missing}"
    
    def test_node_available(self):
        """检查 Node.js 是否可用"""
        try:
            result = subprocess.run(['node', '--version'], capture_output=True, text=True, timeout=5)
            version = result.stdout.strip()
            passed = result.returncode == 0
            test_result.add_result(
                "环境检查",
                "Node.js 检查",
                passed,
                version if passed else "Node.js 未安装"
            )
        except Exception as e:
            test_result.add_result(
                "环境检查",
                "Node.js 检查",
                False,
                str(e)
            )
            pytest.fail(f"Node.js 检查失败：{e}")
    
    def test_project_structure(self):
        """检查项目结构"""
        required_dirs = ['backend', 'frontend', 'tests']
        required_files = [
            'backend/services/ad_creative.py',
            'backend/routes/creative.py',
            'tests/test_ad_creative.py'
        ]
        
        missing = []
        for d in required_dirs:
            if not (ROOT_DIR / d).exists():
                missing.append(f"目录：{d}")
        
        for f in required_files:
            if not (ROOT_DIR / f).exists():
                missing.append(f"文件：{f}")
        
        passed = len(missing) == 0
        test_result.add_result(
            "环境检查",
            "项目结构检查",
            passed,
            f"缺失：{missing}" if missing else "项目结构完整"
        )
        assert passed, f"项目结构不完整：{missing}"


# ==================== 第二部分：服务层测试 ====================

class TestServiceLayer:
    """服务层功能测试"""
    
    @pytest.fixture
    def service(self):
        """创建服务实例"""
        return AdCreativeService()
    
    def test_service_initialization(self, service):
        """测试服务初始化"""
        passed = service is not None and hasattr(service, 'creatives')
        test_result.add_result(
            "服务层测试",
            "服务初始化",
            passed,
            "服务实例创建成功" if passed else "服务实例创建失败"
        )
        assert passed
    
    def test_upload_creative_flow(self, service):
        """测试素材上传流程"""
        creative = service.upload_creative(
            name="集成测试素材",
            creative_type="image",
            file_content=b"test_image_content",
            file_path="uploads/test.jpg",
            dimensions={"width": 1080, "height": 1080},
            file_size=102400,
            tags=["测试", "集成"]
        )
        
        passed = (
            creative is not None and
            creative.id is not None and
            creative.name == "集成测试素材" and
            creative.file_hash is not None
        )
        test_result.add_result(
            "服务层测试",
            "素材上传流程",
            passed,
            f"素材 ID: {creative.id}" if passed else "上传失败"
        )
        assert passed
    
    def test_metrics_update_flow(self, service):
        """测试效果数据更新流程"""
        creative = service.upload_creative(
            name="指标测试素材",
            creative_type="image",
            file_content=b"test",
            file_path="uploads/test.jpg",
            dimensions={"width": 1080, "height": 1080},
            file_size=1024
        )
        
        success = service.update_metrics(
            creative.id,
            impressions=10000,
            clicks=500,
            conversions=25,
            spend=200.0,
            revenue=800.0
        )
        
        passed = success and creative.metrics.ctr == 0.05
        test_result.add_result(
            "服务层测试",
            "效果数据更新流程",
            passed,
            f"CTR: {creative.metrics.ctr:.2%}" if passed else "更新失败"
        )
        assert passed
    
    def test_analysis_flow(self, service):
        """测试分析流程"""
        creative = service.upload_creative(
            name="分析测试素材",
            creative_type="image",
            file_content=b"test",
            file_path="uploads/test.jpg",
            dimensions={"width": 1080, "height": 1080},
            file_size=1024
        )
        
        service.update_metrics(creative.id, 50000, 2500, 150, 1000, 5000)
        analysis = service.analyze_creative(creative.id)
        
        passed = (
            analysis is not None and
            'score' in analysis['analysis'] and
            'suggestions' in analysis['analysis']
        )
        test_result.add_result(
            "服务层测试",
            "分析流程",
            passed,
            f"评分：{analysis['analysis']['score']}" if passed else "分析失败"
        )
        assert passed
    
    def test_ab_test_flow(self, service):
        """测试 A/B 测试流程"""
        c1 = service.upload_creative("素材 A", "image", b"test1", "uploads/a.jpg", {"width": 1080, "height": 1080}, 1024)
        c2 = service.upload_creative("素材 B", "image", b"test2", "uploads/b.jpg", {"width": 1080, "height": 1080}, 1024)
        
        service.update_metrics(c1.id, 10000, 500, 25, 200, 800)
        service.update_metrics(c2.id, 10000, 300, 10, 200, 400)
        
        ab_test = service.create_ab_test("A/B 测试", [c1.id, c2.id])
        result = service.complete_ab_test(ab_test.id)
        
        passed = (
            result is not None and
            result['status'] == 'completed' and
            result['winner_id'] == c1.id  # c1 表现更好
        )
        test_result.add_result(
            "服务层测试",
            "A/B 测试流程",
            passed,
            f"获胜者：{result['winner_id']}" if passed else "测试失败"
        )
        assert passed
    
    def test_export_flow(self, service):
        """测试数据导出流程"""
        service.upload_creative("导出测试", "image", b"test", "uploads/test.jpg", {"width": 1080, "height": 1080}, 1024)
        
        export_data = service.export_analytics(format='json')
        data = json.loads(export_data)
        
        passed = (
            'creatives' in data and
            'exported_at' in data
        )
        test_result.add_result(
            "服务层测试",
            "数据导出流程",
            passed,
            f"导出 {len(data['creatives'])} 个素材" if passed else "导出失败"
        )
        assert passed


# ==================== 第三部分：API 端点测试 ====================

class TestAPIEndpoints:
    """API 端点测试（使用 pytest-httpx）"""
    
    @pytest.fixture
    def service(self):
        """创建服务实例"""
        return AdCreativeService()
    
    def test_api_module_import(self):
        """测试 API 模块可导入"""
        try:
            from backend.routes import creative
            passed = hasattr(creative, 'router')
            test_result.add_result(
                "API 端点测试",
                "API 模块导入",
                passed,
                "模块导入成功" if passed else "缺少 router"
            )
        except ImportError as e:
            test_result.add_result(
                "API 端点测试",
                "API 模块导入",
                False,
                str(e)
            )
            pytest.fail(f"API 模块导入失败：{e}")
    
    def test_api_router_configuration(self):
        """测试 API 路由配置"""
        from backend.routes.creative import router
        
        passed = (
            router.prefix == "/api/creative" and
            len(router.routes) > 0
        )
        test_result.add_result(
            "API 端点测试",
            "API 路由配置",
            passed,
            f"配置了 {len(router.routes)} 个路由" if passed else "配置错误"
        )
        assert passed


# ==================== 第四部分：数据模型测试 ====================

class TestDataModels:
    """数据模型测试"""
    
    def test_creative_model(self):
        """测试 AdCreative 数据模型"""
        creative = AdCreative(
            id="test-123",
            name="测试素材",
            creative_type="image",
            file_path="uploads/test.jpg",
            file_hash="abc123",
            dimensions={"width": 1080, "height": 1080},
            file_size=102400
        )
        
        passed = (
            creative.id == "test-123" and
            creative.status == CreativeStatus.DRAFT and
            creative.metrics is not None
        )
        test_result.add_result(
            "数据模型测试",
            "AdCreative 模型",
            passed,
            "模型创建成功" if passed else "模型错误"
        )
        assert passed
    
    def test_metrics_model(self):
        """测试 CreativeMetrics 数据模型"""
        metrics = CreativeMetrics(
            impressions=10000,
            clicks=500,
            conversions=25,
            spend=200.0,
            revenue=800.0
        )
        
        passed = (
            metrics.ctr == 0.05 and
            metrics.cvr == 0.05 and
            metrics.cpc == 0.4 and
            metrics.cpa == 8.0 and
            metrics.roas == 4.0
        )
        test_result.add_result(
            "数据模型测试",
            "CreativeMetrics 模型",
            passed,
            f"ROAS: {metrics.roas}" if passed else "计算错误"
        )
        assert passed
    
    def test_score_calculation(self):
        """测试评分计算"""
        creative = AdCreative(
            id="test-123",
            name="测试",
            creative_type="image",
            file_path="uploads/test.jpg",
            file_hash="abc",
            dimensions={"width": 1080, "height": 1080},
            file_size=1024
        )
        
        # 设置优秀数据
        creative.metrics = CreativeMetrics(50000, 2500, 150, 1000, 5000)
        score = creative.calculate_score()
        
        passed = 60 <= score <= 100  # 优秀数据应该在 60-100 之间
        test_result.add_result(
            "数据模型测试",
            "评分计算",
            passed,
            f"评分：{score}" if passed else f"评分异常：{score}"
        )
        assert passed
    
    def test_enum_values(self):
        """测试枚举值"""
        passed = (
            CreativeStatus.ACTIVE.value == "active" and
            CreativeStatus.DRAFT.value == "draft" and
            ABTestStatus.RUNNING.value == "running"
        )
        test_result.add_result(
            "数据模型测试",
            "枚举值",
            passed,
            "枚举值正确" if passed else "枚举值错误"
        )
        assert passed


# ==================== 第五部分：前端组件验证 ====================

class TestFrontendComponents:
    """前端组件验证"""
    
    def test_vue_files_exist(self):
        """测试 Vue 文件存在"""
        vue_files = [
            'frontend/src/views/AdCreative.vue',
            'frontend/src/components/CreativeCard.vue'
        ]
        
        missing = []
        for f in vue_files:
            if not (ROOT_DIR / f).exists():
                missing.append(f)
        
        passed = len(missing) == 0
        test_result.add_result(
            "前端组件验证",
            "Vue 文件存在",
            passed,
            "文件完整" if passed else f"缺失：{missing}"
        )
        assert passed
    
    def test_vue_syntax(self):
        """测试 Vue 文件语法（基础检查）"""
        vue_files = [
            'frontend/src/views/AdCreative.vue',
            'frontend/src/components/CreativeCard.vue'
        ]
        
        errors = []
        for f in vue_files:
            path = ROOT_DIR / f
            if path.exists():
                content = path.read_text(encoding='utf-8')
                # 基础语法检查
                if '<template>' not in content or '</template>' not in content:
                    errors.append(f"{f}: 缺少 template 标签")
                if '<script' not in content:
                    errors.append(f"{f}: 缺少 script 标签")
                if '<style' not in content:
                    errors.append(f"{f}: 缺少 style 标签")
        
        passed = len(errors) == 0
        test_result.add_result(
            "前端组件验证",
            "Vue 文件语法",
            passed,
            "语法正确" if passed else "; ".join(errors)
        )
        assert passed
    
    def test_api_integration_code(self):
        """测试 API 集成代码"""
        vue_file = ROOT_DIR / 'frontend/src/views/AdCreative.vue'
        
        if not vue_file.exists():
            test_result.add_result(
                "前端组件验证",
                "API 集成代码",
                False,
                "文件不存在"
            )
            pytest.fail("Vue 文件不存在")
        
        content = vue_file.read_text(encoding='utf-8')
        
        # 检查是否包含 API 调用
        has_axios = 'axios' in content
        has_api_base = 'API_BASE' in content or '/api/creative' in content
        has_api_calls = any(endpoint in content for endpoint in [
            'API_BASE',
            '/api/creative',
            'axios.get',
            'axios.post'
        ])
        
        passed = has_axios and (has_api_base or has_api_calls)
        test_result.add_result(
            "前端组件验证",
            "API 集成代码",
            passed,
            "包含 API 调用" if passed else "缺少 API 集成"
        )
        assert passed


# ==================== 第六部分：完整流程测试 ====================

class TestEndToEndFlow:
    """端到端完整流程测试"""
    
    @pytest.fixture
    def service(self):
        """创建服务实例"""
        return AdCreativeService()
    
    def test_complete_workflow(self, service):
        """测试完整工作流程"""
        # 1. 上传素材
        creative = service.upload_creative(
            name="完整流程测试",
            creative_type="image",
            file_content=b"test_content",
            file_path="uploads/test.jpg",
            dimensions={"width": 1080, "height": 1080},
            file_size=102400,
            tags=["测试"]
        )
        
        # 2. 更新效果数据
        service.update_metrics(creative.id, 10000, 500, 25, 200, 800)
        
        # 3. 获取分析
        analysis = service.analyze_creative(creative.id)
        
        # 4. 获取评分
        score = creative.calculate_score()
        
        # 5. 获取推荐
        top = service.get_top_creatives(limit=5)
        
        # 6. 导出数据
        export = service.export_analytics()
        
        passed = (
            creative.id is not None and
            analysis is not None and
            score > 0 and
            len(top) > 0 and
            export is not None
        )
        
        test_result.add_result(
            "端到端流程测试",
            "完整工作流程",
            passed,
            f"素材 ID: {creative.id}, 评分：{score}" if passed else "流程中断"
        )
        assert passed
    
    def test_batch_operations(self, service):
        """测试批量操作"""
        # 上传多个素材
        creatives = []
        for i in range(5):
            c = service.upload_creative(
                f"批量测试{i}",
                "image",
                b"test",
                f"uploads/test{i}.jpg",
                {"width": 1080, "height": 1080},
                1024
            )
            service.update_metrics(c.id, 1000 * (i + 1), 50 * (i + 1), 5, 100, 200)
            creatives.append(c)
        
        # 获取列表
        all_creatives = service.list_creatives()
        
        # 按类型筛选
        images = service.list_creatives(creative_type="image")
        
        # 按状态筛选
        active = service.list_creatives(status=CreativeStatus.ACTIVE)
        
        passed = (
            len(all_creatives) >= 5 and
            len(images) >= 5 and
            len(active) >= 5
        )
        
        test_result.add_result(
            "端到端流程测试",
            "批量操作",
            passed,
            f"创建 {len(creatives)} 个素材" if passed else "批量操作失败"
        )
        assert passed


# ==================== 测试报告生成 ====================

def pytest_sessionfinish(session, exitstatus):
    """测试会话结束时生成报告"""
    report_path = ROOT_DIR / 'tests' / 'INTEGRATION_TEST_REPORT.md'
    
    report_content = test_result.generate_report()
    
    # 添加额外信息
    report_content += "\n\n---\n\n"
    report_content += "## 测试环境\n\n"
    report_content += f"- **Python**: {sys.version}\n"
    report_content += f"- **pytest**: {pytest.__version__}\n"
    report_content += f"- **工作目录**: {ROOT_DIR}\n"
    report_content += f"- **测试文件**: {__file__}\n"
    
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report_content)
    
    print(f"\n✅ 测试报告已生成：{report_path}")


if __name__ == '__main__':
    # 运行测试
    pytest.main([__file__, '-v', '--tb=short'])
