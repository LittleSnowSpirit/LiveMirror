"""
敏感词检测功能测试 - LiveMirror
测试词库管理、实时检测、分级预警、替换建议
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from backend.services.sensitive_words import (
    SensitiveWordService,
    SeverityLevel,
    SensitiveWordCategory
)
import shutil


def cleanup_test_dir():
    """清理测试目录"""
    if os.path.exists("data/sensitive_words_test"):
        shutil.rmtree("data/sensitive_words_test")


def test_word_library_management():
    """测试 1: 词库管理功能"""
    print("\n" + "="*60)
    print("测试 1: 词库管理功能")
    print("="*60)
    
    cleanup_test_dir()
    service = SensitiveWordService(data_dir="data/sensitive_words_test")
    
    # 测试添加敏感词
    print("\n[1.1] 测试添加敏感词...")
    success = service.add_word(
        word="测试词",
        severity=SeverityLevel.WARNING,
        category=SensitiveWordCategory.GENERAL,
        replacement="示例词",
        reason="测试用途"
    )
    assert success, "添加敏感词失败"
    print("[OK] 成功添加敏感词 '测试词'")
    
    # 测试重复添加
    print("\n[1.2] 测试重复添加...")
    success = service.add_word(
        word="测试词",
        severity=SeverityLevel.WARNING,
        category=SensitiveWordCategory.GENERAL
    )
    assert not success, "重复添加应该失败"
    print("[OK] 重复添加正确被阻止")
    
    # 测试获取敏感词
    print("\n[1.3] 测试获取敏感词详情...")
    entry = service.get_word("测试词")
    assert entry is not None, "获取敏感词失败"
    assert entry.word == "测试词"
    assert entry.severity == SeverityLevel.WARNING
    assert entry.replacement == "示例词"
    print("[OK] 成功获取敏感词详情")
    
    # 测试更新敏感词
    print("\n[1.4] 测试更新敏感词...")
    success = service.update_word(
        word="测试词",
        severity=SeverityLevel.SERIOUS,
        replacement="更新后的替换词"
    )
    assert success, "更新敏感词失败"
    entry = service.get_word("测试词")
    assert entry.severity == SeverityLevel.SERIOUS
    assert entry.replacement == "更新后的替换词"
    print("[OK] 成功更新敏感词")
    
    # 测试列出敏感词
    print("\n[1.5] 测试列出敏感词...")
    words, total = service.list_words(page=1, page_size=10)
    assert total > 0, "词库应该包含敏感词"
    print("[OK] 成功列出敏感词，共 %d 个" % total)
    
    # 测试删除敏感词
    print("\n[1.6] 测试删除敏感词...")
    success = service.remove_word("测试词")
    assert success, "删除敏感词失败"
    entry = service.get_word("测试词")
    assert entry is None, "删除后不应该存在"
    print("[OK] 成功删除敏感词")
    
    cleanup_test_dir()
    print("\n[PASS] 测试 1 通过：词库管理功能正常")
    return True


def test_realtime_detection():
    """测试 2: 实时检测功能"""
    print("\n" + "="*60)
    print("测试 2: 实时检测功能")
    print("="*60)
    
    cleanup_test_dir()
    service = SensitiveWordService(data_dir="data/sensitive_words_test")
    
    # 添加测试词
    service.add_word("敏感词", SeverityLevel.WARNING, SensitiveWordCategory.GENERAL, "替代词")
    service.add_word("禁止词", SeverityLevel.BANNED, SensitiveWordCategory.GENERAL, None)
    
    # 测试基本检测
    print("\n[2.1] 测试基本文本检测...")
    text = "这是一个包含敏感词的测试文本"
    hits = service.detect(text)
    assert len(hits) > 0, "应该检测到敏感词"
    assert any(h["word"] == "敏感词" for h in hits), "应该检测到'敏感词'"
    print("[OK] 检测到 %d 个敏感词" % len(hits))
    
    # 测试实时检测模式
    print("\n[2.2] 测试实时检测模式...")
    result = service.detect_realtime(text)
    assert result["has_sensitive"] == True, "应该标记为包含敏感词"
    assert result["should_block"] == False, "警告级别不应该阻止"
    assert result["suggested_text"] is not None, "应该有替换建议"
    print("[OK] 实时检测结果正确")
    print("    建议文本：%s" % result["suggested_text"])
    
    # 测试封禁级别检测
    print("\n[2.3] 测试封禁级别检测...")
    banned_text = "这个文本包含禁止词"
    result = service.detect_realtime(banned_text)
    assert result["has_sensitive"] == True
    assert result["should_block"] == True, "封禁级别应该阻止"
    assert result["max_severity"] == "banned"
    print("[OK] 封禁检测正确，should_block=%s" % result["should_block"])
    
    cleanup_test_dir()
    print("\n[PASS] 测试 2 通过：实时检测功能正常")
    return True


def test_severity_levels():
    """测试 3: 敏感词分级预警"""
    print("\n" + "="*60)
    print("测试 3: 敏感词分级预警")
    print("="*60)
    
    cleanup_test_dir()
    service = SensitiveWordService(data_dir="data/sensitive_words_test")
    
    # 添加不同级别的词
    service.add_word("警告词", SeverityLevel.WARNING, SensitiveWordCategory.GENERAL, "建议词")
    service.add_word("严重词", SeverityLevel.SERIOUS, SensitiveWordCategory.GENERAL, "替换词")
    service.add_word("封禁词", SeverityLevel.BANNED, SensitiveWordCategory.GENERAL, None)
    
    # 测试各级别检测
    print("\n[3.1] 测试警告级别...")
    result = service.detect_realtime("包含警告词的文本")
    assert result["max_severity"] == "warning"
    assert result["should_block"] == False
    print("[OK] 警告级别正确")
    
    print("\n[3.2] 测试严重级别...")
    result = service.detect_realtime("包含严重词的文本")
    assert result["max_severity"] == "serious"
    assert result["should_block"] == False
    print("[OK] 严重级别正确")
    
    print("\n[3.3] 测试封禁级别...")
    result = service.detect_realtime("包含封禁词的文本")
    assert result["max_severity"] == "banned"
    assert result["should_block"] == True
    print("[OK] 封禁级别正确")
    
    print("\n[3.4] 测试混合级别...")
    result = service.detect_realtime("包含警告词和封禁词的文本")
    assert result["max_severity"] == "banned", "应该取最高级别"
    assert result["should_block"] == True
    print("[OK] 混合级别正确取最高")
    
    cleanup_test_dir()
    print("\n[PASS] 测试 3 通过：分级预警功能正常")
    return True


def test_replacement_suggestions():
    """测试 4: 敏感词替换建议"""
    print("\n" + "="*60)
    print("测试 4: 敏感词替换建议")
    print("="*60)
    
    cleanup_test_dir()
    service = SensitiveWordService(data_dir="data/sensitive_words_test")
    
    # 添加带替换建议的词
    service.add_word("最", SeverityLevel.WARNING, SensitiveWordCategory.ADVERTISING, "极")
    service.add_word("第一", SeverityLevel.WARNING, SensitiveWordCategory.ADVERTISING, "领先")
    service.add_word("顶级", SeverityLevel.WARNING, SensitiveWordCategory.ADVERTISING, "优质")
    
    # 测试替换
    print("\n[4.1] 测试单个词替换...")
    text = "这是最好的产品"
    result = service.detect_realtime(text)
    assert result["suggested_text"] == "这是极好的产品"
    print("[OK] 原文：%s" % text)
    print("    建议：%s" % result["suggested_text"])
    
    print("\n[4.2] 测试多个词替换...")
    text = "我们是第一的顶级品牌"
    result = service.detect_realtime(text)
    print("[OK] 原文：%s" % text)
    print("    建议：%s" % result["suggested_text"])
    assert "领先" in result["suggested_text"]
    assert "优质" in result["suggested_text"]
    
    cleanup_test_dir()
    print("\n[PASS] 测试 4 通过：替换建议功能正常")
    return True


def test_statistics():
    """测试 5: 使用统计功能"""
    print("\n" + "="*60)
    print("测试 5: 使用统计功能")
    print("="*60)
    
    cleanup_test_dir()
    service = SensitiveWordService(data_dir="data/sensitive_words_test")
    
    # 先添加测试词
    service.add_word("测试敏感词", SeverityLevel.WARNING, SensitiveWordCategory.GENERAL)
    
    # 执行多次检测
    print("\n[5.1] 执行多次检测...")
    for i in range(10):
        service.detect("包含测试敏感词的文本")
        service.detect("正常文本")
    
    stats = service.get_statistics()
    print("[OK] 词库大小：%d" % stats["library_size"])
    print("[OK] 总检测次数：%d" % stats["total_checks"])
    print("[OK] 总命中次数：%d" % stats["total_hits"])
    print("[OK] 命中率：%.2f%%" % (stats["hit_rate"] * 100))
    
    assert stats["total_checks"] >= 20, "检测次数应该累加"
    assert stats["total_hits"] > 0, "应该有命中记录"
    
    print("\n[5.2] 测试分类统计...")
    cat_stats = service.get_category_stats()
    print("[OK] 分类统计：%s" % cat_stats)
    
    cleanup_test_dir()
    print("\n[PASS] 测试 5 通过：使用统计功能正常")
    return True


def test_industry_packages():
    """测试 6: 行业敏感词包"""
    print("\n" + "="*60)
    print("测试 6: 行业敏感词包")
    print("="*60)
    
    cleanup_test_dir()
    service = SensitiveWordService(data_dir="data/sensitive_words_test")
    
    # 测试安装行业词包
    print("\n[6.1] 测试安装美妆行业词包...")
    beauty_words = [
        {"word": "美白祛斑", "severity": "serious", "replacement": "焕亮肌肤", "reason": "化妆品禁用医疗术语"},
        {"word": "抗衰老", "severity": "warning", "replacement": "紧致肌肤", "reason": "化妆品禁用医疗术语"},
    ]
    success = service.install_industry_package("beauty", beauty_words)
    assert success, "安装行业词包失败"
    print("[OK] 成功安装美妆行业词包")
    
    # 验证词已添加
    print("\n[6.2] 验证词包内容...")
    entry = service.get_word("美白祛斑")
    assert entry is not None, "词包中的词应该被添加"
    assert entry.category == SensitiveWordCategory.BEAUTY
    print("[OK] 词包内容验证通过")
    
    # 测试获取已安装包
    print("\n[6.3] 测试获取已安装包列表...")
    packages = service.get_industry_packages()
    assert len(packages) > 0, "应该有已安装的包"
    print("[OK] 已安装包：%d 个" % len(packages))
    
    # 测试检测行业词
    print("\n[6.4] 测试行业词检测...")
    text = "本产品具有美白祛斑功效"
    hits = service.detect(text)
    assert any(h["word"] == "美白祛斑" for h in hits), "应该检测到行业敏感词"
    print("[OK] 检测到行业敏感词")
    
    cleanup_test_dir()
    print("\n[PASS] 测试 6 通过：行业词包功能正常")
    return True


def run_all_tests():
    """运行所有测试"""
    print("\n" + "="*60)
    print(" LiveMirror 敏感词检测功能测试")
    print("="*60)
    
    tests = [
        ("词库管理", test_word_library_management),
        ("实时检测", test_realtime_detection),
        ("分级预警", test_severity_levels),
        ("替换建议", test_replacement_suggestions),
        ("使用统计", test_statistics),
        ("行业词包", test_industry_packages)
    ]
    
    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, True, None))
        except Exception as e:
            results.append((name, False, str(e)))
            print("\n[FAIL] 测试失败：%s" % name)
            print("错误：%s" % str(e))
    
    # 汇总结果
    print("\n" + "="*60)
    print("测试结果汇总")
    print("="*60)
    
    passed = sum(1 for _, success, _ in results if success)
    total = len(results)
    
    for name, success, error in results:
        status = "[PASS]" if success else "[FAIL]"
        print("%s - %s" % (status, name))
        if error:
            print("       错误：%s" % error)
    
    print("\n" + "-"*60)
    print("总计：%d/%d 测试通过" % (passed, total))
    
    if passed == total:
        print("\n[SUCCESS] 所有测试通过！敏感词检测系统功能正常！")
        return True
    else:
        print("\n[WARNING] 有 %d 个测试失败，请检查" % (total - passed))
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
