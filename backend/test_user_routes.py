"""
用户路由测试脚本
验证用户个人中心 API 功能
"""

import sys
import os

# 添加父目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database import engine, Base, get_db
from models import User
from routes.user import router
from routes.auth import create_access_token
from fastapi.testclient import TestClient
from fastapi import FastAPI

# 创建测试应用
app = FastAPI()
app.include_router(router)

# 创建测试数据库表
Base.metadata.create_all(bind=engine)

# 创建测试客户端
client = TestClient(app)


def test_user_routes_loaded():
    """测试用户路由模块加载"""
    print("[OK] 用户路由模块加载成功")
    return True


def test_create_test_user():
    """创建测试用户"""
    db = next(get_db())
    
    # 先删除已存在的测试用户（清理）
    db.query(User).filter(User.username == "test_profile_user").delete()
    db.commit()
    
    # 创建新用户
    hashed_password = User.hash_password("test_password_123")
    new_user = User(
        username="test_profile_user",
        email="test_profile_user@example.com",
        hashed_password=hashed_password
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    print(f"[OK] 测试用户创建成功 (ID: {new_user.id})")
    return new_user


def test_get_profile_with_token():
    """测试获取用户资料"""
    db = next(get_db())
    user = db.query(User).filter(User.username == "test_profile_user").first()
    
    if not user:
        print("[FAIL] 测试用户不存在")
        return False
    
    # 创建 Token
    token = create_access_token(data={"sub": user.username})
    
    # 测试 API
    response = client.get(
        "/user/profile",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    print(f"获取用户资料状态码：{response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"[OK] 用户资料获取成功")
        print(f"  - 用户名：{data['profile']['username']}")
        print(f"  - 分析次数：{data['stats']['analysis_count']}")
        print(f"  - 弹幕总数：{data['stats']['total_danmus']}")
        return True
    else:
        print(f"[FAIL] 获取用户资料失败：{response.text}")
        return False


def test_change_password():
    """测试修改密码"""
    db = next(get_db())
    user = db.query(User).filter(User.username == "test_profile_user").first()
    
    if not user:
        print("[FAIL] 测试用户不存在")
        return False
    
    # 创建 Token
    token = create_access_token(data={"sub": user.username})
    
    # 测试修改密码
    response = client.post(
        "/user/change-password",
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        },
        json={
            "old_password": "test_password_123",
            "new_password": "new_password_456"
        }
    )
    
    print(f"修改密码状态码：{response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"[OK] 密码修改成功：{data['message']}")
        
        # 刷新会话
        db.refresh(user)
        
        # 验证新密码
        user = db.query(User).filter(User.username == "test_profile_user").first()
        if user and user.verify_password("new_password_456"):
            print("[OK] 新密码验证成功")
            
            # 恢复原密码
            user.hashed_password = User.hash_password("test_password_123")
            db.commit()
            print("[OK] 密码已恢复")
            
            return True
        else:
            print("[FAIL] 新密码验证失败")
            return False
    else:
        print(f"[FAIL] 修改密码失败：{response.text}")
        return False


def test_change_avatar():
    """测试修改头像"""
    db = next(get_db())
    user = db.query(User).filter(User.username == "test_profile_user").first()
    
    if not user:
        print("[FAIL] 测试用户不存在")
        return False
    
    # 创建 Token
    token = create_access_token(data={"sub": user.username})
    
    # 测试修改头像
    test_avatar_url = "https://example.com/avatar/test.png"
    response = client.post(
        "/user/change-avatar",
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        },
        json={
            "avatar_url": test_avatar_url
        }
    )
    
    print(f"修改头像状态码：{response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"[OK] 头像修改成功：{data['message']}")
        print(f"  - 新头像 URL: {data['avatar_url']}")
        return True
    else:
        print(f"[FAIL] 修改头像失败：{response.text}")
        return False


def test_unauthorized_access():
    """测试未授权访问"""
    # 没有 Token 访问
    response = client.get("/user/profile")
    
    print(f"未授权访问状态码：{response.status_code}")
    
    if response.status_code == 401:
        print("[OK] 未授权访问被正确拒绝")
        return True
    else:
        print(f"[FAIL] 未授权访问检查失败")
        return False


def run_all_tests():
    """运行所有测试"""
    print("=" * 60)
    print("LiveMirror 用户个人中心 API 测试")
    print("=" * 60)
    print()
    
    tests = [
        ("模块加载", test_user_routes_loaded),
        ("创建测试用户", test_create_test_user),
        ("获取用户资料", test_get_profile_with_token),
        ("修改密码", test_change_password),
        ("修改头像", test_change_avatar),
        ("未授权访问", test_unauthorized_access),
    ]
    
    results = []
    for name, test_func in tests:
        print(f"\n测试：{name}")
        print("-" * 40)
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"[ERROR] 测试异常：{e}")
            results.append((name, False))
    
    print("\n" + "=" * 60)
    print("测试总结")
    print("=" * 60)
    
    passed = sum(1 for _, r in results if r)
    total = len(results)
    
    for name, result in results:
        status = "[PASS]" if result else "[FAIL]"
        print(f"  {status} - {name}")
    
    print(f"\n总计：{passed}/{total} 测试通过")
    
    return passed == total


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
