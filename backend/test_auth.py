"""认证系统测试脚本"""
import requests
import sys

BASE_URL = "http://localhost:8001"


def test_register():
    """测试注册"""
    print("=" * 50)
    print("测试 1: 用户注册")
    print("=" * 50)
    
    response = requests.post(
        f"{BASE_URL}/auth/register",
        json={
            "username": "testuser2",
            "password": "password123",
            "email": "test2@example.com"
        }
    )
    
    if response.status_code == 201:
        print("[PASS] 注册成功")
        print(f"  响应：{response.json()}")
        return True
    elif response.status_code == 400:
        print(f"[PASS] 用户已存在（预期行为）: {response.json()['detail']}")
        return True
    else:
        print(f"[FAIL] 注册失败：{response.status_code} - {response.text}")
        return False


def test_login():
    """测试登录"""
    print("\n" + "=" * 50)
    print("测试 2: 用户登录")
    print("=" * 50)
    
    response = requests.post(
        f"{BASE_URL}/auth/login",
        data={
            "username": "testuser",
            "password": "password123"
        }
    )
    
    if response.status_code == 200:
        data = response.json()
        print("[PASS] 登录成功")
        print(f"  Access Token: {data['access_token'][:50]}...")
        print(f"  Refresh Token: {data['refresh_token'][:50]}...")
        print(f"  Token Type: {data['token_type']}")
        print(f"  Expires In: {data['expires_in']} 秒")
        return data['access_token']
    else:
        print(f"[FAIL] 登录失败：{response.status_code} - {response.text}")
        return None


def test_get_user_info(token):
    """测试获取用户信息"""
    print("\n" + "=" * 50)
    print("测试 3: 获取当前用户信息")
    print("=" * 50)
    
    response = requests.get(
        f"{BASE_URL}/auth/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    if response.status_code == 200:
        print("[PASS] 获取用户信息成功")
        print(f"  用户 ID: {response.json()['id']}")
        print(f"  用户名：{response.json()['username']}")
        print(f"  邮箱：{response.json()['email']}")
        return True
    else:
        print(f"[FAIL] 获取用户信息失败：{response.status_code} - {response.text}")
        return False


def test_invalid_token():
    """测试无效 Token"""
    print("\n" + "=" * 50)
    print("测试 4: 无效 Token 验证")
    print("=" * 50)
    
    response = requests.get(
        f"{BASE_URL}/auth/me",
        headers={"Authorization": "Bearer invalid_token"}
    )
    
    if response.status_code == 401:
        print("[PASS] 正确拒绝无效 Token")
        print(f"  响应：{response.json()['detail']}")
        return True
    else:
        print(f"[FAIL] Token 验证失败：{response.status_code}")
        return False


def test_wrong_password():
    """测试错误密码"""
    print("\n" + "=" * 50)
    print("测试 5: 错误密码登录")
    print("=" * 50)
    
    response = requests.post(
        f"{BASE_URL}/auth/login",
        data={
            "username": "testuser",
            "password": "wrong_password"
        }
    )
    
    if response.status_code == 401:
        print("[PASS] 正确拒绝错误密码")
        print(f"  响应：{response.json()['detail']}")
        return True
    else:
        print(f"[FAIL] 密码验证失败：{response.status_code}")
        return False


def main():
    """运行所有测试"""
    print("\n[TEST] LiveMirror 认证系统测试\n")
    
    results = []
    
    results.append(("注册", test_register()))
    
    token = test_login()
    if token:
        results.append(("登录", True))
    else:
        results.append(("登录", False))
        print("\n[FAIL] 登录失败，后续测试跳过")
        return 1
    
    results.append(("获取用户信息", test_get_user_info(token)))
    results.append(("无效 Token 验证", test_invalid_token()))
    results.append(("错误密码验证", test_wrong_password()))
    
    print("\n" + "=" * 50)
    print("测试结果汇总")
    print("=" * 50)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "[PASS]" if result else "[FAIL]"
        print(f"  {name}: {status}")
    
    print(f"\n总计：{passed}/{total} 测试通过")
    
    if passed == total:
        print("\n[SUCCESS] 所有测试通过！")
        return 0
    else:
        print(f"\n[FAILED] {total - passed} 个测试失败")
        return 1


if __name__ == "__main__":
    sys.exit(main())
