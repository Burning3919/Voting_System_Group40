from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
import json

from polls.models import Administrator


class TestApiAdminLogin(TestCase):
    """Test Administrator Login API"""

    def setUp(self):

        self.admin = Administrator.objects.create(
            admin_id=1,
            admin_psw="testpwd"
        )
        self.client = APIClient()
        self.url = reverse('polls:api_admin_login')

    def test_login_success(self):
        """Test the scenario of a successful administrator login"""
        data = {
            'username': '1',
            'password': 'testpwd'
        }
        response = self.client.post(self.url, data, format='json')

        # 验证响应状态码
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # 验证响应内容
        self.assertIn('token', response.data)
        self.assertIn('admin_id', response.data)
        self.assertIn('message', response.data)
        self.assertEqual(response.data['message'], 'login success')
        self.assertEqual(response.data['admin_id'], self.admin.admin_id)

    def test_login_wrong_password(self):
        """测试管理员登录密码错误的情况"""
        data = {
            'username': '1',
            'password': 'wrongpwd'
        }
        response = self.client.post(self.url, data, format='json')

        # 验证响应状态码
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        # 验证响应内容
        self.assertIn('error', response.data)
        self.assertEqual(response.data['error'], 'password error')

    def test_login_nonexistent_admin(self):
        """测试管理员不存在的情况"""
        data = {
            'username': '999',  # 不存在的管理员ID
            'password': 'testpwd'
        }
        response = self.client.post(self.url, data, format='json')

        # 验证响应状态码
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        # 验证响应内容
        self.assertIn('error', response.data)
        self.assertEqual(response.data['error'], 'admin not exist!')

    def test_login_missing_username(self):
        """测试缺少用户名的情况"""
        data = {
            'password': 'testpwd'
        }
        response = self.client.post(self.url, data, format='json')

        # 验证响应状态码
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # 验证响应内容
        self.assertIn('error', response.data)
        self.assertEqual(response.data['error'], 'please provide id and password')

    def test_login_missing_password(self):
        """测试缺少密码的情况"""
        data = {
            'username': '1'
        }
        response = self.client.post(self.url, data, format='json')

        # 验证响应状态码
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # 验证响应内容
        self.assertIn('error', response.data)
        self.assertEqual(response.data['error'], 'please provide id and password')


class TestApiAdminLogout(TestCase):
    """测试管理员登出API"""

    def setUp(self):
        self.client = APIClient()
        self.url = reverse('polls:api_admin_logout')

    def test_logout(self):
        """测试登出功能"""
        response = self.client.post(self.url)

        # 验证响应状态码
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # 验证响应内容
        self.assertIn('message', response.data)
        self.assertEqual(response.data['message'], 'Logout successful')


class TestApiAdminDashboard(TestCase):
    """测试管理员仪表盘API"""

    def setUp(self):
        # 创建测试用的管理员用户
        self.admin = Administrator.objects.create(
            admin_id=2,  # 使用不同的ID避免与其他测试冲突
            admin_psw="testpwd"
        )
        self.client = APIClient()
        self.url = reverse('polls:api_admin_dashboard')

    def test_dashboard_returns_polls(self):
        """测试仪表盘API返回所有投票"""
        # 直接调用仪表盘API（因为它设置了AllowAny权限）
        response = self.client.get(self.url)

        # 验证响应状态码
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # 验证响应是否为列表形式
        self.assertIsInstance(response.data, list)