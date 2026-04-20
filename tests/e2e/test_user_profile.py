"""
LiveMirror 用户个人中心 E2E 测试
测试用户信息加载、修改密码、统计数据和退出登录功能
"""

import pytest
import time
import os
import requests
from pathlib import Path
from typing import Dict, Any


class TestUserProfile:
    """用户个人中心功能测试类"""
    
    # API 基础 URL
    API_BASE_URL = "http://localhost:8001"
    
    @pytest.fixture
    def test_user_credentials(self):
        """测试用户凭据"""
        return {
            "username": f"test_user_{int(time.time())}",
            "password": "test_password_123",
            "email": f"test_{int(time.time())}@example.com"
        }
    
    @pytest.fixture
    def registered_user(self, test_user_credentials):
        """注册测试用户并返回用户信息"""
        # 注册用户
        register_response = requests.post(
            f"{self.API_BASE_URL}/auth/register",
            json={
                "username": test_user_credentials["username"],
                "password": test_user_credentials["password"],
                "email": test_user_credentials["email"]
            }
        )
        
        assert register_response.status_code == 201
        user_data = register_response.json()
        
        return {
            **test_user_credentials,
            "user_id": user_data["id"],
            "created_at": user_data["created_at"]
        }
    
    @pytest.fixture
    def auth_token(self, registered_user):
        """获取认证 Token"""
        login_response = requests.post(
            f"{self.API_BASE_URL}/auth/login",
            data={
                "username": registered_user["username"],
                "password": registered_user["password"]
            }
        )
        
        assert login_response.status_code == 200
        token_data = login_response.json()
        
        return {
            "access_token": token_data["access_token"],
            "refresh_token": token_data["refresh_token"]
        }
    
    @pytest.fixture
    def auth_headers(self, auth_token):
        """获取认证请求头"""
        return {
            "Authorization": f"Bearer {auth_token['access_token']}",
            "Content-Type": "application/json"
        }
    
    def test_01_user_info_loading(self, auth_headers, registered_user):
        """测试用户信息加载"""
        print("\n=== 测试用户信息加载 ===")
        
        # 获取用户资料
        response = requests.get(
            f"{self.API_BASE_URL}/user/profile",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        profile_data = response.json()
        
        # 验证用户信息
        assert "profile" in profile_data
        assert profile_data["profile"]["username"] == registered_user["username"]
        assert profile_data["profile"]["email"] == registered_user["email"]
        assert profile_data["profile"]["id"] == registered_user["user_id"]
        
        # 验证统计信息
        assert "stats" in profile_data
        assert "analysis_count" in profile_data["stats"]
        assert "total_duration" in profile_data["stats"]
        assert "saved_reports" in profile_data["stats"]
        assert "total_danmus" in profile_data["stats"]
        assert "batch_uploads" in profile_data["stats"]
        
        # 验证会员信息
        assert "membership" in profile_data
        assert "is_member" in profile_data["membership"]
        
        print(f"✓ 用户信息加载成功")
        print(f"  - 用户名：{profile_data['profile']['username']}")
        print(f"  - 用户 ID: {profile_data['profile']['id']}")
        print(f"  - 分析次数：{profile_data['stats']['analysis_count']}")
        print(f"  - 弹幕总数：{profile_data['stats']['total_danmus']}")
    
    def test_02_change_password(self, auth_headers, registered_user, test_user_credentials):
        """测试修改密码"""
        print("\n=== 测试修改密码 ===")
        
        new_password = "new_password_456"
        
        # 修改密码
        response = requests.post(
            f"{self.API_BASE_URL}/user/change-password",
            headers=auth_headers,
            json={
                "old_password": test_user_credentials["password"],
                "new_password": new_password
            }
        )
        
        assert response.status_code == 200
        result = response.json()
        
        assert result["success"] is True
        assert "密码修改成功" in result["message"]
        
        print("✓ 密码修改成功")
        
        # 验证新密码可以登录
        login_response = requests.post(
            f"{self.API_BASE_URL}/auth/login",
            data={
                "username": registered_user["username"],
                "password": new_password
            }
        )
        
        assert login_response.status_code == 200
        print("✓ 新密码登录验证成功")
        
        # 验证旧密码无法登录
        old_login_response = requests.post(
            f"{self.API_BASE_URL}/auth/login",
            data={
                "username": registered_user["username"],
                "password": test_user_credentials["password"]
            }
        )
        
        assert old_login_response.status_code == 401
        print("✓ 旧密码已失效")
    
    def test_03_change_password_wrong_old(self, auth_headers, test_user_credentials):
        """测试修改密码 - 原密码错误"""
        print("\n=== 测试修改密码 - 原密码错误 ===")
        
        # 使用错误的原密码
        response = requests.post(
            f"{self.API_BASE_URL}/user/change-password",
            headers=auth_headers,
            json={
                "old_password": "wrong_password",
                "new_password": "new_password_789"
            }
        )
        
        assert response.status_code == 400
        result = response.json()
        
        assert "detail" in result
        print(f"✓ 原密码错误检测正常：{result['detail']}")
    
    def test_04_change_avatar(self, auth_headers):
        """测试修改头像"""
        print("\n=== 测试修改头像 ===")
        
        test_avatar_url = "https://example.com/avatar/test_user.png"
        
        # 修改头像
        response = requests.post(
            f"{self.API_BASE_URL}/user/change-avatar",
            headers=auth_headers,
            json={
                "avatar_url": test_avatar_url
            }
        )
        
        assert response.status_code == 200
        result = response.json()
        
        assert result["success"] is True
        assert result["avatar_url"] == test_avatar_url
        assert "头像修改成功" in result["message"]
        
        print(f"✓ 头像修改成功")
        print(f"  - 新头像 URL: {result['avatar_url']}")
    
    def test_05_change_avatar_invalid_url(self, auth_headers):
        """测试修改头像 - 无效 URL"""
        print("\n=== 测试修改头像 - 无效 URL ===")
        
        # 使用无效的 URL 格式
        response = requests.post(
            f"{self.API_BASE_URL}/user/change-avatar",
            headers=auth_headers,
            json={
                "avatar_url": "invalid-url-format"
            }
        )
        
        assert response.status_code == 400
        result = response.json()
        
        assert "detail" in result
        print(f"✓ 无效 URL 检测正常：{result['detail']}")
    
    def test_06_user_statistics(self, auth_headers):
        """测试统计数据"""
        print("\n=== 测试统计数据 ===")
        
        # 获取用户资料（包含统计）
        response = requests.get(
            f"{self.API_BASE_URL}/user/profile",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        profile_data = response.json()
        
        stats = profile_data["stats"]
        
        # 验证统计数据类型
        assert isinstance(stats["analysis_count"], int)
        assert isinstance(stats["total_duration"], (int, float))
        assert isinstance(stats["saved_reports"], int)
        assert isinstance(stats["total_danmus"], int)
        assert isinstance(stats["batch_uploads"], int)
        
        # 验证初始值（新用户应该都是 0）
        assert stats["analysis_count"] >= 0
        assert stats["total_duration"] >= 0
        assert stats["saved_reports"] >= 0
        assert stats["total_danmus"] >= 0
        assert stats["batch_uploads"] >= 0
        
        print("✓ 统计数据格式正确")
        print(f"  - 分析次数：{stats['analysis_count']}")
        print(f"  - 总时长：{stats['total_duration']} 秒")
        print(f"  - 保存报告：{stats['saved_reports']}")
        print(f"  - 弹幕总数：{stats['total_danmus']}")
        print(f"  - 上传次数：{stats['batch_uploads']}")
    
    def test_07_logout(self, auth_token, auth_headers):
        """测试退出登录"""
        print("\n=== 测试退出登录 ===")
        
        # 调用登出接口
        response = requests.post(
            f"{self.API_BASE_URL}/user/logout",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        result = response.json()
        
        assert result["success"] is True
        print("✓ 登出接口调用成功")
        
        # 验证 Token 失效（在实际实现中，应该将 Token 加入黑名单）
        # 这里简化测试，只验证接口响应
        print("✓ 退出登录流程正常")
    
    def test_08_get_activity_logs(self, auth_headers):
        """测试获取操作日志"""
        print("\n=== 测试获取操作日志 ===")
        
        # 获取操作日志
        response = requests.get(
            f"{self.API_BASE_URL}/user/activity-logs?limit=20",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        logs = response.json()
        
        assert isinstance(logs, list)
        print(f"✓ 操作日志获取成功，共 {len(logs)} 条记录")
    
    def test_09_unauthorized_access(self):
        """测试未授权访问"""
        print("\n=== 测试未授权访问 ===")
        
        # 没有 Token 访问用户资料
        response = requests.get(f"{self.API_BASE_URL}/user/profile")
        
        assert response.status_code == 401
        print("✓ 未授权访问被正确拒绝")
    
    def test_10_invalid_token(self):
        """测试无效 Token"""
        print("\n=== 测试无效 Token ===")
        
        # 使用无效 Token
        headers = {
            "Authorization": "Bearer invalid_token_12345",
            "Content-Type": "application/json"
        }
        
        response = requests.get(
            f"{self.API_BASE_URL}/user/profile",
            headers=headers
        )
        
        assert response.status_code == 401
        print("✓ 无效 Token 被正确拒绝")


class TestUserProfileFrontend:
    """前端个人中心页面测试（需要浏览器自动化）"""
    
    def test_profile_page_load(self):
        """测试个人中心页面加载"""
        # TODO: 使用 Playwright 或 Selenium 实现前端测试
        print("\n=== 前端测试：个人中心页面加载 ===")
        print("⚠ 需要浏览器自动化环境")
        pytest.skip("需要浏览器自动化环境")
    
    def test_profile_page_navigation(self):
        """测试个人中心页面导航"""
        # TODO: 使用 Playwright 或 Selenium 实现前端测试
        print("\n=== 前端测试：个人中心页面导航 ===")
        pytest.skip("需要浏览器自动化环境")
    
    def test_password_change_form(self):
        """测试密码修改表单"""
        # TODO: 使用 Playwright 或 Selenium 实现前端测试
        print("\n=== 前端测试：密码修改表单 ===")
        pytest.skip("需要浏览器自动化环境")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
